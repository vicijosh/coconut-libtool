import streamlit as st

from tools import ai, ui, workbench


st.set_page_config(
    page_title="Coconut",
    page_icon="🥥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ui.apply_app_style()
ui.render_tool_menu()
ui.render_page_header("AI Method Explainer", "Translate analysis methods and settings into plain language.")


METHODS = {
    "Scattertext": "Compares term usage between two groups and visualizes terms that are distinctive to each group.",
    "Topic Modeling": "Finds latent themes in a text collection using probabilistic, biterm, or embedding-based models.",
    "Bidirected Network": "Uses association rules to show directional relationships between keyword pairs.",
    "Sunburst": "Summarizes hierarchical relationships such as document type, source, and year.",
    "Burst Detection": "Detects periods when terms appear unusually often compared with surrounding years.",
    "Keywords Stem": "Normalizes keyword forms using stemming or lemmatization.",
    "Sentiment Analysis": "Scores text polarity, subjectivity, and positive/negative/neutral language.",
    "Shifterator": "Compares word contributions between two text groups.",
    "Semantic Search": "Ranks records by text similarity to a search query.",
    "Named Entity Extraction": "Extracts people, organizations, places, dates, and other named entities.",
    "Corpus Overview": "Profiles a dataset so users can understand rows, columns, missing values, likely text fields, and recommended next tools.",
    "Data Cleaner": "Standardizes common fields, cleans spacing, converts blank values, and removes duplicates before analysis.",
    "Bibliometric Overview": "Summarizes publication years, sources, document types, citations, and keywords from research exports.",
    "Term/Keyword Evolution": "Tracks how selected keywords, phrases, or tokens rise and fade across years.",
    "Ask Your Dataset": "Uses an aggregate dataset profile, and optional user-approved excerpts, to answer interpretive questions with AI.",
    "AI Report Builder": "Turns user-provided methods, findings, caveats, and optional aggregate dataset context into a structured report.",
    "Text Summarization": "Condenses abstracts, articles, notes, or selected text columns into concise summaries and key takeaways.",
}

method = st.selectbox("Method", list(METHODS))
settings = st.text_area("Settings or result details to explain")
audience = st.selectbox("Audience", ["Beginner", "Student", "Researcher", "Librarian", "Administrator"])

payload = {
    "module": "AI Method Explainer",
    "privacy": "Method notes only. No uploaded dataset is required.",
    "method": method,
    "plain_description": METHODS[method],
    "settings_or_results": settings,
    "audience": audience,
}

st.info(METHODS[method])
workbench.render_ai_guardrail()
ai.render_ai_insights(
    "AI Method Explainer",
    payload,
    f"method_explainer_{method.lower().replace(' ', '_')}",
    "Explain this method, how to interpret it, what can go wrong, and how to report it responsibly.",
)
