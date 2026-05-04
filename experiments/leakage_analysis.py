import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from src.crypto import decrypt_posting_list
from src.crypto import generate_key
from src.index import build_index
from dataset.enron_loader import load_enron_dataset


def jaccard_similarity(a, b):
    a = set(a)
    b = set(b)

    if len(a | b) == 0:
        return 0

    return len(a & b) / len(a | b)


def analyze_cooccurrence(index, key, top_k=50):
    """
    Generate trapdoor similarity heatmap.
    """

    posting_lists = {}

    for trapdoor, blob in index.items():
        posting_lists[trapdoor] = decrypt_posting_list(key, blob)

    sorted_items = sorted(
        posting_lists.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )[:top_k]

    trapdoors = [t[0] for t in sorted_items]

    matrix = []

    for t1 in trapdoors:
        row = []
        for t2 in trapdoors:
            sim = jaccard_similarity(posting_lists[t1], posting_lists[t2])
            row.append(sim)
        matrix.append(row)

    matrix = np.array(matrix)

    os.makedirs("results", exist_ok=True)

    plt.figure(figsize=(8, 6))
    sns.heatmap(matrix, cmap="viridis")
    plt.title("Trapdoor Co-occurrence Similarity")
    plt.xlabel("Trapdoors")
    plt.ylabel("Trapdoors")
    plt.savefig("results/cooccurrence_heatmap.png", dpi=300, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    key = generate_key()

    documents = load_enron_dataset("dataset/emails.csv", limit=10000)
    index = build_index(documents, key, mode="normal", remove_stopwords=True)

    analyze_cooccurrence(index, key, top_k=50)

    print("Saved results/cooccurrence_heatmap.png")