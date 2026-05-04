import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

def plot_scatter(csv_path, output_path, title):
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)

    # ---- Handle edge cases ----
    if len(df) > 1 and df["matched_freq"].std() > 0:
        corr = np.corrcoef(df["true_freq"], df["matched_freq"])[0, 1]
    else:
        corr = 0.0

    print(f"{title} Correlation:", corr)

    plt.figure()

    if len(df) > 0:
        plt.scatter(df["true_freq"], df["matched_freq"], alpha=0.5)

        max_val = max(df["true_freq"])

        # Ideal diagonal
        plt.plot([0, max_val], [0, max_val], 'r--')

        # Correlation text
        plt.text(
            0.05 * max_val,
            0.9 * max_val,
            f"Correlation = {corr:.3f}",
            fontsize=12,
            bbox=dict(facecolor='white', alpha=0.7)
        )
    else:
        plt.text(0.5, 0.5, "No data (No leakage detected)",
                 ha='center', va='center', fontsize=12)

    plt.xlabel("True Frequency")
    plt.ylabel("Matched Frequency")
    plt.title(title)

    plt.savefig(output_path)
    plt.close()


if __name__ == "__main__":
    plot_scatter(
        "results/leakage_forward_private_100000.csv",
        "results/leakage_FP_scatter.png",
        "Frequency Leakage (Forward-Private SSE)"
    )

    plot_scatter(
        "results/leakage_normal_100000.csv",
        "results/leakage_normal_scatter.png",
        "Frequency Leakage (Normal SSE)"
    )