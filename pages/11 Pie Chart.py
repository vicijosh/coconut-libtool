import altair as alt
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
ui.render_page_header("Pie Chart Visualization", "Show each frequent word, term, year, source, or category as a share.")


with st.expander("Before you start", expanded=True):
    tab1, tab2, tab3, tab4 = st.tabs(["Prologue", "Steps", "Requirements", "Download"])
    with tab1:
        st.write(
            "The pie chart uses Coconut's fast frequency engine, so it can count exact values such as years and citations "
            "without forcing them through a word-cloud workflow. Use fewer slices for a cleaner chart."
        )
    with tab2:
        st.text("1. Upload a supported file.")
        st.text("2. Choose the column and count method.")
        st.text("3. Keep the slice count focused for readability.")
        st.text("4. Review the chart, table, and optional AI insight.")
    with tab3:
        st.code(
            """
            +----------------+------------------------+--------------------------------------+
            |     Source     |       File Type        |     Column                           |
            +----------------+------------------------+--------------------------------------+
            | Scopus         | Comma-separated values | Source title,                        |
            |                | (.csv)                 | Document Type,                       |
            +----------------+------------------------| Cited by, Year                       |
            | Web of Science | Tab delimited file     | Abstract, Author Keywords,          |
            |                | (.txt)                 | Keywords Plus, Title, Year,         |
            |                |                        | Source title, Document Type          |
            +----------------+------------------------+--------------------------------------+
            | Lens.org       | Comma-separated values | Publication Year,                    |
            |                | (.csv)                 | Publication Type,                    |
            |                |                        | Source Title,                        |
            |                |                        | Citing Works Count                   |
            +----------------+------------------------+--------------------------------------+
            | OpenAlex       | Comma-separated values | publication_year,                    |
            |                | (.csv)                 | cited_by_count,                      |
            |                |                        | type,                                |
            |                |                        | primary_location.source.display_name |
            +----------------+------------------------+--------------------------------------+
            | Other          | .csv .txt .json .xls .xlsx                                  |
            +----------------+------------------------+--------------------------------------+
            """,
            language=None,
        )
    with tab4:
        st.subheader(":blue[Pie Chart Download]", anchor=False)
        st.write("Use the chart menu or the frequency table download button.")


@st.cache_data(ttl=3600, show_spinner=False)
def build_frequency(frame, column, count_mode, max_items, blocked_words, min_word_length):
    return frequency.frequency_frame(
        frame[column],
        column_name=column,
        mode=count_mode,
        max_items=max_items,
        extra_stopwords=blocked_words,
        min_word_length=min_word_length,
    )


def make_pie_chart(frame):
    return (
        alt.Chart(frame)
        .mark_arc(innerRadius=82, outerRadius=150, stroke="white", strokeWidth=1)
        .encode(
            theta=alt.Theta("Frequency:Q", title="Frequency"),
            color=alt.Color("Word:N", title=None, scale=alt.Scale(scheme="tableau20")),
            tooltip=[
                alt.Tooltip("Word:N", title="Item"),
                alt.Tooltip("Frequency:Q", title="Frequency"),
            ],
        )
        .properties(height=420)
    )


papers, source_label, source_kind = workbench.render_data_intake(
    "Pie Chart",
    accepted_types=["txt", "csv", "json", "xls", "xlsx"],
    help_text="Use sample data to compare readable slices before uploading your own file.",
)

workbench.render_dataset_status(papers, source_label)

try:
        left, right = st.columns([1.1, 0.9])
        with left:
            colcho = st.selectbox("Choose column", list(papers.columns))
            count_mode = st.selectbox("Count method", frequency.COUNT_MODES)
        with right:
            max_items = st.number_input("Slices to show", min_value=1, max_value=50, value=12, step=1)
            min_word_length = st.number_input("Minimum word length", min_value=1, max_value=20, value=2, step=1)

        blocked_words = st.text_input("Remove words or values. Separate items by semicolons (;)")

        with st.spinner("Counting frequencies..."):
            freq_frame, resolved_mode = build_frequency(
                papers,
                colcho,
                count_mode,
                int(max_items),
                blocked_words,
                int(min_word_length),
            )

        if freq_frame.empty:
            st.warning("No countable values were found after filtering.")
            st.stop()

        st.caption(f"Counting mode: {resolved_mode}")
        st.altair_chart(make_pie_chart(freq_frame), width="stretch")

        table_col, download_col = st.columns([3, 1])
        with table_col:
            with st.expander("Frequency table", expanded=True):
                st.dataframe(freq_frame, width="stretch", hide_index=True)
        with download_col:
            st.download_button(
                "Download CSV",
                data=data_tools.dataframe_csv(freq_frame),
                file_name=f"{colcho}_frequency.csv",
                mime="text/csv",
                width="stretch",
            )

        payload = ai.frequency_payload("Pie Chart Visualization", colcho, freq_frame)
        ai.render_ai_insights(
            "Pie Chart Visualization",
            payload,
            f"pie_chart_{source_label}_{colcho}_{resolved_mode}",
            "Explain the largest shares, any imbalance, and what to inspect next.",
        )
        workbench.render_report_download(
            "Pie Chart Analysis",
            source_label=source_label,
            sections={"Frequency table": workbench.table_text(freq_frame, limit=30)},
            settings={"Column": colcho, "Count mode": resolved_mode, "Slices": int(max_items)},
            key=f"pie_report_{source_kind}_{colcho}_{resolved_mode}",
        )

except Exception as exc:
    workbench.stop_with_error(
        "Pie Chart could not build the chart with the current settings.",
        exc,
    )
