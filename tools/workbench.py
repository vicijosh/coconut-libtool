import datetime as dt
import html
import re

import pandas as pd
import streamlit as st

from tools import data as data_tools, samples, ui


DEFAULT_TYPES = ["csv", "txt", "json", "xls", "xlsx"]


@st.cache_data(ttl=3600, show_spinner=False)
def load_upload(name, raw):
    return data_tools.read_upload_bytes(name, raw)


def _safe_key(text):
    return re.sub(r"[^a-zA-Z0-9_]+", "_", str(text).lower()).strip("_")


def friendly_file_error(exc):
    message = str(exc)
    lower = message.lower()
    if "unsupported" in lower:
        return "This file type is not supported here. Try CSV, TXT, JSON, XLS, or XLSX."
    if "utf" in lower or "decode" in lower:
        return "Coconut could not read the text encoding. Try saving the file as UTF-8 CSV or TXT."
    if "excel" in lower or "openpyxl" in lower:
        return "Coconut could not read this spreadsheet. Try saving it as CSV, or check that the first sheet contains the data."
    if "no columns" in lower or "empty" in lower:
        return "The file opened, but Coconut could not find usable rows or columns."
    return "Coconut could not read this file. Check that it is exported as a clean CSV, TXT, JSON, XLS, or XLSX file."


def stop_with_error(message, details=None):
    st.error(message, icon="🚨")
    if details:
        with st.expander("Technical details"):
            st.code(str(details))
    st.stop()


def render_data_intake(
    tool_name,
    accepted_types=None,
    help_text=None,
    default_sample=None,
    show_download_sample=True,
):
    accepted_types = accepted_types or DEFAULT_TYPES
    default_sample = default_sample or samples.default_for_tool(tool_name)
    sample_names = samples.names()
    sample_index = sample_names.index(default_sample) if default_sample in sample_names else 0
    key = _safe_key(tool_name)

    with st.container(border=True):
        st.markdown("#### Start Here")
        if help_text:
            st.caption(help_text)

        start_mode = st.radio(
            "Choose a data source",
            ["Use sample data", "Upload my file"],
            horizontal=True,
            key=f"{key}_data_source",
        )

        if start_mode == "Use sample data":
            sample_name = st.selectbox("Sample dataset", sample_names, index=sample_index, key=f"{key}_sample")
            frame = samples.get(sample_name)
            st.success(f"Loaded {sample_name}: {len(frame):,} rows and {len(frame.columns):,} columns.")
            if show_download_sample:
                st.download_button(
                    "Download this sample CSV",
                    samples.csv_bytes(sample_name),
                    f"{_safe_key(sample_name)}.csv",
                    "text/csv",
                    key=f"{key}_download_sample",
                )
            return frame, sample_name, "sample"

        uploaded_file = st.file_uploader(
            "Upload file",
            type=accepted_types,
            key=f"{key}_upload",
        )
        if uploaded_file is None:
            st.info("Upload a file or switch to sample data to explore this tool.")
            st.stop()

        try:
            frame = load_upload(uploaded_file.name, uploaded_file.getvalue())
        except Exception as exc:
            stop_with_error(friendly_file_error(exc), exc)

        if frame.empty:
            stop_with_error("The file opened, but it does not contain any rows.")

        st.success(f"Loaded {uploaded_file.name}: {len(frame):,} rows and {len(frame.columns):,} columns.")
        return frame, uploaded_file.name, "upload"


def column_profile(frame):
    return pd.DataFrame(
        {
            "Column": frame.columns,
            "Type": [str(dtype) for dtype in frame.dtypes],
            "Missing": frame.isna().sum().values,
            "Unique": frame.nunique(dropna=True).values,
        }
    )


def recommend_tools(frame):
    recommendations = []
    year_col = data_tools.year_column(frame)
    text_cols = data_tools.text_columns(frame)
    keyword_cols = data_tools.keyword_columns(frame)
    numeric_cols = data_tools.numeric_columns(frame)

    recommendations.append(("Corpus Overview", "Profile rows, columns, missing values, and likely next steps.", "pages/12 Corpus Overview.py"))
    recommendations.append(("Data Cleaner", "Clean spacing, blank values, years, and duplicate records before analysis.", "pages/13 Data Cleaner.py"))

    if year_col:
        recommendations.append(("Term/Keyword Evolution", f"Use detected year column `{year_col}` to track selected terms over time.", "pages/17 Term Keyword Evolution.py"))
        recommendations.append(("Burst Detection", f"Use detected year column `{year_col}` to find sudden term spikes.", "pages/5 Burst Detection.py"))
    if keyword_cols:
        recommendations.append(("Keywords Stem", f"Normalize keyword-like column `{keyword_cols[0]}` before network mapping.", "pages/6 Keywords Stem.py"))
        recommendations.append(("Bidirected Network", f"Build keyword relationships from `{keyword_cols[0]}`.", "pages/3 Bidirected Network.py"))
    if text_cols:
        recommendations.append(("Semantic Search", f"Search meaningfully across `{text_cols[0]}` or other text fields.", "pages/16 Semantic Search.py"))
        recommendations.append(("Text Summarization", f"Summarize `{text_cols[0]}` or other text fields into key takeaways.", "pages/21 Text Summarization.py"))
        recommendations.append(("Topic Modeling", f"Discover themes in `{text_cols[0]}` or another text field.", "pages/2 Topic Modeling.py"))
        recommendations.append(("WordCloud", f"Quickly see frequent words or terms from `{text_cols[0]}`.", "pages/9 WordCloud.py"))
    if numeric_cols:
        recommendations.append(("Histogram", f"Compare numeric/category values such as `{numeric_cols[0]}`.", "pages/10 Histogram.py"))

    seen = set()
    unique = []
    for item in recommendations:
        if item[0] not in seen:
            unique.append(item)
            seen.add(item[0])
    return unique[:8]


