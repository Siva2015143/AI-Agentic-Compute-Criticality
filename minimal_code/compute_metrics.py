#!/usr/bin/env python3
"""
Compute metrics for Agentic Compute Chain experiment.

Place this file at project root as: analysis/compute_metrics.py
Run: python analysis/compute_metrics.py

Produces:
 - results/summary_metrics.csv
 - results/plots/{variant}_*.png
 - results/per_trial_metrics.csv

Small changes in agent instructions cause a phase-like jump in compute: 
      permissive prompts let the agent spawn helper calls and the total compute per task can multiply by tens to thousands 
      — we measured this empirically, quantified it, and built diagnostics to detect it early.

"""

import os
import json
import glob
import math
import statistics
import random
from collections import defaultdict, Counter
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# -----------------------
# CONFIG
# -----------------------
RAW_LOGS_DIR = "analysis/raw_logs"
RESULTS_DIR = "results"
PLOTS_DIR = os.path.join(RESULTS_DIR, "plots")
BOOTSTRAP_SAMPLES = 2000
RANDOM_SEED = 42

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# -----------------------
# HELPERS
# -----------------------
def read_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception as e:
                # try to fix single quotes
                try:
                    rows.append(json.loads(line.replace("'", '"')))
                except Exception:
                    print("WARN: failed to parse line in", path, "->", e)
    return rows

def detect_variant_from_filename(fn):
    # expecting names like P0_xxx.jsonl or P3_xxx.jsonl
    bn = os.path.basename(fn)
    for prefix in ["P0","P1","P2","P3","P4","P5","P6"]:
        if bn.startswith(prefix + "_") or bn.startswith(prefix + "-") or bn.startswith(prefix + "."):
            return prefix
    # fallback: if contains 'P' followed by digit
    import re
    m = re.search(r"(P[0-6])", bn)
    if m:
        return m.group(1)
    return "UNKNOWN"

# -----------------------
# LOAD ALL TRIALS
# -----------------------
all_files = sorted(glob.glob(os.path.join(RAW_LOGS_DIR, "**", "*.jsonl"), recursive=True))
print(f"Found {len(all_files)} jsonl trial files under {RAW_LOGS_DIR}")

trials = []  # each item: dict with keys: path, variant, calls(list)
for path in all_files:
    rows = read_jsonl(path)
    if len(rows) == 0:
        continue
    variant = detect_variant_from_filename(path)
    trials.append({
        "path": path,
        "variant": variant,
        "calls": rows
    })

if len(trials) == 0:
    raise SystemExit("No trials found. Check RAW_LOGS_DIR and files.")

# -----------------------
# PER-TRIAL METRICS
# -----------------------
per_trial = []
# We'll also collect call-level DataFrame for child counting
call_rows = []

for t in trials:
    path = t["path"]
    variant = t["variant"]
    calls = t["calls"]
    # Ensure call_id and parent_id canonical types
    # Each trial we assume call_id's are unique within file
    total_GFLOPs = 0.0
    total_tokens = 0
    for c in calls:
        # tolerant names
        gf = None
        for k in ("GFLOPs","est_GFLOPs","gflops","gfloPs"):
            if k in c:
                gf = c[k]
                break
        if gf is None:
            # try to compute from tokens (if tokens exist) -- but we prefer GFLOPs present
            gf = 0.0
        try:
            total_GFLOPs += float(gf)
        except Exception:
            # if it's string with commas, etc.
            try:
                total_GFLOPs += float(str(gf).replace(",",""))
            except Exception:
                total_GFLOPs += 0.0

        tokens_in = c.get("tokens_in") or c.get("tokensIn") or 0
        tokens_out = c.get("tokens_out") or c.get("tokensOut") or c.get("tokens_out_count") or 0
        try:
            total_tokens += int(tokens_in) + int(tokens_out)
        except Exception:
            pass

        call_id = c.get("call_id") or c.get("id") or c.get("callId")
        parent_id = c.get("parent_id") or c.get("parentId") or c.get("parent") or None
        # store call-row for global analysis
        call_rows.append({
            "trial_path": path,
            "variant": variant,
            "call_id": call_id,
            "parent_id": parent_id,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "GFLOPs": float(gf) if gf is not None else 0.0,
            "latency": c.get("latency", None)
        })

    T = len(calls)
    per_trial.append({
        "trial_path": path,
        "variant": variant,
        "total_calls": T,
        "total_GFLOPs": total_GFLOPs,
        "total_tokens": total_tokens
    })

