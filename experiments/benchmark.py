import time
import json
import os
import numpy as np
import matplotlib.pyplot as plt
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.index import build_index
from src.crypto import generate_key, decrypt_posting_list, prf_forward_private
from src.search import search
from src.tokenize import tokenize
from dataset.enron_loader import load_enron_dataset
from src.attacks import keyword_recovery_attack

# Ensure results folder exists
os.makedirs("results", exist_ok=True)


def jaccard_similarity(a, b):
    a = set(a)
    b = set(b)
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def benchmark(n_docs, mode="normal", remove_stopwords=False):
    key = generate_key()

    # Load dataset
    documents = load_enron_dataset("dataset/emails.csv", limit=n_docs)
    dataset_size = len(json.dumps(documents).encode())

    # Build index
    start = time.time()
    index = build_index(documents, key, mode, remove_stopwords=remove_stopwords)
    setup_time = time.time() - start

    # Forward privacy check
    fp_trapdoors = [prf_forward_private(key, "test") for _ in range(3)]

    # Query timing
    queries = ["search", "data", "cloud", "privacy"]
    start = time.time()
    for q in queries:
        search(q, index, key)
    query_time = (time.time() - start) / len(queries)

    # Storage metric
    index_size = sum(len(v) for v in index.values())
    expansion_ratio = index_size / dataset_size if dataset_size else 0.0

    # Decrypt posting lists once
    posting_lists = {}
    posting_sizes = []

    for trapdoor, blob in index.items():
        posting = decrypt_posting_list(key, blob)
        posting_lists[trapdoor] = posting
        posting_sizes.append(len(posting))

    # Co-occurrence matrix for top-k largest posting lists
    top_k_heatmap = 40
    sorted_items = sorted(
        posting_lists.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )[:top_k_heatmap]

    trapdoors = [t[0] for t in sorted_items]
    matrix = []

    for t1 in trapdoors:
        row = []
        for t2 in trapdoors:
            row.append(jaccard_similarity(posting_lists[t1], posting_lists[t2]))
        matrix.append(row)

    matrix = np.array(matrix)

    # True keyword frequency
    true_freq = {}
    for doc in documents.values():
        words = tokenize(doc, remove_stopwords=remove_stopwords)
        for word in words:
            true_freq[word] = true_freq.get(word, 0) + 1

    # Observed trapdoor frequency
    trapdoor_freq = {}
    for trapdoor, plist in posting_lists.items():
        trapdoor_freq[trapdoor] = len(plist)

    # Baseline frequency-match recovery
    true_sorted = sorted(true_freq.items(), key=lambda x: x[1], reverse=True)
    trapdoor_sorted = sorted(trapdoor_freq.items(), key=lambda x: x[1], reverse=True)

    top_k = 50
    compare_count = min(top_k, len(true_sorted), len(trapdoor_sorted))
    correct = 0

    for i in range(compare_count):
        true_val = true_sorted[i][1]
        trap_val = trapdoor_sorted[i][1]
        if abs(true_val - trap_val) < 0.05 * true_val:
            correct += 1

    baseline_recovery = correct / compare_count if compare_count else 0.0
    attack_recovery = keyword_recovery_attack(documents, index, key, remove_stopwords=remove_stopwords,log_path=f"results/leakage_{mode}_{n}.csv")

    result = {
        "mode": mode,
        "setup_time": setup_time,
        "query_time": query_time,
        "expansion_ratio": expansion_ratio,
        "posting_sizes": posting_sizes,
        "baseline_recovery": baseline_recovery,
        "attack_recovery": attack_recovery,
        "fp_trapdoors": fp_trapdoors,
    }

    return result


