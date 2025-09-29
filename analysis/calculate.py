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
    parser.add_argument('-r','--results-dir',type=str, default='results/multi_threaded', help='results directory root (e.g. results/multi_threaded or results/single_threaded)')
    parser.add_argument('-met', '--metrics', type=str, nargs='+', help='List of metrics to calculate')
    parser.add_argument('-p', '--precision', type=int, default=0, help='Digits after the decimal point')
    args = parser.parse_args()

    metrics = {'run_time': 'seconds-elapsed', 'memory_consumption': 'max-resident-memory-kb'}

    # Load benchmark and malloc lists
    with open(args.benchmarks) as f:
        benchmarks = sorted([line.strip() for line in f if line.strip()])
    with open(args.mallocs) as f:
        mallocs = [line.strip() for line in f if line.strip()]

        # Build DataFrame columns (add iterations column)
        columns_label = ['benchmark', 'iterations']
        for malloc in mallocs:
            for metric in args.metrics:
                columns_label.append(f"{malloc}_{metric}_mean")
                columns_label.append(f"{malloc}_{metric}_median")
                columns_label.append(f"{malloc}_{metric}_mad_pct")
        res_df = pd.DataFrame(columns=columns_label)

    for benchmark in benchmarks:
        # reserve slot for iterations (filled after scanning all repeats/mallocs)
        results = [benchmark, None]
        iterations_set = set()

        # base results directory (user-controlled)
        results_root = args.results_dir.rstrip('/')

        for malloc in mallocs:
            paths = glob.glob(f'{results_root}/{malloc}/{benchmark}/repeat*/time.csv')
            time_dfs = []
            for p in paths:
                try:
                    df = pd.read_csv(p)
                    time_dfs.append(df)

                    # explicit "iterations" column handling (fallback to 1)
                    if 'iterations' in df.columns:
                        try:
                            iter_val = int(df['iterations'].iloc[0])
                        except Exception:
                            try:
                                iter_val = int(float(df['iterations'].iloc[0]))
                            except Exception:
                                iter_val = 1
                    else:
                        iter_val = 1
                    iterations_set.add(iter_val)

                except EmptyDataError:
                    print(f"Warning: Empty CSV file (no columns to parse): {p}", file=sys.stderr)
                except Exception as e:
                    print(f"Error reading {p}: {e}", file=sys.stderr)

            if not time_dfs:
                print(f"Warning: No valid time.csv files for {malloc}/{benchmark}", file=sys.stderr)
                # append three placeholders per metric (mean, median, mad_pct)
                results.extend([None, None, None] * len(args.metrics))
            else:
                for metric in args.metrics:
                    try:
                        metric_vals = [df[metrics[metric]].iloc[0] for df in time_dfs]
                        mean_val = np.mean(metric_vals)
                        median_val = np.median(metric_vals)
                        mean_abs_dev = np.mean(np.abs(metric_vals - mean_val))  # Mean absolute deviation
                        mad_pct = 0.0 if mean_val == 0 else (mean_abs_dev / mean_val) * 100.0
                        results.extend([mean_val, median_val, mad_pct])
                    except Exception as e:
                        print(f"Missing {metric} in {malloc}/{benchmark}: {e}", file=sys.stderr)
                        # append three placeholders for this metric
                        results.extend([None, None, None])

        # determine iterations value for this benchmark and warn on inconsistencies
        if not iterations_set:
            iterations_val = None
        elif len(iterations_set) == 1:
            iterations_val = next(iter(iterations_set))
        else:
            iterations_val = max(iterations_set)
            print(f"Warning: inconsistent iterations for benchmark {benchmark}: found {sorted(iterations_set)}; using {iterations_val}", file=sys.stderr)

        results[1] = iterations_val
        res_df.loc[len(res_df)] = results

    res_df.to_csv(sys.stdout, index=False, float_format=f"%.{args.precision}f")