df_trials = pd.DataFrame(per_trial)
df_calls = pd.DataFrame(call_rows)

# -----------------------
# Baseline F0: use mean total_GFLOPs across P0 trials
# -----------------------
p0_rows = df_trials[df_trials["variant"] == "P0"]
if len(p0_rows) == 0:
    print("WARN: no P0 baseline trials found. Using global median total_GFLOPs as baseline.")
    F0 = float(df_trials["total_GFLOPs"].median())
else:
    F0 = float(p0_rows["total_GFLOPs"].mean())

print(f"Baseline F0 (mean P0 total GFLOPs): {F0:.3f}")

# Add amplification A to df_trials
df_trials["amplification"] = df_trials["total_GFLOPs"] / (F0 if F0>0 else 1.0)

# -----------------------
# Offspring stats: compute child counts per call within each trial (call_id matching)
# -----------------------
# We'll compute child counts per call by grouping parent_id values inside each trial
def compute_child_counts_for_trial(trial_path, calls_df):
    sub = calls_df[calls_df["trial_path"] == trial_path]
    # use raw values (they could be numbers or strings)
    call_ids = sub["call_id"].tolist()
    # count how many times each call_id appears as parent_id
    parent_counts = Counter(sub["parent_id"].tolist())
    # For calls that never appear as parent -> 0 children
    counts = []
    for cid in call_ids:
        counts.append(parent_counts.get(cid, 0))
    return counts

# compute per-call child_counts and b_hat per trial
trial_offspring = []
all_child_counts = []  # global list of all call child counts (for variant bootstrap)
for idx, row in df_trials.iterrows():
    tp = row["trial_path"]
    counts = compute_child_counts_for_trial(tp, df_calls)
    if len(counts) == 0:
        b_hat = 0.0
    else:
        b_hat = float(np.mean(counts))
    trial_offspring.append({
        "trial_path": tp,
        "variant": row["variant"],
        "b_hat_trial": b_hat,
        "num_calls": row["total_calls"]
    })
    # store counts with trial id
    for c in counts:
        all_child_counts.append({
            "trial_path": tp,
            "variant": row["variant"],
            "child_count": int(c)
        })

df_offspring = pd.DataFrame(trial_offspring)
df_child_counts = pd.DataFrame(all_child_counts)

# -----------------------
# Variant-level aggregation & bootstrap CIs for b_hat (resample calls)
# -----------------------
variants = sorted(df_trials["variant"].unique())

summary_rows = []
for var in variants:
    var_trials = df_trials[df_trials["variant"] == var]
    var_count = len(var_trials)
    mean_GF = var_trials["total_GFLOPs"].mean() if var_count>0 else 0.0
    median_GF = var_trials["total_GFLOPs"].median() if var_count>0 else 0.0
    mean_T = var_trials["total_calls"].mean() if var_count>0 else 0.0
    median_T = var_trials["total_calls"].median() if var_count>0 else 0.0
    amp = var_trials["amplification"].median() if var_count>0 else 0.0

    # collect child counts across this variant
    cc = df_child_counts[df_child_counts["variant"] == var]["child_count"].values
    if len(cc) == 0:
        b_hat = 0.0
        ci_low, ci_high = 0.0, 0.0
    else:
        b_hat = float(np.mean(cc))
        # bootstrap on call-level counts
        boot_means = []
        for _ in range(BOOTSTRAP_SAMPLES):
            sample = np.random.choice(cc, size=len(cc), replace=True)
            boot_means.append(np.mean(sample))
        ci_low, ci_high = np.percentile(boot_means, [2.5, 97.5])

    summary_rows.append({
        "variant": var,
        "n_trials": var_count,
        "mean_total_GFLOPs": float(mean_GF),
        "median_total_GFLOPs": float(median_GF),
        "mean_T": float(mean_T),
        "median_T": float(median_T),
        "median_amplification": float(amp),
        "b_hat_calls_mean": float(b_hat),
        "b_hat_ci_low": float(ci_low),
        "b_hat_ci_high": float(ci_high)
    })

