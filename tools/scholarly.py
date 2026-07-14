import math
import re
import urllib.error
import urllib.parse
import urllib.request

import pandas as pd
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer


OPENALEX_BASE_URL = "https://api.openalex.org/works"

GAP_PHRASES = (
    "future research",
    "further research",
    "more research",
    "additional research",
    "further studies",
    "more studies",
    "additional studies",
    "future studies",
    "limited evidence",
    "more evidence",
    "additional evidence",
    "not well understood",
    "remains unclear",
    "underexplored",
    "under studied",
    "under-studied",
    "research gap",
)

SOLUTION_PHRASES = (
    "we propose",
    "we developed",
    "we develop",
    "we introduce",
    "we present",
    "framework",
    "intervention",
    "solution",
    "toolkit",
    "model",
    "method",
    "approach",
)

SYNTHESIS_PHRASES = (
    "systematic review",
    "literature review",
    "scoping review",
    "meta-analysis",
    "review of",
)


def clean_query(value, max_chars=420):
    value = re.sub(r"\s+", " ", str(value or "")).strip()
    return value[:max_chars]


def extract_terms(texts, max_terms=12):
    documents = [str(text).strip() for text in texts if str(text).strip()]
    if not documents:
        return []

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=1200, min_df=1)
    try:
        matrix = vectorizer.fit_transform(documents)
    except ValueError:
        return []
    scores = matrix.sum(axis=0).A1
    terms = vectorizer.get_feature_names_out()
    ranked = sorted(zip(terms, scores), key=lambda item: item[1], reverse=True)
    return [term for term, _score in ranked[:max_terms]]


def query_terms(query):
    return {
        token.lower()
        for token in re.findall(r"\b[a-zA-Z][a-zA-Z\-]{2,}\b", str(query))
        if token.lower() not in ENGLISH_STOP_WORDS
    }


def abstract_from_inverted_index(index):
    if not isinstance(index, dict) or not index:
        return ""
    positioned = []
    for word, positions in index.items():
        for position in positions or []:
            positioned.append((int(position), str(word)))
    positioned.sort(key=lambda item: item[0])
    return " ".join(word for _position, word in positioned)


