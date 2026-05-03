from src.index import build_index, search, add_document
from src.crypto import generate_key
from src.leakage import LeakageTracker
from src.attacks import frequency_attack
import matplotlib.pyplot as plt
from collections import Counter
import time

def main():

    key = generate_key()

    documents = {
        1: "Encryption allows secure search",
        2: "Searchable encryption protects privacy",
        3: "Cloud systems store encrypted data"
    }

    print("Documents:")
    for k, v in documents.items():
        print(k, v)

    print("\nBuilding encrypted index...")
    index = build_index(documents, key)

    print("\nEncrypted Index (ciphertext posting lists):")

    for trapdoor, blob in index.items():
        print(trapdoor[:16], "... -> ciphertext size:", len(blob))

    # ----------------------------
    # Leakage Tracker
    # ----------------------------

    tracker = LeakageTracker()

    print("\nRunning Queries")

    queries = ["search", "encryption", "search", "privacy"]

    for q in queries:

        results = search(q, index, key, tracker)

        print(f"Query '{q}' -> {results}")

    # ----------------------------
    # Leakage Statistics
    # ----------------------------

    print("\nLeakage Statistics")

    print("Repeated searches:", tracker.search_pattern_leakage())

    print("Repeated access patterns:", tracker.access_pattern_leakage())

    # ----------------------------
    # Frequency Attack Simulation
    # ----------------------------

    print("\nFrequency Attack Simulation")

    attack_results = frequency_attack(tracker.search_history)

    for trapdoor, count in attack_results.items():
        print(trapdoor[:16], "... appeared", count, "times")

    #----------------------------
    # Plotting frequency distribution
    #----------------------------
    counts = Counter(tracker.search_history)

    labels = [t[:8] for t in counts.keys()]
    values = counts.values()

    plt.figure()

    plt.bar(labels, values)

    plt.title("Trapdoor Frequency Distribution")

    plt.xlabel("Trapdoors")

    plt.ylabel("Frequency")

    plt.show()

    #----------------------------
    # Dynamic Insertion
    #----------------------------

    print("\nTesting Dynamic Update")

    new_doc_id = 4
    new_doc_text = "secure cloud encryption"

    start = time.time()

    add_document(new_doc_id, new_doc_text, index, key)

    update_time = time.time() - start

    print("Inserted document:", new_doc_text)

    print("Update time:", round(update_time,6), "seconds")

    results = search("cloud", index, key)

    print("Search results for 'cloud' after update:", results)

if __name__ == "__main__":
    main()