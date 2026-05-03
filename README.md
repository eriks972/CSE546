# Practical Symmetric Searchable Encryption (SSE)

This repository contains the implementation and experimental evaluation for the project:

**“Practical Symmetric Searchable Encryption: Performance, Leakage, and Forward Privacy”**

---

## Overview

This project implements a **symmetric searchable encryption (SSE)** system that enables efficient keyword search over encrypted data while preserving confidentiality.

The system is based on:

* Encrypted inverted indices
* Pseudorandom function (PRF)-based trapdoor generation
* Authenticated encryption for secure storage

We analyze both **performance** and **security leakage**, and evaluate how forward privacy impacts real-world attacks.

---

## Features

* Baseline SSE with deterministic trapdoors
* Forward-private SSE using counter-based trapdoors
* Frequency-based keyword recovery attack
* Co-occurrence leakage analysis
* Performance benchmarking across multiple dataset sizes

---

## Dataset

We use the **Enron Email Dataset**, a real-world corpus of email communications.

To evaluate scalability, we construct subsets of increasing size:

* 100 documents
* 1,000 documents
* 5,000 documents
* 10,000 documents
* 30,000 documents
* 50,000 documents
* 100,000 documents

---

## System Design

### Index Construction

* Documents are tokenized into keywords
* An inverted index maps each keyword to document IDs
* Each keyword is transformed into a trapdoor using a PRF:

  * `τ_w = F_k(w)`
* Posting lists are encrypted using AES-GCM

### Query Processing

* Client generates trapdoor `τ_w`
* Server returns encrypted posting list
* Client decrypts results

### Forward Privacy Extension

* Uses counter-based trapdoors:

  * `τ_{w,i} = F_k(w || i)`
* Prevents linking repeated queries
* Improves resistance to leakage attacks

---

## Experiments

We evaluate both **performance** and **security**:

### Performance Metrics

* Setup time (index construction)
* Query time
* Storage overhead (index expansion ratio)

### Security Metrics

* Keyword recovery rate under attack
* Trapdoor frequency analysis
* Co-occurrence leakage patterns

---

## Repository Structure

```
CSE546/
│
├── index.py / build_index.py   # SSE index construction
├── search.py                  # Query execution
├── attacks.py                 # Leakage-based attacks
├── benchmark.py               # Performance experiments
├── results/                   # Generated CSVs and plots
└── README.md                  # Project documentation
```

---

## How to Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run experiments:

```bash
python benchmark.py
```

3. View results:

* Output CSV files will be saved in `results/`
* Plots can be generated from these results

---

## Key Insights

* SSE enables efficient encrypted search but leaks structural information
* Frequency and co-occurrence patterns can be exploited by attackers
* Forward privacy significantly reduces query linkage
* However, leakage is not fully eliminated

---

## Security Notes

This implementation assumes:

* A secure pseudorandom function (HMAC-SHA256)
* A secure authenticated encryption scheme (AES-GCM)

Even under these assumptions, the system leaks:

* Search patterns (baseline)
* Access patterns
* Result sizes

These leakages are inherent to practical SSE systems.

---

## Author

**Erik Swanson**
CSE 546 – Cryptography / Security Project

---

## References

* Jonathan Katz and Yehuda Lindell. *Introduction to Modern Cryptography*, 2nd Edition.
* Goldreich, Goldwasser, Micali. *How to Construct Random Functions*, 1986.
* Bellare and Namprempre. *Authenticated Encryption*, ASIACRYPT 2000.
