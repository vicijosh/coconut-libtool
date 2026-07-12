import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
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
ui.render_page_header("Semantic Search", "Search a corpus by meaning-oriented terms and ranked text similarity.")

@st.cache_data(ttl=3600, show_spinner=False)
def build_search_index(texts, ngram_max):
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, ngram_max), min_df=1)
    matrix = vectorizer.fit_transform(texts)
    return vectorizer, matrix


frame, source_label, source_kind = workbench.render_data_intake(
    "Semantic Search",
    help_text="Try the sample with queries like 'AI ethics', 'metadata discovery', or 'student privacy'.",
)

workbench.render_dataset_status(frame, source_label)

text_options = data_tools.text_columns(frame)
if not text_options:
    workbench.stop_with_error("Semantic Search needs at least one text-like column.")

text_cols = st.multiselect("Search columns", text_options, default=text_options[:1])
title_options = ["None"] + frame.columns.tolist()
title_index = title_options.index("Title") if "Title" in title_options else 0
title_col = st.selectbox("Title/display column", title_options, index=title_index)
query = st.text_input("Search query", value="AI ethics" if source_kind == "sample" else "")
top_k = st.slider("Results", 5, min(50, max(5, len(frame))), min(10, max(5, len(frame))))
ngram_max = st.select_slider("N-gram depth", options=[1, 2, 3], value=2)

if query and text_cols:
    texts = data_tools.joined_text(frame, text_cols)
    vectorizer, matrix = build_search_index(texts, ngram_max)
    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, matrix).ravel()
    order = scores.argsort()[::-1][:top_k]

    rows = []
    for rank, idx in enumerate(order, start=1):
        title = "" if title_col == "None" else str(frame.iloc[idx][title_col])
        snippet = texts[idx][:450]
        rows.append({"Rank": rank, "Score": round(float(scores[idx]), 4), "Title": title, "Snippet": snippet})
    results = pd.DataFrame(rows)
    st.dataframe(results, width="stretch", hide_index=True)
    st.download_button("Download search results", data_tools.dataframe_csv(results), "semantic_search_results.csv", "text/csv")

    include_snippets = st.toggle("Include result snippets in AI payload", value=False)
    ai_results = results.copy()
    if not include_snippets:
        ai_results = ai_results.drop(columns=["Snippet"])
    payload = ai.table_payload(
        "Semantic Search",
        "Ranked search results",
        ai_results,
        metadata={"query": query, "text_columns": text_cols, "result_count": int(top_k)},
    )
    ai.render_ai_insights(
        "Semantic Search",
        payload,
        f"semantic_search_{source_kind}",
        "Explain whether the search results look focused, what themes appear, and how to refine the query.",
    )
    workbench.render_report_download(
        "Semantic Search",
        source_label=source_label,
        sections={"Search Results": workbench.table_text(results)},
        settings={"Query": query, "Search columns": ", ".join(text_cols), "N-gram depth": ngram_max},
        key=f"semantic_report_{source_kind}_{query}",
    )
else:
    st.info("Enter a query to search the selected text columns.")
