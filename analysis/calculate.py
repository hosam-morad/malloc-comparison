#!/usr/bin/env python3

import argparse
import pandas as pd
import numpy as np
import sys, glob
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

    # Build DataFrame columns
    columns_label = ['benchmark']
    for malloc in mallocs:
        for metric in args.metrics:
            columns_label.append(f"{malloc}_{metric}_mean")
            columns_label.append(f"{malloc}_{metric}_median")
            columns_label.append(f"{malloc}_{metric}_mad")
    res_df = pd.DataFrame(columns=columns_label)

    for benchmark in benchmarks:
        results = [benchmark]
        for malloc in mallocs:
            paths = glob.glob(f'results/{malloc}/{benchmark}/repeat*/time.csv')
            time_dfs = []
            for p in paths:
                try:
                    df = pd.read_csv(p)
                    time_dfs.append(df)
                except EmptyDataError:
                    print(f"Warning: Empty CSV file (no columns to parse): {p}", file=sys.stderr)
                except Exception as e:
                    print(f"Error reading {p}: {e}", file=sys.stderr)

            if not time_dfs:
                print(f"Warning: No valid time.csv files for {malloc}/{benchmark}", file=sys.stderr)
                results.extend([None] * len(args.metrics))
            else:
                for metric in args.metrics:
                    try:
                        metric_vals = [df[metrics[metric]].iloc[0] for df in time_dfs]
                        mean_val = np.mean(metric_vals)
                        median_val = np.median(metric_vals)
                        mad_val = np.mean(np.abs(metric_vals - mean_val))  # Mean absolute deviation
                        results.extend([mean_val, median_val, mad_val])
                    except Exception as e:
                        print(f"Missing {metric} in {malloc}/{benchmark}: {e}", file=sys.stderr)
                        results.append(None)
                        
        res_df.loc[len(res_df)] = results

    res_df.to_csv(sys.stdout, index=False, float_format=f"%.{args.precision}f")
