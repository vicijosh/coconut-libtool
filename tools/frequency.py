from collections import Counter
import re

import pandas as pd

try:
    from wordcloud import STOPWORDS as WORDCLOUD_STOPWORDS
except Exception:
    WORDCLOUD_STOPWORDS = set()


MODE_AUTO = "Auto"
MODE_WORDS = "Words in text"
MODE_VALUES = "Exact cell values"
MODE_DELIMITED = "Split delimited terms"
COUNT_MODES = [MODE_AUTO, MODE_WORDS, MODE_VALUES, MODE_DELIMITED]

TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_'-]*")
DELIMITER_RE = re.compile(r"[;|,\n]+")
TEXT_HINTS = ("abstract", "description", "summary", "text", "title")
DELIMITED_HINTS = ("keyword", "keywords", "subject", "subjects", "mesh", "term", "terms")

DEFAULT_STOPWORDS = frozenset(
    {word.lower() for word in WORDCLOUD_STOPWORDS}
    | {
        "also",
        "among",
        "using",
        "use",
        "used",
        "based",
        "study",
        "studies",
        "paper",
        "article",
        "research",
    }
)


def parse_stopwords(raw_words):
    if not raw_words:
        return set()
    return {
        word.strip().lower()
        for word in re.split(r"[;,\n|]+", str(raw_words))
        if word.strip()
    }


def normalize_mode(mode):
    return mode if mode in COUNT_MODES else MODE_AUTO


def _clean_value(value):
    if pd.isna(value):
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return re.sub(r"\s+", " ", str(value)).strip()


def infer_count_mode(series, column_name=""):
    if pd.api.types.is_numeric_dtype(series):
        return MODE_VALUES

    name = str(column_name).lower()
    sample = series.dropna().astype(str).head(250)
    if sample.empty:
        return MODE_WORDS

    avg_words = sample.map(lambda value: len(TOKEN_RE.findall(value))).mean()
    delimited_share = sample.map(lambda value: bool(DELIMITER_RE.search(value))).mean()
    unique_ratio = sample.nunique(dropna=True) / max(len(sample), 1)

    if any(hint in name for hint in DELIMITED_HINTS) and delimited_share >= 0.15:
        return MODE_DELIMITED
    if any(hint in name for hint in TEXT_HINTS):
        return MODE_WORDS
    if avg_words >= 5:
        return MODE_WORDS
    if unique_ratio > 0.65 and avg_words >= 3:
        return MODE_WORDS
    return MODE_VALUES


def _top_items(counter, max_items):
    return pd.DataFrame(counter.most_common(max_items), columns=["Word", "Frequency"])


def _value_frequency(series, max_items, blocked_words):
    values = series.dropna().map(_clean_value)
    values = values[values.astype(bool)]
    if blocked_words:
        values = values[~values.str.lower().isin(blocked_words)]
    counts = values.value_counts(sort=True).head(max_items)
    return counts.rename_axis("Word").reset_index(name="Frequency")


def _delimited_frequency(series, max_items, blocked_words):
    counter = Counter()
    for value in series.dropna().astype(str):
        parts = [part.strip().lower() for part in DELIMITER_RE.split(value) if part.strip()]
        counter.update(part for part in parts if part not in blocked_words)
    return _top_items(counter, max_items)


def _word_frequency(series, max_items, blocked_words, min_word_length):
    stopwords = DEFAULT_STOPWORDS | set(blocked_words)
    counter = Counter()
    for value in series.dropna().astype(str):
        tokens = (
            token.lower().strip("'_-")
            for token in TOKEN_RE.findall(value)
        )
        counter.update(
            token
            for token in tokens
            if len(token) >= min_word_length and token not in stopwords
        )
    return _top_items(counter, max_items)


def frequency_frame(series, column_name="", mode=MODE_AUTO, max_items=250, extra_stopwords=None, min_word_length=2):
    max_items = max(1, int(max_items or 1))
    blocked_words = parse_stopwords(extra_stopwords)
    selected_mode = normalize_mode(mode)
    resolved_mode = infer_count_mode(series, column_name) if selected_mode == MODE_AUTO else selected_mode

    if resolved_mode == MODE_VALUES:
        frame = _value_frequency(series, max_items, blocked_words)
    elif resolved_mode == MODE_DELIMITED:
        frame = _delimited_frequency(series, max_items, blocked_words)
    else:
        frame = _word_frequency(series, max_items, blocked_words, int(min_word_length or 1))

    if frame.empty:
        frame = pd.DataFrame(columns=["Word", "Frequency"])
    frame["Word"] = frame["Word"].astype(str)
    frame["Frequency"] = frame["Frequency"].astype(int)
    return frame, resolved_mode


def frequency_dict(frame):
    return {
        str(row.Word): int(row.Frequency)
        for row in frame.itertuples(index=False)
        if int(row.Frequency) > 0
    }
