from io import BytesIO

import streamlit as st
from wordcloud import WordCloud

from tools import ai, data as data_tools, frequency, ui, workbench


st.set_page_config(
    page_title="Coconut",
    page_icon="🥥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ui.apply_app_style()
ui.render_tool_menu()
ui.render_page_header("WordCloud", "Create a quick visual summary of frequent words, terms, or values.")


with st.expander("Before you start", expanded=True):
    tab1, tab2, tab3, tab4 = st.tabs(["Prologue", "Steps", "Requirements", "Download Visualization"])
    with tab1:
        st.write(
            "A word cloud shows frequent items at a glance. Coconut now counts frequencies first, then draws the cloud "
            "from those counts, which makes larger files faster and lets numeric or categorical columns work cleanly."
        )
        st.divider()
        st.write("💡 The idea came from this:")
        st.write(
            "Mueller, A. (2012). A Wordcloud in Python. Peekaboo. Available at: "
            "https://peekaboo-vision.blogspot.com/2012/11/a-wordcloud-in-python.html."
        )
    with tab2:
        st.text("1. Upload a supported file.")
        st.text("2. Choose the column and count method.")
        st.text("3. Adjust the visual settings and optional words or values to remove.")
        st.text("4. Review the word cloud, frequency table, and optional AI insight.")
    with tab3:
        st.code(
            """
            +----------------+------------------------+----------------------------------+
            |     Source     |       File Type        |              Column              |
            +----------------+------------------------+----------------------------------+
            | Scopus         | Comma-separated values | Choose your preferred column     |
            |                | (.csv)                 |                                  |
            +----------------+------------------------+                                  |
            | Web of Science | Tab delimited file     |                                  |
            |                | (.txt)                 |                                  |
            +----------------+------------------------+                                  |
            | Lens.org       | Comma-separated values |                                  |
            |                | (.csv)                 |                                  |
            +----------------+------------------------+                                  |
            | Dimensions     | Comma-separated values |                                  |
            |                | (.csv)                 |                                  |
            +----------------+------------------------+                                  |
            | OpenAlex       | Comma-separated values |                                  |
            |                | (.csv)                 |                                  |
            +----------------+------------------------+                                  |
            | Other          | .csv .txt .json .xls .xlsx                                |
            +----------------+------------------------+----------------------------------+
            """,
            language=None,
        )
    with tab4:
        st.subheader(":blue[Visualization Download]", anchor=False)
        st.write("Use the download button below the visualization.")


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


@st.cache_data(ttl=3600, show_spinner=False)
def make_wordcloud_image(freq_frame, max_font, max_words, background, height, width, scale, colormap):
    freq_dict = frequency.frequency_dict(freq_frame)
    wordcloud = WordCloud(
        max_font_size=max_font,
        max_words=max_words,
        background_color=background,
        height=height,
        width=width,
        scale=scale,
        colormap=colormap,
        collocations=False,
    ).generate_from_frequencies(freq_dict)
    return wordcloud.to_image()


def image_png_bytes(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


papers, source_label, source_kind = workbench.render_data_intake(
    "WordCloud",
    accepted_types=["txt", "csv", "json", "xls", "xlsx"],
    help_text="Use sample data to learn the tool, or upload a file when you are ready.",
)

workbench.render_dataset_status(papers, source_label)

try:
        tab1, tab2, tab3 = st.tabs(["📈 Generate visualization", "📃 Reference", "⬇️ Download Help"])
        with tab1:
            controls_left, controls_right = st.columns(2)
            with controls_left:
                colcho = st.selectbox("Choose column", list(papers.columns))
                count_mode = st.selectbox("Count method", frequency.COUNT_MODES)
                max_words = st.number_input("Max items", min_value=1, max_value=2000, value=250, step=25)
                min_word_length = st.number_input("Minimum word length", min_value=1, max_value=20, value=2, step=1)
            with controls_right:
                max_font = st.number_input("Max font size", min_value=1, max_value=500, value=100, step=5)
                image_width = st.number_input("Image width", min_value=200, max_value=3000, value=900, step=50)
                image_height = st.number_input("Image height", min_value=200, max_value=3000, value=520, step=50)
                scale = st.number_input("Scale", min_value=1, max_value=5, value=2, step=1)

            style_col, remove_col = st.columns([0.7, 1.3])
            with style_col:
                background = st.selectbox("Background color", ["white", "black"])
                colormap = st.selectbox("Color palette", ["viridis", "plasma", "turbo", "cividis", "tab20"])
            with remove_col:
                blocked_words = st.text_input("Remove words or values. Separate items by semicolons (;)")

            with st.spinner("Counting frequencies..."):
                freq_frame, resolved_mode = build_frequency(
                    papers,
                    colcho,
                    count_mode,
                    int(max_words),
                    blocked_words,
                    int(min_word_length),
                )

            if freq_frame.empty:
                st.warning("No countable values were found after filtering.")
                st.stop()

            st.caption(f"Counting mode: {resolved_mode}")
            image = make_wordcloud_image(
                freq_frame,
                int(max_font),
                int(max_words),
                background,
                int(image_height),
                int(image_width),
                int(scale),
                colormap,
            )
            st.image(image, width="stretch")

            with st.expander("Top items", expanded=False):
                st.dataframe(freq_frame, width="stretch", hide_index=True)

            download_col, table_col = st.columns([1, 1])
            with download_col:
                st.download_button(
                    "Download PNG",
                    data=image_png_bytes(image),
                    file_name=f"{colcho}_wordcloud.png",
                    mime="image/png",
                    width="stretch",
                )
            with table_col:
                st.download_button(
                    "Download CSV",
                    data=data_tools.dataframe_csv(freq_frame),
                    file_name=f"{colcho}_frequency.csv",
                    mime="text/csv",
                    width="stretch",
                )

            payload = ai.frequency_payload("WordCloud", colcho, freq_frame)
            ai.render_ai_insights(
                "WordCloud",
                payload,
                f"wordcloud_{source_label}_{colcho}_{resolved_mode}",
                "Explain the dominant terms, likely themes, and any caveats in this word cloud.",
            )
            workbench.render_report_download(
                "WordCloud Analysis",
                source_label=source_label,
                sections={"Top items": workbench.table_text(freq_frame, limit=25)},
                settings={"Column": colcho, "Count mode": resolved_mode, "Max items": int(max_words)},
                key=f"wordcloud_report_{source_kind}_{colcho}_{resolved_mode}",
            )

        with tab2:
            st.write("Mueller, A. (2012). A Wordcloud in Python. Peekaboo.")

        with tab3:
            st.write("Use the PNG and CSV download buttons on the visualization tab.")

except Exception as exc:
    workbench.stop_with_error(
        "WordCloud could not build the visualization with the current settings.",
        exc,
    )
