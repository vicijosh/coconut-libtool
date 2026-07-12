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
ui.render_page_header("Data Cleaner", "Find duplicates, standardize common fields, and export a cleaner file.")

def clean_frame(frame, trim_text=True, normalize_blank=True, standardize_year=True, duplicate_subset=None):
    cleaned = frame.copy()
    object_cols = cleaned.select_dtypes(include=["object"]).columns
    if trim_text:
        for column in object_cols:
            cleaned[column] = cleaned[column].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
    if normalize_blank:
        cleaned.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA}, inplace=True)
    year_col = data_tools.year_column(cleaned)
    if standardize_year and year_col:
        cleaned[year_col] = pd.to_numeric(cleaned[year_col], errors="coerce").astype("Int64")
    before = len(cleaned)
    if duplicate_subset:
        cleaned = cleaned.drop_duplicates(subset=duplicate_subset, keep="first")
    return cleaned, before - len(cleaned)


frame, source_label, source_kind = workbench.render_data_intake(
    "Data Cleaner",
    help_text="Use this before analysis to reduce formatting noise, missing-value confusion, and duplicate rows.",
)

workbench.render_dataset_status(frame, source_label)

with st.expander("Cleaning settings", expanded=True):
    c1, c2, c3 = st.columns(3)
    trim_text = c1.toggle("Trim and normalize text spacing", value=True)
    normalize_blank = c2.toggle("Convert blank values to missing", value=True)
    standardize_year = c3.toggle("Standardize year column", value=True)
    subset = st.multiselect("Duplicate check columns", frame.columns.tolist(), default=[])

cleaned, dropped = clean_frame(
    frame,
    trim_text=trim_text,
    normalize_blank=normalize_blank,
    standardize_year=standardize_year,
    duplicate_subset=subset,
)

m1, m2, m3 = st.columns(3)
m1.metric("Original Rows", f"{len(frame):,}")
m2.metric("Cleaned Rows", f"{len(cleaned):,}")
m3.metric("Duplicates Removed", f"{dropped:,}")

tab1, tab2, tab3, tab4 = st.tabs(["Cleaned Data", "Audit", "AI", "Report"])
with tab1:
    st.dataframe(cleaned.head(200), width="stretch", hide_index=True)
    st.download_button(
        "Download cleaned CSV",
        data_tools.dataframe_csv(cleaned),
        "cleaned_data.csv",
        "text/csv",
    )

with tab2:
    audit = pd.DataFrame(
        {
            "Column": cleaned.columns,
            "Missing Before": frame.isna().sum().values,
            "Missing After": cleaned.isna().sum().reindex(cleaned.columns).fillna(0).astype(int).values,
            "Unique After": cleaned.nunique(dropna=True).values,
        }
    )
    st.dataframe(audit, width="stretch", hide_index=True)

with tab3:
    payload = data_tools.profile_payload(cleaned)
    payload["cleaning_actions"] = {
        "trim_text": trim_text,
        "normalize_blank": normalize_blank,
        "standardize_year": standardize_year,
        "duplicate_subset": subset,
        "duplicates_removed": dropped,
    }
    ai.render_ai_insights(
        "Data Cleaner",
        payload,
        f"data_cleaner_{source_kind}",
        "Explain the cleaning results, remaining data quality risks, and what to check before analysis.",
    )

with tab4:
    workbench.render_report_download(
        "Data Cleaning Audit",
        source_label=source_label,
        sections={"Audit": workbench.table_text(audit)},
        settings={
            "Trim text": trim_text,
            "Normalize blanks": normalize_blank,
            "Standardize year": standardize_year,
            "Duplicates removed": dropped,
        },
        key=f"cleaner_report_{source_kind}",
    )
