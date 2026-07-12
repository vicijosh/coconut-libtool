import re

import pandas as pd
import plotly.express as px
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
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
ui.render_page_header("Term/Keyword Evolution", "Track how selected terms, keywords, and phrases rise or fade across years.")

def tokenize(text):
    return [
        token for token in re.findall(r"\b[a-zA-Z][a-zA-Z\-]{2,}\b", str(text).lower())
        if token not in ENGLISH_STOP_WORDS
    ]


frame, source_label, source_kind = workbench.render_data_intake(
    "Term/Keyword Evolution",
    help_text="Track terms over time when your dataset has a year column and keyword or text column.",
)

workbench.render_dataset_status(frame, source_label)

year_col = data_tools.year_column(frame)
if not year_col:
    workbench.stop_with_error("Term/Keyword Evolution needs a year-like column. Use Data Cleaner to standardize a year column first.")

text_options = data_tools.text_columns(frame)
if not text_options:
    workbench.stop_with_error("Term/Keyword Evolution needs at least one keyword or text column.")

text_col = st.selectbox("Column to track", text_options)
mode = st.radio("Term source", ["Split keywords/phrases", "Tokenize text"], horizontal=True)
top_n = st.slider("Top terms", 5, 40, 15)

working = frame[[year_col, text_col]].dropna().copy()
working[year_col] = pd.to_numeric(working[year_col], errors="coerce")
working = working.dropna(subset=[year_col])
working[year_col] = working[year_col].astype(int)
working["_record_id"] = range(len(working))

if mode == "Split keywords/phrases":
    term_frame = working.assign(Term=working[text_col].astype(str).str.split(r";|,|\|", regex=True)).explode("Term")
    term_frame["Term"] = term_frame["Term"].astype(str).str.strip().str.lower()
else:
    term_frame = working.assign(Term=working[text_col].map(tokenize)).explode("Term")
    term_frame["Term"] = term_frame["Term"].astype(str).str.strip()

term_frame = term_frame[term_frame["Term"].notna()]
term_frame = term_frame[~term_frame["Term"].str.lower().isin(["", "nan", "none"])]
term_frame = term_frame.drop_duplicates(subset=["_record_id", "Term"])
selected_terms = term_frame["Term"].value_counts().head(top_n).index.tolist()
evolution = (
    term_frame[term_frame["Term"].isin(selected_terms)]
    .groupby([year_col, "Term"], as_index=False)
    .size()
    .rename(columns={year_col: "Year", "size": "Records"})
)

if evolution.empty:
    st.warning("No terms found.")
    st.stop()

st.plotly_chart(px.line(evolution, x="Year", y="Records", color="Term", markers=True), width="stretch")
heat = evolution.pivot_table(index="Term", columns="Year", values="Records", fill_value=0)
st.plotly_chart(px.imshow(heat, aspect="auto", color_continuous_scale="Blues"), width="stretch")
st.dataframe(evolution.sort_values(["Term", "Year"]), width="stretch", hide_index=True)
st.download_button("Download evolution table", data_tools.dataframe_csv(evolution), "term_keyword_evolution.csv", "text/csv")

payload = ai.table_payload(
    "Term/Keyword Evolution",
    "Term counts by year",
    evolution.sort_values(["Records"], ascending=False),
    metadata={"year_column": year_col, "tracked_column": text_col, "term_source": mode, "top_terms": selected_terms},
)
ai.render_ai_insights(
    "Term/Keyword Evolution",
    payload,
    f"term_keyword_evolution_{source_kind}",
    "Explain which terms are rising, fading, or stable over time.",
)
workbench.render_report_download(
    "Term/Keyword Evolution",
    source_label=source_label,
    sections={"Term Counts by Year": workbench.table_text(evolution.sort_values(["Term", "Year"]))},
    settings={"Year column": year_col, "Tracked column": text_col, "Term source": mode, "Top terms": top_n},
    key=f"term_keyword_evolution_report_{source_kind}",
)
