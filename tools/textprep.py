import re
from functools import lru_cache

from nltk.stem import WordNetLemmatizer


PUNCTUATION_RE = r"[,:;.!?•=\-\(\)\[\]\{\}\"'`/\\]"
QUOTE_RE = r"[\u2018\u2019\u201c\u201d]"


@lru_cache(maxsize=1)
def _lemmatizer():
    return WordNetLemmatizer()


def parse_remove_words(raw_words):
    return [word.strip().lower() for word in str(raw_words or "").split(";") if word.strip()]


def _word_pattern(words):
    words = [word for word in words if word]
    if not words:
        return None
    return r"\b(?:" + "|".join(re.escape(word) for word in sorted(set(words), key=len, reverse=True)) + r")\b"


def _lemmatize_text(text, lemmatizer):
    return " ".join(lemmatizer.lemmatize(word) for word in str(text).split())


def clean_text_series(
    series,
    stop_words=None,
    remove_words=None,
    remove_punctuation=True,
    remove_copyright=False,
    lemmatize=True,
):
    cleaned = series.dropna().astype(str).str.lower()

    if remove_copyright:
        cleaned = cleaned.str.replace(r"©.*", "", regex=True)

    if remove_punctuation:
        cleaned = (
            cleaned.str.replace(PUNCTUATION_RE, " ", regex=True)
            .str.replace(QUOTE_RE, "", regex=True)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

    stop_pattern = _word_pattern([word.lower() for word in (stop_words or [])])
    if stop_pattern:
        cleaned = cleaned.str.replace(stop_pattern, " ", regex=True).str.replace(r"\s+", " ", regex=True).str.strip()

    remove_pattern = _word_pattern(parse_remove_words(remove_words))
    if remove_pattern:
        cleaned = cleaned.str.replace(remove_pattern, " ", regex=True).str.replace(r"\s+", " ", regex=True).str.strip()

    if lemmatize:
        lemmatizer = _lemmatizer()
        cleaned = cleaned.map(lambda text: _lemmatize_text(text, lemmatizer))

    return cleaned


def clean_frame_column(
    frame,
    column,
    stop_words=None,
    remove_words=None,
    remove_punctuation=True,
    remove_copyright=False,
    lemmatize=True,
    output_column=None,
):
    output = frame.dropna(subset=[column]).copy()
    target = output_column or column
    output[target] = clean_text_series(
        output[column],
        stop_words=stop_words,
        remove_words=remove_words,
        remove_punctuation=remove_punctuation,
        remove_copyright=remove_copyright,
        lemmatize=lemmatize,
    )
    return output
