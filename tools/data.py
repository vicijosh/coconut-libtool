from io import BytesIO, StringIO
import json
import re

import pandas as pd

from tools import sourceformat as sf


STANDARD_COLUMN_ALIASES = {
    "Publication Year": "Year",
    "publication_year": "Year",
    "PubYear": "Year",
    "Source Title": "Source title",
    "primary_location.source.display_name": "Source title",
    "Publication Type": "Document Type",
    "type": "Document Type",
    "Citing Works Count": "Cited by",
    "cited_by_count": "Cited by",
    "Times cited": "Cited by",
    "abstract": "Abstract",
    "title": "Title",
    "keywords.display_name": "Keywords",
    "MeSH terms": "Keywords",
}

WOS_COLUMN_ALIASES = {
    "PT": "Record Type",
    "AU": "Authors",
    "AF": "Author Full Names",
    "TI": "Title",
    "SO": "Source title",
    "LA": "Language",
    "DT": "Document Type",
    "DE": "Author Keywords",
    "ID": "Keywords Plus",
    "AB": "Abstract",
    "C1": "Addresses",
    "C3": "Affiliations",
    "RP": "Reprint Address",
    "EM": "Emails",
    "RI": "Researcher IDs",
    "OI": "ORCIDs",
    "FU": "Funding Agencies",
    "FX": "Funding Text",
    "CR": "Cited References",
    "NR": "Cited Reference Count",
    "TC": "Cited by",
    "Z9": "Total Times Cited",
    "PU": "Publisher",
    "PI": "Publisher City",
    "PA": "Publisher Address",
    "SN": "ISSN",
    "EI": "eISSN",
    "J9": "Source Abbreviation",
    "JI": "ISO Source Abbreviation",
    "PD": "Publication Date",
    "PY": "Year",
    "VL": "Volume",
    "IS": "Issue",
    "BP": "Start Page",
    "EP": "End Page",
    "AR": "Article Number",
    "DI": "DOI",
    "DL": "DOI Link",
    "PG": "Page Count",
    "WC": "Web of Science Categories",
    "WE": "Web of Science Index",
    "SC": "Research Areas",
    "DA": "Export Date",
    "UT": "Accession Number",
    "OA": "Open Access",
}

WOS_SIGNATURE_COLUMNS = {"AU", "TI", "SO", "PY", "UT"}

TEXT_NAME_HINTS = ("abstract", "title", "description", "summary", "text", "keyword")
KEYWORD_NAME_HINTS = ("keyword", "subject", "term", "mesh")


def normalize_columns(frame):
    data = frame.copy()
    data.columns = [str(column).lstrip("\ufeff").strip() for column in data.columns]
    if _looks_like_web_of_science(data):
        data.rename(columns=WOS_COLUMN_ALIASES, inplace=True)
    data.rename(columns=STANDARD_COLUMN_ALIASES, inplace=True)
    return data


def _looks_like_web_of_science(frame):
    columns = {str(column).lstrip("\ufeff").strip() for column in frame.columns}
    signature_matches = len(columns.intersection(WOS_SIGNATURE_COLUMNS))
    has_text_metadata = bool(columns.intersection({"AB", "DE", "ID", "DT"}))
    return signature_matches >= 3 and has_text_metadata


def read_upload(uploaded_file):
    return read_upload_bytes(uploaded_file.name, uploaded_file.getvalue())


def read_upload_bytes(name, raw):
    suffix = name.lower()

    if suffix.endswith(".csv"):
        frame = pd.read_csv(BytesIO(raw), low_memory=False)
        if len(frame.columns) and "About the data" in str(frame.columns[0]):
            frame = sf.dim(frame)
    elif suffix.endswith((".xls", ".xlsx")):
        frame = pd.read_excel(BytesIO(raw), sheet_name=0, engine="openpyxl")
        if len(frame.columns) and "About the data" in str(frame.columns[0]):
            frame = sf.dim(frame)
    elif suffix.endswith(".json"):
        payload = json.loads(raw.decode("utf-8"))
        if isinstance(payload, dict):
            if "gathers" in payload and isinstance(payload["gathers"], list):
                payload = payload["gathers"]
            else:
                payload = [payload]
        frame = pd.DataFrame.from_records(payload)
    elif suffix.endswith(".txt"):
        text = raw.decode("utf-8", errors="replace")
        if "PMID" in text:
            frame = sf.medline(BytesIO(raw))
        else:
            try:
                frame = pd.read_csv(StringIO(text), sep="\t", low_memory=False)
                if len(frame.columns) <= 1:
                    frame = pd.DataFrame({"Text": [text]})
            except Exception:
                frame = pd.DataFrame({"Text": [text]})
    else:
        raise ValueError("Unsupported file type.")

    return normalize_columns(frame)


def text_columns(frame):
    object_cols = frame.select_dtypes(include=["object"]).columns.tolist()
    hinted = [
        column for column in object_cols
        if any(hint in column.lower() for hint in TEXT_NAME_HINTS)
    ]
    return hinted or object_cols


def numeric_columns(frame):
    return frame.select_dtypes(include=["number"]).columns.tolist()


def year_column(frame):
    for column in frame.columns:
        if column.lower() == "year" or "year" in column.lower():
            return column
    return None


def keyword_columns(frame):
    object_cols = frame.select_dtypes(include=["object"]).columns.tolist()
    hinted = [
        column for column in object_cols
        if any(hint in column.lower() for hint in KEYWORD_NAME_HINTS)
    ]
    return hinted or object_cols


def split_keywords(series):
    values = series.dropna().astype(str).str.split(r";|,|\|", regex=True).explode().str.strip()
    return values[values.astype(bool)].reset_index(drop=True).astype("object")


def joined_text(frame, columns, limit=None):
    selected = frame[list(columns)].fillna("").astype(str)
    if limit:
        selected = selected.head(limit)
    if len(selected.columns) == 1:
        rows = selected.iloc[:, 0].str.strip()
    else:
        rows = selected.agg(" ".join, axis=1).str.replace(r"\s+", " ", regex=True).str.strip()
    return rows.tolist()


def dataframe_csv(frame):
    return frame.to_csv(index=False).encode("utf-8")


def profile_payload(frame, limit=20):
    missing = frame.isna().sum().sort_values(ascending=False)
    return {
        "row_count": int(len(frame)),
        "column_count": int(len(frame.columns)),
        "columns": [str(column) for column in frame.columns],
        "dtypes": {str(column): str(dtype) for column, dtype in frame.dtypes.items()},
        "missing_values": {str(column): int(value) for column, value in missing.head(limit).items()},
    }
