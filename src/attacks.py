from collections import Counter, defaultdict
from src.crypto import decrypt_posting_list
from src.tokenize import tokenize


def frequency_attack(search_history):
    """
    Simulate a frequency attack based on observed trapdoor frequencies.
    """
    return Counter(search_history)


def keyword_recovery_attack(documents, index, key, k=50, tolerance=0.05, remove_stopwords=False, log_path=None):

    true_doc_freq = defaultdict(int)

    for _, text in documents.items():
        words = set(tokenize(text, remove_stopwords=remove_stopwords))
        for word in words:
            true_doc_freq[word] += 1

    trapdoor_freq = {}

    for trapdoor, enc_posting in index.items():
        posting = decrypt_posting_list(key, enc_posting)
        trapdoor_freq[trapdoor] = len(posting)

    if not true_doc_freq or not trapdoor_freq:
        return 0.0

    keyword_values = sorted(true_doc_freq.values(), reverse=True)[:k]
    trapdoor_values = sorted(trapdoor_freq.values(), reverse=True)[:k]

    correct = 0
    used = set()
    matches = []

    for true_val in keyword_values:
        best_j = None
        best_diff = float("inf")

        for j, trap_val in enumerate(trapdoor_values):
            if j in used:
                continue

            diff = abs(true_val - trap_val)
            if diff < best_diff:
                best_diff = diff
                best_j = j

        allowed_diff = max(1, round(tolerance * true_val))
        is_match = best_j is not None and best_diff <= allowed_diff

        if is_match:
            correct += 1
            used.add(best_j)

        if best_j is not None:
            matches.append({
                "true_freq": true_val,
                "matched_freq": trapdoor_values[best_j],
                "difference": best_diff,
                "within_tolerance": is_match
            })

    if log_path is not None:
        import csv
        with open(log_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "true_freq",
                "matched_freq",
                "difference",
                "within_tolerance"
            ])
            writer.writeheader()
            writer.writerows(matches)

    return correct / len(keyword_values)