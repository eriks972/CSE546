import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("results/leakage_forward_private_100000.csv")

# ---- Handle edge cases ----
if len(df) > 1 and df["matched_freq"].std() > 0:
    corr = np.corrcoef(df["true_freq"], df["matched_freq"])[0, 1]
else:
    corr = 0.0

print("Correlation (Forward-Private SSE):", corr)

plt.figure()

# Scatter plot
if len(df) > 0:
    plt.scatter(df["true_freq"], df["matched_freq"], alpha=0.5)

    max_val = max(df["true_freq"])

    # Ideal diagonal line
    plt.plot([0, max_val], [0, max_val], 'r--')

    # Add correlation text
    plt.text(
        0.05 * max_val,
        0.9 * max_val,
        f"Correlation = {corr:.3f}",
        fontsize=12,
        bbox=dict(facecolor='white', alpha=0.7)
    )

else:
    # Empty dataset case
    plt.text(0.5, 0.5, "No data (No leakage detected)", 
             ha='center', va='center', fontsize=12)

plt.xlabel("True Frequency")
plt.ylabel("Matched Frequency")
plt.title("Frequency Leakage (Forward-Private SSE)")

plt.savefig("results/leakage_FP_scatter.png")
plt.close()