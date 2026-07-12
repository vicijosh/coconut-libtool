import datetime as dt

import streamlit as st

from tools import ai, data as data_tools, samples, ui, workbench


st.set_page_config(
    page_title="Coconut",
    page_icon="🥥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ui.apply_app_style()
ui.render_tool_menu()
ui.render_page_header("AI Report Builder", "Turn analysis notes and aggregate results into a polished research report.")


def report_markdown(title, author, objective, methods, findings, caveats):
    today = dt.date.today().isoformat()
    return f"""# {title}

**Author:** {author or "Not specified"}  
**Date:** {today}

## Objective
{objective or "Not specified"}

## Methods
{methods or "Not specified"}

## Key Findings
{findings or "Not specified"}

## Caveats
{caveats or "Not specified"}

## Recommended Next Steps
- Review the underlying data quality and missing values.
- Confirm AI-assisted interpretations with domain expertise.
- Export final charts and tables from the relevant Coconut Libtool tools.
"""


frame_payload = {}
with st.expander("Optional dataset context", expanded=False):
    context_mode = st.radio("Dataset context", ["No dataset", "Use sample data", "Upload a file"], horizontal=True)
    if context_mode == "Use sample data":
        sample_name = st.selectbox("Sample dataset", samples.names())
        frame = samples.get(sample_name)
        st.dataframe(frame.head(25), width="stretch", hide_index=True)
        frame_payload = data_tools.profile_payload(frame)
        frame_payload["source"] = sample_name
    elif context_mode == "Upload a file":
        uploaded_file = st.file_uploader(
            "Optional dataset for report context",
            type=["csv", "txt", "json", "xls", "xlsx"],
        )
        if uploaded_file is not None:
            try:
                frame = workbench.load_upload(uploaded_file.name, uploaded_file.getvalue())
                st.dataframe(frame.head(25), width="stretch", hide_index=True)
                frame_payload = data_tools.profile_payload(frame)
                frame_payload["source"] = uploaded_file.name
            except Exception as exc:
                st.warning(workbench.friendly_file_error(exc))
                with st.expander("Technical details"):
                    st.code(str(exc))

title = st.text_input("Report title", value="Coconut Libtool Analysis Report")
author = st.text_input("Author")
objective = st.text_area("Research objective")
methods = st.text_area("Methods and tools used")
findings = st.text_area("Paste key findings or AI insights")
caveats = st.text_area("Caveats and limitations")

draft = report_markdown(title, author, objective, methods, findings, caveats)
st.markdown(draft)
st.download_button("Download Markdown report", draft, "coconut_report.md", "text/markdown")
workbench.render_ai_guardrail()

payload = {
    "module": "AI Report Builder",
    "privacy": "User-entered report notes and optional aggregate dataset profile.",
    "report_title": title,
    "objective": objective,
    "methods": methods,
    "findings": findings,
    "caveats": caveats,
    "dataset_profile": frame_payload,
}
ai.render_ai_insights(
    "AI Report Builder",
    payload,
    "ai_report_builder",
    "Rewrite this into a concise professional report with clear sections and careful caveats.",
)
