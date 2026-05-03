import pandas as pd
import re

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    return text

def load_enron_dataset(path, limit=1000):

    df = pd.read_csv(path, nrows=limit)

    documents = {}

    for i in range(limit):

        text = df.iloc[i]["message"]

        documents[i+1] = clean_text(text)

    return documents