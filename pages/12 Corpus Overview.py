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
ui.render_page_header("Corpus Overview", "Profile an uploaded dataset before choosing an analysis path.")

frame, source_label, source_kind = workbench.render_data_intake(
    "Corpus Overview",
    help_text="Start here when you are not sure what is inside your file or which tool to use next.",
)

workbench.render_dataset_status(frame, source_label, expanded=True)

year_col = data_tools.year_column(frame)
text_cols = data_tools.text_columns(frame)
numeric_cols = data_tools.numeric_columns(frame)
keyword_cols = data_tools.keyword_columns(frame)

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Columns", "AI", "Report"])

with tab1:
    st.dataframe(frame.head(100), width="stretch", hide_index=True)

    col1, col2 = st.columns(2)
    missing = frame.isna().sum().reset_index()
    missing.columns = ["Column", "Missing values"]
    missing = missing[missing["Missing values"] > 0].sort_values("Missing values", ascending=False)
    if not missing.empty:
        col1.plotly_chart(
            px.bar(missing.head(20), x="Missing values", y="Column", orientation="h"),
            width="stretch",
        )
    else:
        col1.success("No missing values detected.")

    if year_col:
        years = pd.to_numeric(frame[year_col], errors="coerce").dropna().astype(int)
        if not years.empty:
            by_year = years.value_counts().sort_index().reset_index()
            by_year.columns = ["Year", "Records"]
            col2.plotly_chart(px.line(by_year, x="Year", y="Records", markers=True), width="stretch")
    else:
        col2.info("No year-like column detected.")

with tab2:
    profile = workbench.column_profile(frame)
    st.dataframe(profile, width="stretch", hide_index=True)
    selected_col = st.selectbox("Inspect values", frame.columns)
    values = frame[selected_col].dropna().astype(str).value_counts().head(30).reset_index()
    values.columns = [selected_col, "Count"]
    st.dataframe(values, width="stretch", hide_index=True)

with tab3:
    payload = data_tools.profile_payload(frame)
    if year_col:
        payload["year_column"] = year_col
    if keyword_cols:
        top_keywords = data_tools.split_keywords(frame[keyword_cols[0]]).str.lower().value_counts().head(20)
        payload["top_keywords"] = top_keywords.to_dict()
    ai.render_ai_insights(
        "Corpus Overview",
        payload,
        f"corpus_overview_{source_kind}",
        "Explain the dataset structure, likely quality issues, and which Coconut tools fit this file.",
    )

with tab4:
    sections = {
        "Dataset Profile": workbench.table_text(workbench.column_profile(frame)),
        "Recommended Tools": "\n".join(f"- {title}: {reason}" for title, reason, _ in workbench.recommend_tools(frame)),
    }
    workbench.render_report_download(
        "Corpus Overview",
        source_label=source_label,
        sections=sections,
        settings={"Rows": len(frame), "Columns": len(frame.columns)},
        key=f"corpus_report_{source_kind}",
    )