df_summary = pd.DataFrame(summary_rows).sort_values("variant")
summary_csv_path = os.path.join(RESULTS_DIR, "summary_metrics.csv")
df_summary.to_csv(summary_csv_path, index=False)
print("Wrote summary ->", summary_csv_path)

per_trial_csv = os.path.join(RESULTS_DIR, "per_trial_metrics.csv")
df_trials.to_csv(per_trial_csv, index=False)
print("Wrote per-trial metrics ->", per_trial_csv)

# -----------------------
# PLOTS
# -----------------------
# 1) b_hat with CI
plt.figure(figsize=(8,4))
xs = df_summary["variant"].tolist()
ys = df_summary["b_hat_calls_mean"].tolist()
err_low = df_summary["b_hat_calls_mean"] - df_summary["b_hat_ci_low"]
err_high = df_summary["b_hat_ci_high"] - df_summary["b_hat_calls_mean"]
plt.errorbar(xs, ys, yerr=[err_low, err_high], fmt='o-', capsize=6)
plt.axhline(1.0, color="red", linestyle="--", label="b = 1 (critical)")
plt.xlabel("Variant")
plt.ylabel("b_hat (mean children per call)")
plt.title("Estimated offspring mean b by variant (with bootstrap 95% CI)")
plt.grid(True, alpha=0.2)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "b_hat_by_variant.png"), dpi=150)
plt.close()

# 2) amplification median per variant (bar)
plt.figure(figsize=(8,4))
xs = df_summary["variant"].tolist()
ys = df_summary["median_amplification"].tolist()
plt.bar(xs, ys)
plt.xlabel("Variant")
plt.ylabel("Median amplification A (F_total / F0)")
plt.title("Median amplification by variant")
plt.grid(axis='y', alpha=0.2)
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "amplification_by_variant.png"), dpi=150)
plt.close()

# 3) Scatter of b_hat vs median amplification
plt.figure(figsize=(6,5))
plt.scatter(df_summary["b_hat_calls_mean"], df_summary["median_amplification"])
for i, row in df_summary.iterrows():
    plt.text(row["b_hat_calls_mean"], row["median_amplification"], row["variant"])
plt.xscale('linear')
plt.yscale('log')
plt.xlabel("b_hat (mean children per call)")
plt.ylabel("Median amplification (log scale)")
plt.title("b_hat vs amplification")
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "b_vs_amplification.png"), dpi=150)
plt.close()

# 4) CCDF of total_calls per trial per variant (log-log)
plt.figure(figsize=(7,5))
for var in variants:
    vals = df_trials[df_trials["variant"]==var]["total_calls"].values
    if len(vals)==0:
        continue
    vals_sorted = np.sort(vals)
    ccdf = 1.0 - np.arange(1, len(vals_sorted)+1)/len(vals_sorted)
    plt.step(vals_sorted, ccdf, where='post', label=var)
plt.xscale('log')
plt.yscale('log')
plt.xlabel("Total calls (T)")
plt.ylabel("CCDF P(T >= t)")
plt.title("CCDF of total calls per trial (log-log)")
plt.legend()
plt.grid(True, alpha=0.2)
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "ccdf_total_calls.png"), dpi=150)
plt.close()

print("Saved plots to", PLOTS_DIR)

# -----------------------
# PRINT KEY NUMBERS (console summary)
# -----------------------
print("\n=== VARIANT SUMMARY (console) ===")
print(df_summary.to_string(index=False))

print("\n=== SAMPLE per-trial metrics (first 100) ===")
print(df_trials.head(100).to_string(index=False))

print("\nDone.")