def _get_json(url, params=None, timeout=25):
    query = urllib.parse.urlencode({k: v for k, v in (params or {}).items() if v not in (None, "")})
    full_url = f"{url}?{query}" if query else url
    request = urllib.request.Request(
        full_url,
        headers={
            "Accept": "application/json",
            "User-Agent": "Coconut-Libtool/1.0 (scholarly metadata lookup)",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAlex returned HTTP {exc.code}: {details}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach OpenAlex: {exc.reason}") from exc


def openalex_search(query, from_year=None, to_year=None, per_page=25, api_key="", mailto=""):
    import json

    query = clean_query(query)
    if not query:
        return []

    filters = []
    if from_year:
        filters.append(f"from_publication_date:{int(from_year)}-01-01")
    if to_year:
        filters.append(f"to_publication_date:{int(to_year)}-12-31")

    params = {
        "search": query,
        "per_page": max(1, min(int(per_page or 25), 100)),
        "select": ",".join(
            [
                "id",
                "doi",
                "display_name",
                "publication_year",
                "cited_by_count",
                "type",
                "authorships",
                "primary_location",
                "open_access",
                "topics",
                "keywords",
                "abstract_inverted_index",
            ]
        ),
    }
    if filters:
        params["filter"] = ",".join(filters)
    if api_key:
        params["api_key"] = api_key.strip()
    if mailto:
        params["mailto"] = mailto.strip()

    payload = json.loads(_get_json(OPENALEX_BASE_URL, params=params))
    return payload.get("results", [])


def _source_name(work):
    source = ((work.get("primary_location") or {}).get("source") or {})
    return source.get("display_name") or ""


def _landing_url(work):
    location = work.get("primary_location") or {}
    return location.get("landing_page_url") or work.get("doi") or work.get("id") or ""


def _countries(work):
    countries = []
    for authorship in work.get("authorships") or []:
        for institution in authorship.get("institutions") or []:
            country = institution.get("country_code")
            if country and country not in countries:
                countries.append(country)
    return countries


def _topic_names(work):
    topics = []
    for topic in work.get("topics") or []:
        name = topic.get("display_name")
        if name and name not in topics:
            topics.append(name)
    if topics:
        return topics
    keywords = []
    for keyword in work.get("keywords") or []:
        name = keyword.get("display_name")
        if name and name not in keywords:
            keywords.append(name)
    return keywords


def works_to_frame(works):
    rows = []
    for work in works:
        abstract = abstract_from_inverted_index(work.get("abstract_inverted_index"))
        countries = _countries(work)
        topics = _topic_names(work)
        rows.append(
            {
                "Title": work.get("display_name") or "Untitled",
                "Year": work.get("publication_year"),
                "Cited by": int(work.get("cited_by_count") or 0),
                "Type": work.get("type") or "",
                "Source": _source_name(work),
                "DOI": work.get("doi") or "",
                "URL": _landing_url(work),
                "Open access": bool((work.get("open_access") or {}).get("is_oa")),
                "Countries": "; ".join(countries),
                "Topics": "; ".join(topics[:5]),
                "Abstract": abstract,
            }
        )
    return pd.DataFrame(rows)


def classify_relation(row, seed_terms):
    text = f"{row.get('Title', '')} {row.get('Abstract', '')}".lower()
    title = str(row.get("Title", "")).lower()
    kind = str(row.get("Type", "")).lower()
    terms = set(seed_terms or [])
    found = {term for term in terms if term in text}
    overlap = len(found) / max(len(terms), 1)

    if any(phrase in text for phrase in GAP_PHRASES):
        return "Requests more evidence"
    if any(phrase in title or phrase in text[:700] for phrase in SYNTHESIS_PHRASES) or "review" in kind:
        return "Evidence synthesis"
    if any(phrase in text[:900] for phrase in SOLUTION_PHRASES):
        return "Possible solution or method"
    if overlap >= 0.45:
        return "Directly related"
    if overlap >= 0.2:
        return "Partially related"
    return "Adjacent context"


def score_relation(row, seed_terms):
    text = f"{row.get('Title', '')} {row.get('Abstract', '')}".lower()
    found = sum(1 for term in seed_terms if term in text)
    overlap_score = found / max(len(seed_terms), 1)
    citation_score = math.log1p(float(row.get("Cited by") or 0)) / 8
    year = row.get("Year")
    try:
        recency_score = max(0, (int(year) - 2015) / 12)
    except Exception:
        recency_score = 0
    return round((0.68 * overlap_score + 0.18 * citation_score + 0.14 * recency_score) * 100, 1)


def classify_research_radar(frame, query):
    if frame.empty:
        return frame
    terms = query_terms(query)
    output = frame.copy()
    output["Evidence relationship"] = output.apply(lambda row: classify_relation(row, terms), axis=1)
    output["Radar score"] = output.apply(lambda row: score_relation(row, terms), axis=1)
    return output.sort_values(["Radar score", "Cited by"], ascending=False).reset_index(drop=True)


def future_research_signal(text):
    lowered = str(text or "").lower()
    matches = [phrase for phrase in GAP_PHRASES if phrase in lowered]
    return "; ".join(matches[:4])


def build_gap_signals(frame, from_year=None, to_year=None):
    if frame.empty:
        return pd.DataFrame()

    working = frame.copy()
    working["Gap phrase"] = working["Abstract"].map(future_research_signal)
    working["Year"] = pd.to_numeric(working["Year"], errors="coerce")
    min_year = int(from_year or working["Year"].min() or 0)
    max_year = int(to_year or working["Year"].max() or min_year)
    recent_floor = max(min_year, max_year - 2)

    topic_rows = []
    for _idx, row in working.iterrows():
        topics = [part.strip() for part in str(row.get("Topics", "")).split(";") if part.strip()]
        for topic in topics:
            topic_rows.append({"Topic": topic, "Year": row.get("Year"), "Gap phrase": row.get("Gap phrase", "")})

    if not topic_rows:
        return pd.DataFrame()

    topic_frame = pd.DataFrame(topic_rows)
    total_counts = topic_frame.groupby("Topic").size()
    recent_counts = topic_frame[topic_frame["Year"] >= recent_floor].groupby("Topic").size()
    gap_counts = topic_frame[topic_frame["Gap phrase"].astype(bool)].groupby("Topic").size()

    rows = []
    for topic, count in total_counts.items():
        recent = int(recent_counts.get(topic, 0))
        gap_mentions = int(gap_counts.get(topic, 0))
        recent_share = recent / max(int(count), 1)
        if count <= 3 and recent > 0:
            signal = "Emerging but thin evidence"
        elif gap_mentions > 0 and gap_mentions / max(int(count), 1) >= 0.25:
            signal = "Authors often ask for more evidence"
        elif count <= 2:
            signal = "Sparse coverage"
        else:
            signal = "Established area"
        rows.append(
            {
                "Topic": topic,
                "Works found": int(count),
                "Recent works": recent,
                "Recent share": round(recent_share, 2),
                "Gap-phrase mentions": gap_mentions,
                "Gap signal": signal,
            }
        )

    return pd.DataFrame(rows).sort_values(
        ["Gap signal", "Gap-phrase mentions", "Recent share", "Works found"],
        ascending=[False, False, False, True],
    )
