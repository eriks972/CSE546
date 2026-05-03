import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from src.crypto import decrypt_posting_list


def jaccard_similarity(a, b):
    a = set(a)
    b = set(b)

    if len(a | b) == 0:
        return 0

    return len(a & b) / len(a | b)


def analyze_cooccurrence(index, key, top_k=50):
    """
    Generate trapdoor similarity heatmap
    """

    posting_lists = {}

    for trapdoor, blob in index.items():
        posting_lists[trapdoor] = decrypt_posting_list(key, blob)

    # select top-k largest posting lists
    sorted_items = sorted(posting_lists.items(),
                          key=lambda x: len(x[1]),
                          reverse=True)[:top_k]

    trapdoors = [t[0] for t in sorted_items]

    matrix = []

    for t1 in trapdoors:
        row = []

        for t2 in trapdoors:
            sim = jaccard_similarity(posting_lists[t1], posting_lists[t2])
            row.append(sim)

        matrix.append(row)

    matrix = np.array(matrix)

    plt.figure(figsize=(8,6))
    sns.heatmap(matrix, cmap="viridis")
    plt.title("Trapdoor Co-occurrence Similarity")

    plt.savefig("results/cooccurrence_heatmap.png")
    plt.close()