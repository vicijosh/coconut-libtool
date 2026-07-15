import math
import re

import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.feature_extraction.text import CountVectorizer, ENGLISH_STOP_WORDS

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
    "Keyness Corpus Compare",
    "Compare two text groups and find the words or phrases that distinguish each side.",
)

with st.expander("Before you start", expanded=True):
    tab1, tab2, tab3 = st.tabs(["What it does", "Steps", "Limits"])
    with tab1:
        st.write(
            "Keyness compares two corpora and highlights terms that are unusually common in one group compared with another. "
            "It is useful for comparing years, publication types, sources, departments, authors, survey groups, or any labeled text collection."
        )
    with tab2:
        st.write("1. Upload text data or use the sample data.")
        st.write("2. Choose the text column and define two groups by category or year range.")
        st.write("3. Review distinctive terms, normalized rates, and download the keyness table.")
    with tab3:
        st.write(
            "This tool uses word and phrase counts with smoothed log-ratio scoring. It identifies strong language signals, "
            "but it does not prove causation or importance without interpretation and source review."
        )


def compact_label(value, limit=42):
    text = str(value)
    return text if len(text) <= limit else text[:limit - 3] + "..."


def grouping_columns(frame, text_col):
    max_unique = max(2, min(80, len(frame) // 2 if len(frame) > 4 else len(frame)))
    candidates = []
    for column in frame.columns:
        if column == text_col:
            continue
        unique_count = frame[column].nunique(dropna=True)
        if 2 <= unique_count <= max_unique:
            candidates.append(column)
    return candidates


def custom_stopword_tuple(text):
    terms = re.split(r"[,;\n]+", text or "")
    custom = {term.strip().lower() for term in terms if term.strip()}
    return tuple(sorted(set(ENGLISH_STOP_WORDS).union(custom)))


@st.cache_data(ttl=3600, show_spinner=False)
def compute_keyness(texts_a, texts_b, label_a, label_b, ngram_max, min_total_count, stopwords):
    texts_a = [str(text or "") for text in texts_a]
    texts_b = [str(text or "") for text in texts_b]
    docs = texts_a + texts_b
    if not any(doc.strip() for doc in docs):
        return pd.DataFrame(), {"terms_a": 0, "terms_b": 0, "docs_a": len(texts_a), "docs_b": len(texts_b)}

    vectorizer = CountVectorizer(
        lowercase=True,
        stop_words=list(stopwords),
        ngram_range=(1, ngram_max),
        min_df=1,
        token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z-]{2,}\b",
    )
    try:
        matrix = vectorizer.fit_transform(docs)
    except ValueError:
        return pd.DataFrame(), {"terms_a": 0, "terms_b": 0, "docs_a": len(texts_a), "docs_b": len(texts_b)}

    vocab = vectorizer.get_feature_names_out()
    split_at = len(texts_a)
    counts_a = matrix[:split_at].sum(axis=0).A1
    counts_b = matrix[split_at:].sum(axis=0).A1
    total_a = int(counts_a.sum())
    total_b = int(counts_b.sum())
    vocab_size = max(len(vocab), 1)

    rows = []
    for term, count_a, count_b in zip(vocab, counts_a, counts_b):
        count_a = int(count_a)
        count_b = int(count_b)
        combined = count_a + count_b
        if combined < min_total_count:
            continue

        rate_a = (count_a / total_a * 10000) if total_a else 0
        rate_b = (count_b / total_b * 10000) if total_b else 0
        smoothed_a = (count_a + 0.5) / (total_a + 0.5 * vocab_size) if total_a else 0
        smoothed_b = (count_b + 0.5) / (total_b + 0.5 * vocab_size) if total_b else 0
        log_ratio = math.log2(smoothed_a / smoothed_b) if smoothed_a and smoothed_b else 0
        direction = f"More common in {compact_label(label_a)}" if log_ratio >= 0 else f"More common in {compact_label(label_b)}"
        reliability = "Stronger" if combined >= 20 else "Moderate" if combined >= 8 else "Exploratory"
        rows.append(
            {
                "Term": term,
                f"{compact_label(label_a)} count": count_a,
                f"{compact_label(label_b)} count": count_b,
                f"{compact_label(label_a)} rate per 10k": round(rate_a, 2),
                f"{compact_label(label_b)} rate per 10k": round(rate_b, 2),
                "Combined count": combined,
                "Log2 keyness": round(float(log_ratio), 3),
                "Absolute keyness": round(abs(float(log_ratio)), 3),
                "Direction": direction,
                "Signal strength": reliability,
            }
        )

    result = pd.DataFrame(rows)
    if not result.empty:
        result = result.sort_values(["Absolute keyness", "Combined count"], ascending=[False, False]).reset_index(drop=True)
    stats = {"terms_a": total_a, "terms_b": total_b, "docs_a": len(texts_a), "docs_b": len(texts_b)}
    return result, stats


frame, source_label, source_kind = workbench.render_data_intake(
    "Keyness Corpus Compare",
    help_text="Upload a corpus with a text column and a grouping column, or compare two year ranges.",
)
workbench.render_dataset_status(frame, source_label)

text_options = data_tools.text_columns(frame)
if not text_options:
    workbench.stop_with_error("Keyness Corpus Compare needs at least one text-like column.")

year_col = data_tools.year_column(frame)
left, right = st.columns([1.05, 0.95])
with left:
    text_col = st.selectbox("Text column", text_options)
    available_group_cols = grouping_columns(frame, text_col)
    mode_options = []
    if available_group_cols:
        mode_options.append("Compare categories")
    if year_col:
        mode_options.append("Compare year ranges")
    if not mode_options:
        workbench.stop_with_error("This page needs either a category column with at least two values or a year column for comparison.")
    compare_mode = st.radio("Comparison type", mode_options, horizontal=True)

with right:
    ngram_max = st.select_slider("Term length", options=[1, 2, 3], value=2, help="Use 2 or 3 to include short phrases.")
    top_n = st.slider("Terms to display", 10, 100, 30, step=10)
    min_total_count = st.slider("Minimum combined count", 1, 25, 3)
    custom_stopwords_text = st.text_area("Extra stopwords", value="", height=80, help="Optional words to ignore, separated by commas or new lines.")

if compare_mode == "Compare categories":
    group_col = st.selectbox("Group/category column", available_group_cols)
    values = frame[group_col].dropna().astype(str).value_counts().index.tolist()
    if len(values) < 2:
        workbench.stop_with_error("Choose a grouping column with at least two non-empty values.")
    group_cols = st.columns(2)
    with group_cols[0]:
        label_a = st.selectbox("Group A", values, index=0)
    with group_cols[1]:
        second_index = 1 if len(values) > 1 else 0
        label_b = st.selectbox("Group B", values, index=second_index)
    if label_a == label_b:
        st.warning("Choose two different groups.")
        st.stop()
    group_values = frame[group_col].astype(str)
    frame_a = frame[group_values == label_a]
    frame_b = frame[group_values == label_b]
    comparison_label = f"{group_col}: {label_a} vs {label_b}"
else:
    numeric_years = pd.to_numeric(frame[year_col], errors="coerce")
    valid_years = numeric_years.dropna().astype(int)
    if valid_years.empty:
        workbench.stop_with_error("The detected year column does not contain usable years.")
    min_year = int(valid_years.min())
    max_year = int(valid_years.max())
    midpoint = int(valid_years.median())
    range_cols = st.columns(2)
    with range_cols[0]:
        range_a = st.slider("Group A year range", min_year, max_year, (min_year, midpoint), key="keyness_year_a")
    with range_cols[1]:
        default_b_start = min(max_year, midpoint + 1)
        range_b = st.slider("Group B year range", min_year, max_year, (default_b_start, max_year), key="keyness_year_b")
    label_a = f"{range_a[0]}-{range_a[1]}"
    label_b = f"{range_b[0]}-{range_b[1]}"
    frame_a = frame[numeric_years.between(range_a[0], range_a[1], inclusive="both")]
    frame_b = frame[numeric_years.between(range_b[0], range_b[1], inclusive="both")]
    comparison_label = f"{year_col}: {label_a} vs {label_b}"

if frame_a.empty or frame_b.empty:
    workbench.stop_with_error("One of the comparison groups has no rows. Adjust the groups or year ranges.")

texts_a = tuple(data_tools.joined_text(frame_a, [text_col]))
texts_b = tuple(data_tools.joined_text(frame_b, [text_col]))
stopwords = custom_stopword_tuple(custom_stopwords_text)
results, stats = compute_keyness(texts_a, texts_b, label_a, label_b, ngram_max, min_total_count, stopwords)

if results.empty:
    st.warning("No usable terms were found after stopword filtering. Lower the minimum count or choose a richer text column.")
    st.stop()

metric_cols = st.columns(4)
metric_cols[0].metric(compact_label(label_a), f"{stats['docs_a']:,} records")
metric_cols[1].metric(compact_label(label_b), f"{stats['docs_b']:,} records")
metric_cols[2].metric("Terms in Group A", f"{stats['terms_a']:,}")
metric_cols[3].metric("Terms in Group B", f"{stats['terms_b']:,}")

chart_frame = results.head(top_n).sort_values("Log2 keyness")
st.plotly_chart(
    px.bar(
        chart_frame,
        x="Log2 keyness",
        y="Term",
        color="Direction",
        orientation="h",
        title="Distinctive Terms by Corpus",
    ),
    width="stretch",
)

with st.expander("Keyness table", expanded=True):
    st.dataframe(results.head(max(top_n, 100)), width="stretch", hide_index=True)

st.download_button(
    "Download keyness table CSV",
    data_tools.dataframe_csv(results),
    "keyness_corpus_compare.csv",
    "text/csv",
)

payload = ai.table_payload(
    "Keyness Corpus Compare",
    "Keyness terms",
    results.head(60),
    metadata={
        "source_dataset": source_label,
        "comparison": comparison_label,
        "text_column": text_col,
        "term_length": ngram_max,
        "scoring": "Smoothed log2 ratio with normalized rates per 10,000 terms.",
    },
)
ai.render_ai_insights(
    "Keyness Corpus Compare",
    payload,
    f"keyness_compare_{source_kind}",
    "Explain the most distinctive terms on each side, likely themes, caveats, and what examples to inspect next.",
)

workbench.render_report_download(
    "Keyness Corpus Compare",
    source_label=source_label,
    sections={"Keyness Terms": workbench.table_text(results.head(60))},
    settings={
        "Comparison": comparison_label,
        "Text column": text_col,
        "Term length": ngram_max,
        "Minimum combined count": min_total_count,
    },
    key=f"keyness_report_{source_kind}",
)
