import re

import pandas as pd
import plotly.express as px
import streamlit as st

from tools import ai, data as data_tools, ui, workbench


st.set_page_config(
    page_title="Coconut",
    page_icon="🥥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ui.apply_app_style()
ui.render_tool_menu()
ui.render_page_header(
    "Words in Context",
    "Search words or phrases and inspect the sentences around each match.",
)

with st.expander("Before you start", expanded=True):
    tab1, tab2, tab3 = st.tabs(["What it does", "Steps", "Limits"])
    with tab1:
        st.write(
            "Words in Context is a concordance-style tool. It finds a word, phrase, or pattern in your corpus "
            "and shows the surrounding sentences so you can judge meaning, tone, and usage instead of only counts."
        )
    with tab2:
        st.write("1. Upload text, abstracts, notes, survey responses, or use the sample data.")
        st.write("2. Choose the text columns and enter one or more search terms.")
        st.write("3. Review matched sentences, nearby context, and frequency summaries.")
    with tab3:
        st.write(
            "Sentence splitting is lightweight and may be imperfect for abbreviations, OCR text, or unusual punctuation. "
            "For AI insights, raw context snippets are excluded unless you explicitly include them."
        )


SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")
TERM_SPLIT_RE = re.compile(r"[;\n]+")


def split_terms(search_text):
    return [term.strip() for term in TERM_SPLIT_RE.split(search_text or "") if term.strip()]


def normalize_space(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()


def split_sentences(text):
    cleaned = normalize_space(text)
    if not cleaned:
        return []
    sentences = [part.strip() for part in SENTENCE_SPLIT_RE.split(cleaned) if part.strip()]
    return sentences or [cleaned]


def build_pattern(terms, regex_mode, case_sensitive):
    flags = 0 if case_sensitive else re.IGNORECASE
    if regex_mode:
        pattern_text = "|".join(f"(?:{term})" for term in terms)
    else:
        pattern_text = "|".join(re.escape(term) for term in terms)
    return pattern_text, int(flags), re.compile(pattern_text, flags)


def match_label(match_text, terms, case_sensitive, regex_mode):
    if regex_mode:
        return match_text
    if case_sensitive:
        for term in terms:
            if term == match_text:
                return term
    lowered = match_text.lower()
    for term in terms:
        if term.lower() == lowered:
            return term
    return match_text


@st.cache_data(ttl=3600, show_spinner=False)
def context_matches(
    frame,
    text_cols,
    metadata_cols,
    terms,
    pattern_text,
    flags,
    regex_mode,
    case_sensitive,
    sentence_window,
    max_matches,
):
    pattern = re.compile(pattern_text, flags)
    rows = []
    selected_cols = list(text_cols)
    selected_meta = [column for column in metadata_cols if column in frame.columns]

    for record_number, (_idx, row) in enumerate(frame.iterrows(), start=1):
        text = normalize_space(" ".join(str(row.get(column, "")) for column in selected_cols))
        sentences = split_sentences(text)
        if not sentences:
            continue

        for sentence_index, sentence in enumerate(sentences):
            match = pattern.search(sentence)
            if not match:
                continue

            before = sentences[max(0, sentence_index - sentence_window):sentence_index]
            after = sentences[sentence_index + 1:sentence_index + 1 + sentence_window]
            context_parts = before + [sentence] + after
            record = {
                "Record": record_number,
                "Match": match_label(match.group(0), terms, case_sensitive, regex_mode),
                "Matched sentence": sentence,
                "Context before": " ".join(before),
                "Context after": " ".join(after),
                "Full context": " ".join(context_parts),
            }
            for column in selected_meta:
                record[column] = row.get(column, "")
            rows.append(record)
            if len(rows) >= max_matches:
                return pd.DataFrame(rows)

    return pd.DataFrame(rows)


frame, source_label, source_kind = workbench.render_data_intake(
    "Words in Context",
    help_text="Upload text-rich data and search for terms in their surrounding sentence context.",
)
workbench.render_dataset_status(frame, source_label)

text_options = data_tools.text_columns(frame)
if not text_options:
    workbench.stop_with_error("Words in Context needs at least one text-like column.")

default_query = "library" if source_kind == "sample" else ""
left, right = st.columns([1.1, 0.9])
with left:
    text_cols = st.multiselect("Text columns to search", text_options, default=text_options[:1])
    search_text = st.text_area(
        "Search words or phrases",
        value=default_query,
        height=90,
        help="Use semicolons or new lines to search more than one term. Example: privacy; student data",
    )
    metadata_defaults = [column for column in ["Title", data_tools.year_column(frame), "Source title"] if column in frame.columns]
    metadata_cols = st.multiselect("Optional columns to show with each match", frame.columns.tolist(), default=metadata_defaults[:3])

with right:
    sentence_window = st.slider("Sentences before/after", 0, 4, 1)
    max_matches = st.slider("Maximum matches to collect", 25, 500, 100, step=25)
    case_sensitive = st.toggle("Case-sensitive search", value=False)
    regex_mode = st.toggle("Use regular expressions", value=False, help="Advanced: interpret each search line as a regex pattern.")

terms = split_terms(search_text)
if not text_cols:
    st.warning("Choose at least one text column.")
    st.stop()

if not terms:
    st.info("Enter a word or phrase to inspect it in context.")
    st.stop()

try:
    pattern_text, flags, _pattern = build_pattern(terms, regex_mode, case_sensitive)
except re.error as exc:
    workbench.stop_with_error("The regular expression could not be read. Turn off regex mode or simplify the pattern.", exc)

results = context_matches(
    frame,
    tuple(text_cols),
    tuple(metadata_cols),
    tuple(terms),
    pattern_text,
    flags,
    regex_mode,
    case_sensitive,
    sentence_window,
    max_matches,
)

if results.empty:
    st.warning("No matches were found. Try a broader term, fewer punctuation marks, or another text column.")
    st.stop()

matched_records = results["Record"].nunique()
metric_cols = st.columns(4)
metric_cols[0].metric("Matches", f"{len(results):,}")
metric_cols[1].metric("Records Matched", f"{matched_records:,}")
metric_cols[2].metric("Search Terms", f"{len(terms):,}")
metric_cols[3].metric("Context Window", f"{sentence_window} sentence(s)")

match_counts = results["Match"].astype(str).str.lower().value_counts().reset_index()
match_counts.columns = ["Match", "Count"]
if not match_counts.empty:
    st.plotly_chart(
        px.bar(match_counts.head(20), x="Count", y="Match", orientation="h", title="Most Frequent Matched Terms"),
        width="stretch",
    )

with st.expander("Context table", expanded=True):
    st.dataframe(results, width="stretch", hide_index=True)

st.download_button(
    "Download context matches CSV",
    data_tools.dataframe_csv(results),
    "words_in_context_matches.csv",
    "text/csv",
)

include_context = st.toggle("Include context snippets in AI payload", value=False)
if include_context:
    ai_frame = results.head(40)
else:
    ai_frame = match_counts.head(40)

payload = ai.table_payload(
    "Words in Context",
    "Context search results" if include_context else "Aggregate match counts",
    ai_frame,
    metadata={
        "source_dataset": source_label,
        "search_terms": terms,
        "text_columns": text_cols,
        "context_snippets_included": include_context,
    },
)
ai.render_ai_insights(
    "Words in Context",
    payload,
    f"words_in_context_{source_kind}",
    "Explain how the searched terms are being used, what meanings or patterns stand out, and what to verify next.",
)

workbench.render_report_download(
    "Words in Context",
    source_label=source_label,
    sections={"Match Counts": workbench.table_text(match_counts), "Context Matches": workbench.table_text(results.head(40))},
    settings={
        "Search terms": "; ".join(terms),
        "Text columns": ", ".join(text_cols),
        "Context window": sentence_window,
        "Regex mode": regex_mode,
    },
    key=f"words_context_report_{source_kind}",
)
