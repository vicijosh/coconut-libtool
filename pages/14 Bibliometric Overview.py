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
ui.render_page_header("Bibliometric Overview", "Summarize publication years, sources, document types, citations, and keywords.")

frame, source_label, source_kind = workbench.render_data_intake(
    "Bibliometric Overview",
    help_text="Best for research-export files with years, sources, document types, keywords, and citation counts.",
)

workbench.render_dataset_status(frame, source_label)

year_col = data_tools.year_column(frame)
source_col = st.selectbox("Source column", frame.columns, index=frame.columns.get_loc("Source title") if "Source title" in frame.columns else 0)
doc_col = st.selectbox("Document type column", frame.columns, index=frame.columns.get_loc("Document Type") if "Document Type" in frame.columns else 0)
keyword_options = data_tools.keyword_columns(frame) or frame.columns.tolist()
keyword_col = st.selectbox("Keyword column", keyword_options)

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Tables", "AI", "Report"])

summary_payload = data_tools.profile_payload(frame)
with tab1:
    if year_col:
        years = frame.copy()
        by_year = years.assign(YearNum=pd.to_numeric(years[year_col], errors="coerce")).dropna(subset=["YearNum"])
        by_year = by_year["YearNum"].astype(int).value_counts().sort_index().reset_index()
        by_year.columns = ["Year", "Records"]
        st.plotly_chart(px.line(by_year, x="Year", y="Records", markers=True), width="stretch")
        summary_payload["publication_trend"] = by_year.to_dict("records")
    else:
        by_year = pd.DataFrame(columns=["Year", "Records"])
        st.info("No year-like column detected.")

    c1, c2 = st.columns(2)
    source_counts = frame[source_col].dropna().astype(str).value_counts().head(20).reset_index()
    source_counts.columns = ["Source", "Records"]
    c1.plotly_chart(px.bar(source_counts, x="Records", y="Source", orientation="h"), width="stretch")

    doc_counts = frame[doc_col].dropna().astype(str).value_counts().head(20).reset_index()
    doc_counts.columns = ["Document Type", "Records"]
    c2.plotly_chart(px.bar(doc_counts, x="Document Type", y="Records"), width="stretch")

with tab2:
    keywords = data_tools.split_keywords(frame[keyword_col]).str.lower().value_counts().head(50).reset_index()
    keywords.columns = ["Keyword", "Count"]
    st.dataframe(source_counts, width="stretch", hide_index=True)
    st.dataframe(doc_counts, width="stretch", hide_index=True)
    st.dataframe(keywords, width="stretch", hide_index=True)
    summary_payload["top_sources"] = source_counts.to_dict("records")
    summary_payload["document_types"] = doc_counts.to_dict("records")
    summary_payload["top_keywords"] = keywords.head(25).to_dict("records")

with tab3:
    ai.render_ai_insights(
        "Bibliometric Overview",
        summary_payload,
        f"bibliometric_overview_{source_kind}",
        "Explain the publication trend, leading sources, document types, and keyword signals.",
    )

with tab4:
    workbench.render_report_download(
        "Bibliometric Overview",
        source_label=source_label,
        sections={
            "Publication Trend": workbench.table_text(by_year),
            "Top Sources": workbench.table_text(source_counts),
            "Document Types": workbench.table_text(doc_counts),
            "Top Keywords": workbench.table_text(keywords, limit=25),
        },
        settings={"Source column": source_col, "Document type column": doc_col, "Keyword column": keyword_col},
        key=f"bibliometric_report_{source_kind}",
    )
