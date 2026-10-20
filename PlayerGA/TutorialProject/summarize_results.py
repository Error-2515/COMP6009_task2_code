"""
Summarise the CoinTex experiment results for the COMP6009 Lab 2 report.

Usage (run it in the folder that contains results.csv):
    pip install pandas matplotlib
    python summarize_results.py

With no arguments it merges every results*.csv in the current folder. That also combines your
group members' files: rename them results_alice.csv, results_bob.csv, ... and put them in one folder.
You can also pass file names:  python summarize_results.py results.csv other.csv

Outputs: summary.csv (the table for the report) and success_rate.png, remaining_life.png, time_to_win.png.
"""
import glob
import sys

import pandas as pd

files = sys.argv[1:] or sorted(glob.glob("results*.csv"))
if not files:
    sys.exit("No results*.csv found in this folder.")

df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
print("Merged", len(df), "runs from", files)

df["win"] = (df["outcome"] == "win").astype(int)
df["survived"] = (df["outcome"] != "dead").astype(int)     # timeout counts as survived, death does not
df["coins_pct"] = df["coins_collected"] / df["coins_total"] * 100   # share of the level's coins collected in each run

keys = ["config", "level"]
g = df.groupby(keys)
summary = g.agg(runs=("win", "size"),
                wins=("win", "sum"),
                success_rate=("win", "mean"),
                survival_rate=("survived", "mean"),
                mean_coins=("coins_collected", "mean"),
                mean_coins_pct=("coins_pct", "mean"),
                mean_life_pct=("remaining_life_pct", "mean"),
                mean_generations=("generations", "mean")).round(2)
summary["mean_time_wins_s"] = df[df["win"] == 1].groupby(keys)["time_s"].mean().round(2)   # blank if no wins
summary["mean_time_all_s"] = g["time_s"].mean().round(2)                                     # includes timeouts/deaths

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)
print(summary)
summary.to_csv("summary.csv")
print("Saved summary.csv")

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    for col, label, fname in [("success_rate", "Success rate", "success_rate.png"),
                              ("mean_coins_pct", "Mean coins collected (%)", "coins_collected.png"),
                              ("mean_life_pct", "Mean remaining life (%)", "remaining_life.png"),
                              ("mean_time_wins_s", "Mean time to win (s)", "time_to_win.png")]:
        ax = summary[col].unstack("level").plot.bar()
        ax.set_ylabel(label)
        ax.set_xlabel("Configuration")
        ax.legend(title="Level")
        ax.figure.tight_layout()
        ax.figure.savefig(fname, dpi=200)
        plt.close(ax.figure)
        print("Saved", fname)
except ImportError:
    print("matplotlib is not installed, so no plots were made (pip install matplotlib).")
