import pandas as pd
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
    "Global Research Gap Radar",
    "Scan worldwide scholarly metadata for thin evidence, emerging topics, and repeated calls for more research.",
)

with st.expander("Before you start", expanded=True):
    tab1, tab2, tab3 = st.tabs(["What it does", "Steps", "Limits"])
    with tab1:
        st.write(
            "Global Research Gap Radar searches open scholarly metadata for a research area, then looks for signs "
            "that a topic may need more work: sparse publication coverage, recent-but-thin growth, and abstracts that "
            "explicitly call for more evidence."
        )
    with tab2:
        st.write("1. Enter a research area or seed the query from an uploaded corpus.")
        st.write("2. Choose a publication-year range and result size.")
        st.write("3. Run the search and review topic, country, year, and gap-signal tables.")
    with tab3:
        st.write(
            "This is an exploratory signal finder, not a definitive global systematic review. Open metadata coverage varies by field, language, publisher, and region."
        )


@st.cache_data(ttl=1800, show_spinner=False)
def search_gap_area(query, from_year, to_year, max_results, api_key, mailto):
    works = scholarly.openalex_search(
        query,
        from_year=from_year,
        to_year=to_year,
        per_page=max_results,
        api_key=api_key,
        mailto=mailto,
    )
    frame = scholarly.works_to_frame(works)
    gaps = scholarly.build_gap_signals(frame, from_year=from_year, to_year=to_year)
    return frame, gaps


mode = st.radio("Start with", ["A research question", "An uploaded corpus"], horizontal=True)

source_label = "manual query"
source_kind = "manual"
seed_query = ""

if mode == "An uploaded corpus":
    frame, source_label, source_kind = workbench.render_data_intake(
        "Global Research Gap Radar",
        help_text="Upload abstracts, titles, or keywords and Coconut will build a search profile.",
    )
    workbench.render_dataset_status(frame, source_label)
    text_cols = data_tools.text_columns(frame)
    if not text_cols:
        workbench.stop_with_error("Choose a file with at least one title, abstract, keyword, or text-like column.")
    selected_cols = st.multiselect("Columns to seed the global search", text_cols, default=text_cols[:2])
    if selected_cols:
        seed_terms = scholarly.extract_terms(data_tools.joined_text(frame, selected_cols, limit=300), max_terms=12)
        seed_query = " ".join(seed_terms[:8])

left, right = st.columns([1.15, 0.85])
with left:
    query = st.text_area(
        "Research area to scan",
        value=seed_query or "artificial intelligence library services evidence user experience",
        height=100,
        help="Use a focused research problem, not a full paragraph.",
    )
with right:
    from_year, to_year = st.slider("Publication years", 1900, 2026, (2016, 2026))
    max_results = st.slider("OpenAlex works to scan", 25, 100, 75, step=25)
    with st.expander("OpenAlex settings"):
        api_key = st.text_input("OpenAlex API key (optional)", type="password")
        mailto = st.text_input("Contact email for polite API usage (optional)")

if st.button("Scan Global Research Gaps", type="primary"):
    with st.spinner("Searching OpenAlex and scanning for gap signals..."):
        try:
            works_frame, gap_frame = search_gap_area(query, from_year, to_year, max_results, api_key, mailto)
        except Exception as exc:
            workbench.stop_with_error("Global Research Gap Radar could not search OpenAlex right now.", exc)

    if works_frame.empty:
        st.warning("No OpenAlex results were found. Try a broader research area.")
        st.stop()

    st.session_state["global_gap_works"] = works_frame
    st.session_state["global_gap_signals"] = gap_frame
    st.session_state["global_gap_query"] = query

works_frame = st.session_state.get("global_gap_works")
gap_frame = st.session_state.get("global_gap_signals")
query = st.session_state.get("global_gap_query", query)

if works_frame is None:
    st.info("Run the scan to build a global research gap profile.")
    st.stop()
    raise SystemExit

