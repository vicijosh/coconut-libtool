import pandas as pd
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
ui.render_page_header("Named Entity Extraction", "Extract people, organizations, places, and dates from text fields.")

@st.cache_resource(show_spinner=False)
def load_nlp():
    import en_core_web_sm

    return en_core_web_sm.load()


def extract_entities(texts, labels, nlp, limit):
    rows = []
    for index, text in enumerate(texts[:limit], start=1):
        doc = nlp(text[:100000])
        for ent in doc.ents:
            if ent.label_ in labels:
                rows.append({"Entity": ent.text.strip(), "Type": ent.label_, "Record": index})
    return pd.DataFrame(rows)


frame, source_label, source_kind = workbench.render_data_intake(
    "Named Entity Extraction",
    help_text="Extract names, organizations, places, dates, and other entities from title, abstract, or text columns.",
)

workbench.render_dataset_status(frame, source_label)

text_options = data_tools.text_columns(frame)
if not text_options:
    workbench.stop_with_error("Named Entity Extraction needs at least one text-like column.")

text_cols = st.multiselect("Text columns", text_options, default=text_options[:1])
labels = st.multiselect(
    "Entity types",
    ["PERSON", "ORG", "GPE", "LOC", "DATE", "NORP", "FAC", "EVENT", "WORK_OF_ART", "LAW"],
    default=["PERSON", "ORG", "GPE", "LOC", "DATE"],
)
row_step = 1 if len(frame) < 50 else 50
row_limit = st.slider("Rows to scan", 1, min(5000, max(1, len(frame))), min(1000, max(1, len(frame))), step=row_step)

if st.button("Extract entities"):
    if not text_cols:
        st.warning("Choose at least one text column.")
        st.stop()
    try:
        nlp = load_nlp()
    except Exception as exc:
        workbench.stop_with_error(
            "The spaCy English model is not available. Install or repair en_core_web_sm to use this tool.",
            exc,
        )

    texts = data_tools.joined_text(frame, text_cols)
    entities = extract_entities(texts, labels, nlp, row_limit)
    if entities.empty:
        st.warning("No selected entities were found.")
        st.stop()

    counts = entities.groupby(["Entity", "Type"], as_index=False).size().rename(columns={"size": "Count"})
    counts = counts.sort_values("Count", ascending=False)
    st.dataframe(counts, width="stretch", hide_index=True)
    st.download_button("Download entities", data_tools.dataframe_csv(counts), "named_entities.csv", "text/csv")

    payload = ai.table_payload(
        "Named Entity Extraction",
        "Named entity counts",
        counts,
        metadata={"text_columns": text_cols, "entity_types": labels, "rows_scanned": row_limit},
    )
    ai.render_ai_insights(
        "Named Entity Extraction",
        payload,
        f"named_entity_extraction_{source_kind}",
        "Explain the dominant entities and what they may indicate about this corpus.",
    )
    workbench.render_report_download(
        "Named Entity Extraction",
        source_label=source_label,
        sections={"Entity Counts": workbench.table_text(counts, limit=75)},
        settings={"Text columns": ", ".join(text_cols), "Entity types": ", ".join(labels), "Rows scanned": row_limit},
        key=f"ner_report_{source_kind}",
    )
