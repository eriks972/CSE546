import re

STOPWORDS = set([
    "the","and","to","of","a","in","for","on","with","is",
    "this","that","by","from","as","at","it","an","be"
])

def tokenize(text, remove_stopwords=True):
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())

    if remove_stopwords:
        return [w for w in words if w not in STOPWORDS]

    return words