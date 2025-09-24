#!/usr/bin/env python3

import argparse
import pandas as pd
import numpy as np
import sys, glob
import os
from pandas.errors import EmptyDataError

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--benchmarks', type=str, help='text file containing the list of benchmarks')
    parser.add_argument('-m', '--mallocs', type=str, help='text file containing the list of malloc implementations')
    parser.add_argument('-met', '--metrics', type=str, nargs='+', help='List of metrics to calculate')
    parser.add_argument('-p', '--precision', type=int, default=0, help='Digits after the decimal point')
    args = parser.parse_args()

    metrics = {'run_time': 'seconds-elapsed', 'memory_consumption': 'max-resident-memory-kb'}

    # Load benchmark and malloc lists
    with open(args.benchmarks) as f:
        benchmarks = sorted([line.strip() for line in f if line.strip()])
    with open(args.mallocs) as f:
        mallocs = [line.strip() for line in f if line.strip()]

    # Discover repeat directories by scanning results tree. We look for the first
    # malloc/benchmark that exists and collect subdirs starting with 'repeat'.
    repeats = []
    for m in mallocs:
        found_repeats = []
        for b in benchmarks:
            base = os.path.join('results', m, b)
            if os.path.isdir(base):
                try:
                    found = sorted([d for d in os.listdir(base) if d.startswith('repeat') and os.path.isdir(os.path.join(base, d))])
                except Exception:
                    found = []
                if found:
                    found_repeats = found
                    break
        if found_repeats:
            repeats = found_repeats
            break
    # Fallback default repeats if none discovered
    if not repeats:
        repeats = ['repeat1', 'repeat2', 'repeat3']

    # Build DataFrame columns: first column is identifier 'benchmark-malloc', then one
    # column per repeat per metric (e.g. repeat1_run_time)
    columns_label = ['benchmark_malloc']
    for r in repeats:
        for metric in args.metrics:
            columns_label.append(f"{r}_{metric}")
    res_df = pd.DataFrame(columns=columns_label)

    # Populate rows: one row per (benchmark, malloc) pair
    for benchmark in benchmarks:
        for malloc in mallocs:
            row_id = f"{benchmark}-{malloc}"
            results = [row_id]
            for r in repeats:
                time_csv = os.path.join('results', malloc, benchmark, r, 'time.csv')
                if not os.path.exists(time_csv):
                    # missing repeat folder or file; append empty values for each metric
                    results.extend([None] * len(args.metrics))
                    continue
                try:
                    df = pd.read_csv(time_csv)
                except EmptyDataError:
                    print(f"Warning: Empty CSV file (no columns to parse): {time_csv}", file=sys.stderr)
                    results.extend([None] * len(args.metrics))
                    continue
                except Exception as e:
                    print(f"Error reading {time_csv}: {e}", file=sys.stderr)
                    results.extend([None] * len(args.metrics))
                    continue

                for metric in args.metrics:
                    col = metrics.get(metric)
                    if col is None:
                        # Unknown metric requested; append None
                        results.append(None)
                        continue
                    try:
                        val = df[col].iloc[0]
                        results.append(val)
                    except Exception:
                        results.append(None)

            # append row
            res_df.loc[len(res_df)] = results

    # Output CSV
    res_df.to_csv(sys.stdout, index=False, float_format=f"%.{args.precision}f")
