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
ui.render_page_header("Histogram Visualization", "Compare frequent words, terms, years, sources, or categories.")


with st.expander("Before you start", expanded=True):
    tab1, tab2, tab3, tab4 = st.tabs(["Prologue", "Steps", "Requirements", "Download"])
    with tab1:
        st.write(
            "The histogram now uses Coconut's fast frequency engine instead of generating a hidden word cloud first. "
            "Text columns can be counted as words, keyword columns can be split into terms, and numeric or category columns "
            "can be counted as exact values."
        )
    with tab2:
        st.text("1. Upload a supported file.")
        st.text("2. Choose the column and count method.")
        st.text("3. Adjust the number of bars and optional words or values to remove.")
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
            | Web of Science | Tab delimited file     |                                      |
            |                | (.txt)                 |                                      |
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
        st.subheader(":blue[Histogram Download]", anchor=False)
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


def make_histogram(frame):
    chart_height = max(320, min(760, 24 * len(frame) + 80))
    return (
        alt.Chart(frame)
        .mark_bar(cornerRadiusEnd=5)
        .encode(
            x=alt.X("Frequency:Q", title="Frequency"),
            y=alt.Y("Word:N", title=None, sort="-x"),
            color=alt.Color(
                "Frequency:Q",
                legend=None,
                scale=alt.Scale(range=["#00c7be", "#007aff"]),
            ),
            tooltip=[
                alt.Tooltip("Word:N", title="Item"),
                alt.Tooltip("Frequency:Q", title="Frequency"),
            ],
        )
        .properties(height=chart_height)
    )


papers, source_label, source_kind = workbench.render_data_intake(
    "Histogram",
    accepted_types=["txt", "csv", "json", "xls", "xlsx"],
    help_text="Use sample data to see how exact values, keywords, and text words are counted.",
)

workbench.render_dataset_status(papers, source_label)

try:
        left, right = st.columns([1.1, 0.9])
        with left:
            colcho = st.selectbox("Choose column", list(papers.columns))
            count_mode = st.selectbox("Count method", frequency.COUNT_MODES)
        with right:
            max_items = st.number_input("Bars to show", min_value=1, max_value=500, value=30, step=5)
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
        chart = make_histogram(freq_frame)
        st.altair_chart(chart, width="stretch")

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

        payload = ai.frequency_payload("Histogram Visualization", colcho, freq_frame)
        ai.render_ai_insights(
            "Histogram Visualization",
            payload,
            f"histogram_{source_label}_{colcho}_{resolved_mode}",
            "Explain the strongest frequency patterns and what they may suggest.",
        )
        workbench.render_report_download(
            "Histogram Analysis",
            source_label=source_label,
            sections={"Frequency table": workbench.table_text(freq_frame, limit=50)},
            settings={"Column": colcho, "Count mode": resolved_mode, "Bars": int(max_items)},
            key=f"histogram_report_{source_kind}_{colcho}_{resolved_mode}",
        )

except Exception as exc:
    workbench.stop_with_error(
        "Histogram could not build the chart with the current settings.",
        exc,
    )
