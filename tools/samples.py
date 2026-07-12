import pandas as pd


RESEARCH_RECORDS = [
    {
        "Title": "Artificial intelligence literacy in academic libraries",
        "Abstract": "Academic libraries are designing instruction programs that help students evaluate artificial intelligence tools, understand citation risk, and use generative systems responsibly.",
        "Keywords": "artificial intelligence; information literacy; academic libraries; responsible use",
        "Year": 2020,
        "Source title": "Journal of Library Innovation",
        "Document Type": "Article",
        "Cited by": 18,
        "Group": "AI Literacy",
    },
    {
        "Title": "Metadata quality and digital humanities discovery",
        "Abstract": "Digital humanities collections depend on consistent metadata, controlled vocabularies, and transparent documentation for discovery across archives and cultural heritage systems.",
        "Keywords": "metadata; digital humanities; archives; discovery",
        "Year": 2020,
        "Source title": "Digital Scholarship Review",
        "Document Type": "Article",
        "Cited by": 24,
        "Group": "Metadata",
    },
    {
        "Title": "Open science services in research libraries",
        "Abstract": "Research libraries support open science through data management training, repository consultation, publishing support, and research impact guidance.",
        "Keywords": "open science; research data; repositories; scholarly communication",
        "Year": 2021,
        "Source title": "College and Research Libraries",
        "Document Type": "Article",
        "Cited by": 31,
        "Group": "Open Science",
    },
    {
        "Title": "Student privacy in learning analytics dashboards",
        "Abstract": "Learning analytics dashboards can improve student support, but library workers must consider consent, data minimization, and clear explanations of algorithmic limits.",
        "Keywords": "learning analytics; privacy; dashboards; student success",
        "Year": 2021,
        "Source title": "Information Ethics Quarterly",
        "Document Type": "Article",
        "Cited by": 12,
        "Group": "Ethics",
    },
    {
        "Title": "Topic modeling library chat transcripts",
        "Abstract": "Topic models reveal recurring needs in reference chat transcripts, including access questions, citation help, database selection, and remote service issues.",
        "Keywords": "topic modeling; reference services; chat transcripts; text mining",
        "Year": 2021,
        "Source title": "Library Analytics",
        "Document Type": "Conference Paper",
        "Cited by": 9,
        "Group": "Text Mining",
    },
    {
        "Title": "Ethical guidance for generative AI in libraries",
        "Abstract": "Libraries are creating generative AI guidance that balances experimentation with transparency, bias awareness, accessibility, and intellectual property concerns.",
        "Keywords": "generative ai; ethics; bias; library policy",
        "Year": 2022,
        "Source title": "Journal of Library Innovation",
        "Document Type": "Article",
        "Cited by": 42,
        "Group": "AI Literacy",
    },
    {
        "Title": "Citation network patterns in open access publishing",
        "Abstract": "Citation networks show clusters around open access publishing, transformative agreements, author rights, and funder compliance in library literature.",
        "Keywords": "citation networks; open access; scholarly publishing; bibliometrics",
        "Year": 2022,
        "Source title": "Scientometrics and Libraries",
        "Document Type": "Article",
        "Cited by": 35,
        "Group": "Bibliometrics",
    },
    {
        "Title": "Named entities in archival description",
        "Abstract": "Named entity extraction can identify people, organizations, locations, and dates in archival descriptions, supporting collection discovery and remediation work.",
        "Keywords": "named entity recognition; archives; discovery; metadata enrichment",
        "Year": 2022,
        "Source title": "Digital Scholarship Review",
        "Document Type": "Article",
        "Cited by": 16,
        "Group": "Metadata",
    },
    {
        "Title": "Semantic search for institutional repositories",
        "Abstract": "Semantic search improves repository discovery by matching researcher intent to abstracts, keywords, and titles rather than relying only on exact words.",
        "Keywords": "semantic search; repositories; discovery; embeddings",
        "Year": 2023,
        "Source title": "Information Discovery",
        "Document Type": "Article",
        "Cited by": 27,
        "Group": "Search",
    },
    {
        "Title": "Burst detection of emerging library topics",
        "Abstract": "Burst detection helps identify sudden attention to topics such as generative AI, open science, data ethics, and remote instruction.",
        "Keywords": "burst detection; emerging topics; bibliometrics; trend analysis",
        "Year": 2023,
        "Source title": "Library Analytics",
        "Document Type": "Conference Paper",
        "Cited by": 14,
        "Group": "Bibliometrics",
    },
    {
        "Title": "Responsible AI toolkits for research support",
        "Abstract": "Research support teams need practical AI toolkits that include prompt documentation, privacy checks, model limitations, and transparent reporting language.",
        "Keywords": "responsible ai; research support; prompt documentation; transparency",
        "Year": 2024,
        "Source title": "College and Research Libraries",
        "Document Type": "Article",
        "Cited by": 20,
        "Group": "AI Literacy",
    },
    {
        "Title": "Keyword normalization before science mapping",
        "Abstract": "Keyword normalization improves bibliometric maps by merging spelling variants, singular and plural forms, acronyms, and near-duplicate phrases.",
        "Keywords": "keyword normalization; science mapping; bibliometrics; data cleaning",
        "Year": 2024,
        "Source title": "Scientometrics and Libraries",
        "Document Type": "Article",
        "Cited by": 11,
        "Group": "Bibliometrics",
    },
    {
        "Title": "Library sentiment in student survey responses",
        "Abstract": "Student survey responses show positive sentiment about helpful staff and quiet spaces, while negative comments often mention confusing interfaces and access delays.",
        "Keywords": "sentiment analysis; student surveys; user experience; library services",
        "Year": 2024,
        "Source title": "Library Assessment",
        "Document Type": "Report",
        "Cited by": 6,
        "Group": "Assessment",
    },
    {
        "Title": "Comparing humanities and science research language",
        "Abstract": "Scattertext visualizations reveal differences between humanities and science abstracts, including interpretive language, experimental terms, and data-centered vocabulary.",
        "Keywords": "scattertext; research language; humanities; science",
        "Year": 2025,
        "Source title": "Digital Scholarship Review",
        "Document Type": "Article",
        "Cited by": 8,
        "Group": "Text Mining",
    },
    {
        "Title": "AI reporting practices in library research",
        "Abstract": "Transparent AI reporting requires model names, prompts, dates, data handling notes, validation steps, and limitations for generated interpretations.",
        "Keywords": "ai reporting; methods; transparency; research integrity",
        "Year": 2025,
        "Source title": "Information Ethics Quarterly",
        "Document Type": "Article",
        "Cited by": 13,
        "Group": "Ethics",
    },
]


