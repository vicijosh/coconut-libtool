import re
from collections import Counter

import pandas as pd
import streamlit as st

from tools import ai, data as data_tools, frequency, ui, workbench


st.set_page_config(
    page_title="Coconut",
    page_icon="🥥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ui.apply_app_style()
ui.render_tool_menu()
ui.render_page_header("Text Summarization", "Create concise summaries, key points, and AI-assisted takeaways from text.")


SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
TOKEN_RE = re.compile(r"\b[a-zA-Z][a-zA-Z\-']{2,}\b")
STOPWORDS = frequency.DEFAULT_STOPWORDS | {
    "abstract",
    "article",
    "chapter",
    "paper",
    "study",
    "research",
    "using",
    "based",
    "across",
}


def split_sentences(text):
    sentences = [sentence.strip() for sentence in SENTENCE_RE.split(str(text)) if sentence.strip()]
    if len(sentences) <= 1:
        sentences = [part.strip() for part in re.split(r"\n+|;\s+", str(text)) if part.strip()]
    return sentences


def tokenize(text):
    return [
        token.lower()
        for token in TOKEN_RE.findall(str(text))
        if token.lower() not in STOPWORDS
    ]


def extractive_summary(text, sentence_count=5, min_sentence_words=5):
    sentences = split_sentences(text)
    candidates = [
        (idx, sentence)
        for idx, sentence in enumerate(sentences)
        if len(tokenize(sentence)) >= min_sentence_words
    ]
    if not candidates:
        return " ".join(sentences[:sentence_count])

    word_counts = Counter(tokenize(text))
    if not word_counts:
        return " ".join(sentence for _, sentence in candidates[:sentence_count])

    scored = []
    for idx, sentence in candidates:
        terms = tokenize(sentence)
        if not terms:
            continue
        score = sum(word_counts[term] for term in terms) / max(len(terms), 1)
        scored.append((score, idx, sentence))

    selected = sorted(scored, key=lambda item: (-item[0], item[1]))[:sentence_count]
    selected = sorted(selected, key=lambda item: item[1])
    return " ".join(sentence for _, _, sentence in selected)


def key_points(text, point_count=6):
    sentences = split_sentences(text)
    summary = extractive_summary(text, sentence_count=point_count)
    selected = split_sentences(summary)
    if len(selected) < point_count:
        selected.extend(sentence for sentence in sentences if sentence not in selected)
    return selected[:point_count]


def joined_text_for_rows(frame, columns, row_limit):
    selected = frame[list(columns)].head(row_limit).fillna("").astype(str)
    if len(selected.columns) == 1:
        return selected.iloc[:, 0].str.strip()
    return selected.agg(" ".join, axis=1).str.replace(r"\s+", " ", regex=True).str.strip()


@st.cache_data(ttl=3600, show_spinner=False)
def summarize_rows(frame, text_columns, title_column, row_limit, sentence_count):
    texts = joined_text_for_rows(frame, text_columns, row_limit)
    rows = []
    for idx, text in texts.items():
        title = "" if title_column == "None" else str(frame.loc[idx, title_column])
        rows.append(
            {
                "Record": int(idx) + 1,
                "Title": title,
                "Summary": extractive_summary(text, sentence_count=sentence_count),
            }
        )
    return pd.DataFrame(rows)


frame, source_label, source_kind = workbench.render_data_intake(
    "Text Summarization",
    help_text="Use sample data or upload abstracts, articles, notes, survey responses, or other text-rich files.",
)

workbench.render_dataset_status(frame, source_label)
workbench.render_ai_guardrail()

text_options = data_tools.text_columns(frame)
if not text_options:
    workbench.stop_with_error("Text Summarization needs at least one text-like column.")

with st.expander("Summary settings", expanded=True):
    c1, c2 = st.columns(2)
    text_columns = c1.multiselect("Text columns", text_options, default=text_options[:1])
    title_options = ["None"] + frame.columns.tolist()
    title_index = title_options.index("Title") if "Title" in title_options else 0
    title_column = c2.selectbox("Title/display column", title_options, index=title_index)

    c3, c4, c5 = st.columns(3)
    summary_mode = c3.radio("Summary mode", ["Corpus summary", "Row-by-row summaries"], horizontal=False)
    sentence_count = c4.slider("Summary sentences", 2, 12, 5)
    row_limit = c5.slider("Rows to include", 1, min(500, max(1, len(frame))), min(50, max(1, len(frame))))

if not text_columns:
    st.warning("Choose at least one text column.")
    st.stop()

combined_texts = joined_text_for_rows(frame, text_columns, row_limit)
corpus_text = " ".join(text for text in combined_texts if text)
if not corpus_text.strip():
    st.warning("No usable text was found in the selected columns.")
    st.stop()

top_terms_frame, resolved_mode = frequency.frequency_frame(
    pd.Series([corpus_text]),
    column_name="Combined text",
    mode=frequency.MODE_WORDS,
    max_items=25,
    min_word_length=3,
)

tab1, tab2, tab3, tab4 = st.tabs(["Summary", "Key Points", "AI", "Report"])

with tab1:
    if summary_mode == "Corpus summary":
        summary_text = extractive_summary(corpus_text, sentence_count=sentence_count)
        st.markdown(summary_text)
        st.download_button(
            "Download summary",
            summary_text,
            "text_summary.md",
            "text/markdown",
        )
        summary_table = pd.DataFrame([{"Source": source_label, "Summary": summary_text}])
    else:
        summary_table = summarize_rows(frame, text_columns, title_column, row_limit, sentence_count)
        st.dataframe(summary_table, width="stretch", hide_index=True)
        st.download_button(
            "Download row summaries",
            data_tools.dataframe_csv(summary_table),
            "text_summaries.csv",
            "text/csv",
        )
        summary_text = "\n\n".join(summary_table["Summary"].head(10).tolist())

with tab2:
    points = key_points(corpus_text, point_count=sentence_count)
    for point in points:
        st.markdown(f"- {point}")
    st.subheader("Top Terms", anchor=False)
    st.dataframe(top_terms_frame, width="stretch", hide_index=True)

with tab3:
    include_source_excerpt = st.toggle("Include selected text excerpts in AI payload", value=False)
    payload = {
        "module": "Text Summarization",
        "source": source_label,
        "summary_mode": summary_mode,
        "text_columns": text_columns,
        "row_limit": int(row_limit),
        "extractive_summary": summary_text,
        "key_points": points,
        "top_terms": top_terms_frame.head(15).to_dict("records"),
        "privacy": "Raw text excerpts are excluded unless the user explicitly enables them.",
    }
    if include_source_excerpt:
        payload["source_excerpts"] = combined_texts.head(8).tolist()

    ai.render_ai_insights(
        "Text Summarization",
        payload,
        f"text_summarization_{source_kind}_{summary_mode}",
        "Turn this extractive summary into a concise, accurate, plain-language summary with key takeaways and caveats.",
    )

with tab4:
    workbench.render_report_download(
        "Text Summarization",
        source_label=source_label,
        sections={
            "Summary": summary_text,
            "Key Points": "\n".join(f"- {point}" for point in points),
            "Top Terms": workbench.table_text(top_terms_frame, limit=25),
        },
        settings={
            "Summary mode": summary_mode,
            "Text columns": ", ".join(text_columns),
            "Rows included": row_limit,
            "Summary sentences": sentence_count,
        },
        key=f"text_summary_report_{source_kind}_{summary_mode}",
    )
