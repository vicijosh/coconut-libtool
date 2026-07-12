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
ui.render_page_header("Ask Your Dataset", "Ask an AI question using a privacy-first dataset summary.")

frame, source_label, source_kind = workbench.render_data_intake(
    "Ask Your Dataset",
    help_text="Ask questions from a dataset profile first. Raw excerpts are optional and off by default.",
)

workbench.render_dataset_status(frame, source_label)
workbench.render_ai_guardrail()

st.dataframe(frame.head(50), width="stretch", hide_index=True)

text_cols = st.multiselect("Optional text columns for excerpts", data_tools.text_columns(frame), default=[])
include_excerpts = st.toggle("Include selected text excerpts in AI payload", value=False)
excerpt_count = st.slider("Excerpt count", 1, 20, 5, disabled=not include_excerpts)

payload = data_tools.profile_payload(frame)
payload["privacy"] = "Dataset profile only by default. Raw text excerpts are included only if explicitly enabled."
payload["source"] = source_label
if include_excerpts and text_cols:
    payload["selected_excerpts"] = data_tools.joined_text(frame, text_cols, limit=excerpt_count)

ai.render_ai_insights(
    "Ask Your Dataset",
    payload,
    f"ask_your_dataset_{source_kind}",
    "Answer my question using only the dataset profile and any selected excerpts I allowed.",
)