COMPARISON_RECORDS = [
    {
        "Title": "Humanities abstract 1",
        "Text": "The archive reveals memory, interpretation, identity, and cultural context through letters, photographs, and oral histories.",
        "Category": "Humanities",
        "Year": 2022,
        "Keywords": "archives; memory; culture; interpretation",
    },
    {
        "Title": "Humanities abstract 2",
        "Text": "This study examines narrative form, historical imagination, translation, and public meaning in digital literary collections.",
        "Category": "Humanities",
        "Year": 2023,
        "Keywords": "digital humanities; narrative; literature; translation",
    },
    {
        "Title": "Humanities abstract 3",
        "Text": "Museum records show how communities describe place, belonging, migration, and heritage across generations.",
        "Category": "Humanities",
        "Year": 2024,
        "Keywords": "heritage; migration; place; museum records",
    },
    {
        "Title": "Science abstract 1",
        "Text": "The experiment measures model accuracy, sensor reliability, regression error, and reproducible workflow performance.",
        "Category": "Science",
        "Year": 2022,
        "Keywords": "experiment; model accuracy; sensors; reproducibility",
    },
    {
        "Title": "Science abstract 2",
        "Text": "Researchers analyze data pipelines, statistical uncertainty, machine learning classification, and computational efficiency.",
        "Category": "Science",
        "Year": 2023,
        "Keywords": "data pipelines; machine learning; classification; uncertainty",
    },
    {
        "Title": "Science abstract 3",
        "Text": "The dataset supports hypothesis testing, simulation, optimization, and quantitative comparison across experimental conditions.",
        "Category": "Science",
        "Year": 2024,
        "Keywords": "simulation; optimization; hypothesis testing; quantitative analysis",
    },
]


SAMPLE_DATASETS = {
    "Research literature sample": RESEARCH_RECORDS,
    "Text comparison sample": COMPARISON_RECORDS,
}


def names():
    return list(SAMPLE_DATASETS)


def get(name):
    records = SAMPLE_DATASETS.get(name, RESEARCH_RECORDS)
    return pd.DataFrame.from_records(records)


def default_for_tool(tool_name):
    if tool_name in {"Scattertext", "Shifterator"}:
        return "Text comparison sample"
    return "Research literature sample"


def csv_bytes(name):
    return get(name).to_csv(index=False).encode("utf-8")