gap_mentions = works_frame["Abstract"].map(scholarly.future_research_signal).astype(bool).sum()
country_count = (
    works_frame["Countries"]
    .dropna()
    .astype(str)
    .str.split(";")
    .explode()
    .str.strip()
    .replace("", pd.NA)
    .dropna()
    .nunique()
)
metric_cols = st.columns(4)
metric_cols[0].metric("Works Scanned", f"{len(works_frame):,}")
metric_cols[1].metric("Gap-Language Papers", f"{gap_mentions:,}")
metric_cols[2].metric("Countries Observed", f"{country_count:,}")
metric_cols[3].metric("Open Access", f"{works_frame['Open access'].sum():,}")

year_counts = works_frame.dropna(subset=["Year"]).groupby("Year", as_index=False).size().rename(columns={"size": "Works"})
if not year_counts.empty:
    st.plotly_chart(px.line(year_counts, x="Year", y="Works", markers=True, title="Publication Activity Over Time"), width="stretch")

if gap_frame is not None and not gap_frame.empty:
    st.subheader("Topic Gap Signals", anchor=False)
    st.dataframe(gap_frame, width="stretch", hide_index=True)
    st.plotly_chart(
        px.scatter(
            gap_frame,
            x="Works found",
            y="Recent share",
            size="Gap-phrase mentions",
            color="Gap signal",
            hover_name="Topic",
            title="Sparse, Emerging, and Evidence-Seeking Topics",
        ),
        width="stretch",
    )
else:
    st.warning("OpenAlex did not return enough topic metadata to compute topic gap signals.")

country_rows = []
for countries in works_frame["Countries"].dropna().astype(str):
    for country in [part.strip() for part in countries.split(";") if part.strip()]:
        country_rows.append(country)
if country_rows:
    country_frame = pd.Series(country_rows).value_counts().reset_index()
    country_frame.columns = ["Country", "Works"]
    st.subheader("Observed Country Coverage", anchor=False)
    st.dataframe(country_frame.head(25), width="stretch", hide_index=True)

works_frame["Gap phrase"] = works_frame["Abstract"].map(scholarly.future_research_signal)
gap_papers = works_frame[works_frame["Gap phrase"].astype(bool)].copy()
with st.expander("Papers that explicitly request more evidence", expanded=not gap_papers.empty):
    if gap_papers.empty:
        st.write("No explicit future-research phrases were found in the retrieved abstracts.")
    else:
        st.dataframe(
            gap_papers[["Gap phrase", "Title", "Year", "Cited by", "Source", "URL"]],
            width="stretch",
            hide_index=True,
            column_config={"URL": st.column_config.LinkColumn("URL")},
        )

with st.expander("All scanned works"):
    st.dataframe(
        works_frame[["Title", "Year", "Cited by", "Type", "Source", "Topics", "Countries", "URL"]],
        width="stretch",
        hide_index=True,
        column_config={"URL": st.column_config.LinkColumn("URL")},
    )

st.download_button("Download scanned works CSV", data_tools.dataframe_csv(works_frame), "global_gap_scanned_works.csv", "text/csv")
if gap_frame is not None and not gap_frame.empty:
    st.download_button("Download gap signals CSV", data_tools.dataframe_csv(gap_frame), "global_research_gap_signals.csv", "text/csv")

payload = ai.table_payload(
    "Global Research Gap Radar",
    "Global research gap signals",
    gap_frame if gap_frame is not None else pd.DataFrame(),
    metadata={
        "research_area": query,
        "works_scanned": len(works_frame),
        "gap_language_papers": int(gap_mentions),
        "classification_note": "Gap signals are exploratory and depend on OpenAlex metadata coverage.",
    },
)
ai.render_ai_insights(
    "Global Research Gap Radar",
    payload,
    f"global_research_gap_{source_kind}",
    "Explain which topics look under-researched, emerging, or in need of more evidence. Include caveats about metadata coverage.",
)

workbench.render_report_download(
    "Global Research Gap Radar",
    source_label=source_label,
    sections={
        "Gap Signals": workbench.table_text(gap_frame if gap_frame is not None else pd.DataFrame()),
        "Scanned Works": workbench.table_text(works_frame[["Title", "Year", "Cited by", "Source"]].head(40)),
    },
    settings={"Research area": query, "Year range": f"{from_year}-{to_year}", "Works scanned": len(works_frame)},
    key=f"global_gap_report_{source_kind}",
)
