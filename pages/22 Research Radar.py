import plotly.express as px
import streamlit as st

from tools import ai, data as data_tools, scholarly, ui, workbench


st.set_page_config(
    page_title="Coconut",
    page_icon="🥥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ui.apply_app_style()
ui.render_tool_menu()
ui.render_page_header(
    "Research Radar",
    "Find related papers, possible solutions, evidence syntheses, and calls for more evidence from open scholarly metadata.",
)

with st.expander("Before you start", expanded=True):
    tab1, tab2, tab3 = st.tabs(["What it does", "Steps", "Limits"])
    with tab1:
        st.write(
            "Research Radar starts from your uploaded abstracts or titles, creates a search profile, "
            "then searches OpenAlex for related scholarly works. Coconut groups results into practical "
            "research categories such as directly related, possible solution or method, evidence synthesis, "
            "and requests for more evidence."
        )
    with tab2:
        st.write("1. Upload a bibliography, abstract list, or use the sample data.")
        st.write("2. Choose the title/abstract/text columns that describe your topic.")
        st.write("3. Review or edit the generated search query.")
        st.write("4. Search OpenAlex and inspect the evidence relationship table.")
    with tab3:
        st.write(
            "This tool uses open scholarly metadata and heuristic classification. It does not prove that a problem is solved. "
            "Use the linked papers, abstracts, and domain expertise to verify each result."
        )


@st.cache_data(ttl=1800, show_spinner=False)
def search_openalex(query, from_year, to_year, max_results, api_key, mailto):
    works = scholarly.openalex_search(
        query,
        from_year=from_year,
        to_year=to_year,
        per_page=max_results,
        api_key=api_key,
        mailto=mailto,
    )
    frame = scholarly.works_to_frame(works)
    return scholarly.classify_research_radar(frame, query)


frame, source_label, source_kind = workbench.render_data_intake(
    "Research Radar",
    help_text="Upload titles, abstracts, or bibliographic metadata. Coconut will search open scholarly metadata for related work.",
)
workbench.render_dataset_status(frame, source_label)

text_cols = data_tools.text_columns(frame)
if not text_cols:
    workbench.stop_with_error("Research Radar needs at least one title, abstract, keyword, or text-like column.")

year_col = data_tools.year_column(frame)
default_cols = text_cols[:2]

controls_left, controls_right = st.columns([1.1, 0.9])
with controls_left:
    selected_cols = st.multiselect("Columns that describe the research problem", text_cols, default=default_cols)
    if not selected_cols:
        st.warning("Choose at least one text column.")
        st.stop()
    seed_terms = scholarly.extract_terms(data_tools.joined_text(frame, selected_cols, limit=250), max_terms=12)
    generated_query = " ".join(seed_terms[:8])
    query = st.text_area(
        "Search profile",
        value=generated_query,
        height=100,
        help="You can edit this. A focused phrase usually works better than a very long abstract.",
    )

with controls_right:
    max_results = st.slider("OpenAlex results to review", 10, 100, 40, step=10)
    if year_col:
        years = frame[year_col].dropna()
        years = years[years.astype(str).str.match(r"^\d{4}$", na=False)]
        if not years.empty:
            inferred_min = int(years.astype(int).min())
            inferred_max = int(years.astype(int).max())
        else:
            inferred_min, inferred_max = 2010, 2026
    else:
        inferred_min, inferred_max = 2010, 2026
    from_year, to_year = st.slider("Publication years to search", 1900, 2026, (max(1900, inferred_min - 3), 2026))
    with st.expander("OpenAlex settings"):
        api_key = st.text_input("OpenAlex API key (optional)", type="password")
        mailto = st.text_input("Contact email for polite API usage (optional)")

if st.button("Search Open Scholarly Metadata", type="primary"):
    with st.spinner("Searching OpenAlex and classifying evidence relationships..."):
        try:
            results = search_openalex(query, from_year, to_year, max_results, api_key, mailto)
        except Exception as exc:
            workbench.stop_with_error("Research Radar could not search OpenAlex right now.", exc)

    if results.empty:
        st.warning("No OpenAlex results were found. Try a broader search profile.")
        st.stop()

    st.session_state["research_radar_results"] = results
    st.session_state["research_radar_query"] = query

results = st.session_state.get("research_radar_results")
query = st.session_state.get("research_radar_query", query)

if results is None:
    st.info("Run the search to build a research radar table.")
    st.stop()
    raise SystemExit

metric_cols = st.columns(4)
metric_cols[0].metric("Works Found", f"{len(results):,}")
metric_cols[1].metric("Possible Solutions", f"{(results['Evidence relationship'] == 'Possible solution or method').sum():,}")
metric_cols[2].metric("Evidence Syntheses", f"{(results['Evidence relationship'] == 'Evidence synthesis').sum():,}")
metric_cols[3].metric("Calls for Evidence", f"{(results['Evidence relationship'] == 'Requests more evidence').sum():,}")

st.plotly_chart(
    px.histogram(
        results,
        x="Evidence relationship",
        color="Evidence relationship",
        title="Evidence Relationship Categories",
    ),
    width="stretch",
)

display_cols = [
    "Radar score",
    "Evidence relationship",
    "Title",
    "Year",
    "Cited by",
    "Type",
    "Source",
    "Topics",
    "URL",
]
with st.expander("Research radar table", expanded=True):
    st.dataframe(
        results[display_cols],
        width="stretch",
        hide_index=True,
        column_config={"URL": st.column_config.LinkColumn("URL")},
    )

with st.expander("Abstract snippets for verification"):
    for _idx, row in results.head(12).iterrows():
        st.markdown(f"**{row.get('Title')}**")
        st.caption(f"{row.get('Evidence relationship')} | {row.get('Year')} | cited by {row.get('Cited by')}")
        abstract = row.get("Abstract", "")
        st.write((abstract[:900] + "...") if len(abstract) > 900 else abstract or "No abstract available in OpenAlex metadata.")
        st.divider()

st.download_button(
    "Download research radar CSV",
    data_tools.dataframe_csv(results),
    "research_radar.csv",
    "text/csv",
)

payload = ai.table_payload(
    "Research Radar",
    "Open scholarly metadata results",
    results[display_cols + ["Abstract"]].head(40),
    metadata={
        "source_dataset": source_label,
        "search_profile": query,
        "classification_note": "Evidence relationship categories are heuristic and should be verified against the linked papers.",
    },
)
ai.render_ai_insights(
    "Research Radar",
    payload,
    f"research_radar_{source_kind}",
    "Explain the strongest related papers, possible solutions, evidence syntheses, and research gaps. Be careful and cite uncertainty.",
)

workbench.render_report_download(
    "Research Radar",
    source_label=source_label,
    sections={"Research Radar Results": workbench.table_text(results[display_cols].head(40))},
    settings={"Search profile": query, "Year range": f"{from_year}-{to_year}", "Results reviewed": len(results)},
    key=f"research_radar_report_{source_kind}",
)