def render_dataset_status(frame, source_label=None, expanded=False):
    year_col = data_tools.year_column(frame)
    text_cols = data_tools.text_columns(frame)
    keyword_cols = data_tools.keyword_columns(frame)
    numeric_cols = data_tools.numeric_columns(frame)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Rows", f"{len(frame):,}")
    m2.metric("Columns", f"{len(frame.columns):,}")
    m3.metric("Text Fields", f"{len(text_cols):,}")
    m4.metric("Numeric Fields", f"{len(numeric_cols):,}")

    with st.expander("Dataset health and recommendations", expanded=expanded):
        if source_label:
            st.caption(f"Source: {source_label}")
        detected = []
        if year_col:
            detected.append(f"Year column: `{year_col}`")
        if keyword_cols:
            detected.append(f"Keyword-like columns: `{', '.join(keyword_cols[:4])}`")
        if text_cols:
            detected.append(f"Text-like columns: `{', '.join(text_cols[:4])}`")
        if detected:
            st.markdown("  \n".join(detected))
        else:
            st.info("Coconut did not detect obvious year, keyword, or text columns. You can still choose columns manually.")

        st.dataframe(column_profile(frame), width="stretch", hide_index=True)
        st.markdown("#### Recommended next tools")
        for title, reason, page in recommend_tools(frame):
            st.page_link(page, label=title, help=reason, query_params=ui.theme_query_params())
            st.caption(reason)


def require_columns(frame, required=None, any_of=None, purpose="this tool"):
    missing = [column for column in (required or []) if column not in frame.columns]
    if missing:
        stop_with_error(
            f"{purpose} needs these missing columns: {', '.join(missing)}. "
            "Use Data Cleaner or rename columns in your file, then try again."
        )
    if any_of and not any(column in frame.columns for column in any_of):
        stop_with_error(
            f"{purpose} needs at least one of these columns: {', '.join(any_of)}. "
            "Use Corpus Overview to inspect your columns first."
        )


def markdown_report(title, source_label=None, sections=None, settings=None):
    sections = sections or {}
    settings = settings or {}
    date = dt.date.today().isoformat()
    lines = [f"# {title}", "", f"**Date:** {date}"]
    if source_label:
        lines.append(f"**Dataset:** {source_label}")
    if settings:
        lines.extend(["", "## Settings"])
        for key, value in settings.items():
            lines.append(f"- **{key}:** {value}")
    for heading, content in sections.items():
        lines.extend(["", f"## {heading}", str(content or "Not specified")])
    lines.extend(
        [
            "",
            "## Responsible Interpretation",
            "AI-assisted explanations should be treated as interpretive support, not proof. Confirm patterns with the underlying tables, charts, and domain expertise.",
        ]
    )
    return "\n".join(lines)


def table_text(frame, limit=None):
    table = frame.head(limit) if limit else frame
    try:
        return table.to_markdown(index=False)
    except Exception:
        return "```csv\n" + table.to_csv(index=False).strip() + "\n```"


def render_report_download(title, source_label=None, sections=None, settings=None, file_name=None, key=None):
    report = markdown_report(title, source_label=source_label, sections=sections, settings=settings)
    st.download_button(
        "Download analysis report",
        report,
        file_name or f"{_safe_key(title)}_report.md",
        "text/markdown",
        key=key or f"{_safe_key(title)}_report_download",
    )
    return report


def render_ai_guardrail():
    st.markdown(
        """
        <div class="coconut-ai-note">
            AI can help explain aggregate patterns, but it does not prove causation or replace domain judgment.
            Keep sensitive raw text out of prompts unless you intentionally enable excerpt sharing.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_workflow_card(title, body, page, icon):
    safe_title = html.escape(title)
    safe_body = html.escape(body)
    st.markdown(f"### {icon} {safe_title}")
    st.caption(safe_body)
    st.page_link(page, label=f"Open {title}", query_params=ui.theme_query_params())