if __name__ == "__main__":
    dataset_sizes = [100, 1000, 5000, 10000, 30000, 50000, 100000]

    setup_times = []
    query_times = []
    expansion_ratios = []

    # Recovery tracking
    normal_with_sw = []
    normal_without_sw = []
    fp_with_sw = []
    fp_without_sw = []

    last_posting_sizes = []
    results_rows = []

    print("\n===== Benchmarking SSE Scheme (4 Configurations) =====\n")

    for n in dataset_sizes:

        # ---- Run all 4 configurations ----
        normal_sw = benchmark(n, mode="normal", remove_stopwords=False)
        normal_no_sw = benchmark(n, mode="normal", remove_stopwords=True)

        fp_sw = benchmark(n, mode="forward_private", remove_stopwords=False)
        fp_no_sw = benchmark(n, mode="forward_private", remove_stopwords=True)
        

        # ---- Store results (use normal + stopwords for base metrics) ----
        setup_times.append(normal_sw["setup_time"])
        query_times.append(normal_sw["query_time"])
        expansion_ratios.append(normal_sw["expansion_ratio"])
        last_posting_sizes = normal_sw["posting_sizes"]

        normal_with_sw.append(normal_sw["attack_recovery"])
        normal_without_sw.append(normal_no_sw["attack_recovery"])
        fp_with_sw.append(fp_sw["attack_recovery"])
        fp_without_sw.append(fp_no_sw["attack_recovery"])

        # ---- Clean console output ----
        print(f"Dataset size: {n}")
        print("-" * 60)

        print("Normal SSE (With Stopwords)")
        print(f"  Attack recovery: {normal_sw['attack_recovery']:.4f}")

        print("Normal SSE (No Stopwords)")
        print(f"  Attack recovery: {normal_no_sw['attack_recovery']:.4f}")

        print("Forward-Private SSE (With Stopwords)")
        print(f"  Attack recovery: {fp_sw['attack_recovery']:.4f}")

        print("Forward-Private SSE (No Stopwords)")
        print(f"  Attack recovery: {fp_no_sw['attack_recovery']:.4f}")

        print("=" * 60)

    # ----------------------------
    # Setup time graph
    # ----------------------------
    plt.figure()
    plt.plot(dataset_sizes, setup_times, marker="o")
    plt.yscale("log")
    plt.title("Dataset Size vs Setup Time")
    plt.xlabel("Documents")
    plt.ylabel("Setup Time (seconds)")
    plt.grid(True)
    plt.savefig("results/setup_time.png")
    plt.close()

    # ----------------------------
    # Query time graph
    # ----------------------------
    plt.figure()
    plt.plot(dataset_sizes, query_times, marker="o")
    plt.title("Dataset Size vs Query Time")
    plt.xlabel("Documents")
    plt.ylabel("Query Time (seconds)")
    plt.grid(True)
    plt.savefig("results/query_time.png")
    plt.close()

    # ----------------------------
    # Posting size distribution
    # ----------------------------
    plt.figure()
    plt.hist(last_posting_sizes, bins=50)
    plt.xscale("log")
    plt.yscale("log")
    plt.title("Posting List Size Distribution")
    plt.xlabel("Number of Matches")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.savefig("results/posting_distribution.png")
    plt.close()

    # ----------------------------
    # 4-WAY RECOVERY COMPARISON
    # ----------------------------
    plt.figure()

    plt.plot(dataset_sizes, normal_with_sw, marker="o", label="Normal (With Stopwords)")
    plt.plot(dataset_sizes, normal_without_sw, marker="o", label="Normal (No Stopwords)")
    plt.plot(dataset_sizes, fp_with_sw, marker="o", label="FP (With Stopwords)")
    plt.plot(dataset_sizes, fp_without_sw, marker="o", label="FP (No Stopwords)")

    plt.title("Keyword Recovery Comparison (All Configurations)")
    plt.xlabel("Dataset Size")
    plt.ylabel("Recovery Rate")
    plt.legend()
    plt.grid(True)

    plt.savefig("results/recovery_4way_comparison.png")
    plt.close()

    print("\nSaved plots to results/:")
    print("  - setup_time.png")
    print("  - query_time.png")
    print("  - posting_distribution.png")
    print("  - recovery_4way_comparison.png")