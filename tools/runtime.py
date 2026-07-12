import nltk


_NLTK_PATHS = {
    "punkt": "tokenizers/punkt",
    "punkt_tab": "tokenizers/punkt_tab",
    "stopwords": "corpora/stopwords",
    "vader_lexicon": "sentiment/vader_lexicon.zip",
    "wordnet": "corpora/wordnet",
}

_CHECKED_RESOURCES = set()

def ensure_nltk_data(*resources):
    resources_to_check = [resource for resource in resources if resource not in _CHECKED_RESOURCES]
    missing = []
    for resource in resources_to_check:
        lookup_path = _NLTK_PATHS.get(resource, resource)
        try:
            nltk.data.find(lookup_path)
        except LookupError:
            missing.append(resource)

    for resource in missing:
        nltk.download(resource, quiet=True)

    _CHECKED_RESOURCES.update(resources_to_check)
    return True
