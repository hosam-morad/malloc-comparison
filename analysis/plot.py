#!/usr/bin/env python3

import sys
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import re
import math

# Constants
BENCHMARK_COL = 'benchmark'
GLIBC_NAME = 'ptmalloc2'
SUBPLOTS_PER_FIGURE = 12  # 3x4 layout
NROWS, NCOLS = 3, 4

def parse_columns(columns):
    """
    Parse the columns to identify (malloc, metric) pairs.
    Returns: metric -> list of (malloc, column name)
    """
    colmap = {}
    for col in columns:
        if col == BENCHMARK_COL:
            continue
        match = re.match(r'([^_]+)_(.+)', col)
        if not match:
            continue
        malloc, metric = match.groups()
        colmap.setdefault(metric, []).append((malloc, col))
    return colmap

def prepare_precent_differences(df, malloc_columns):
    """
    Prepare a DataFrame with percent differences relative to glibc.
    Returns: DataFrame with benchmarks as index and mallocs as columns.
    """
    df = df.set_index(BENCHMARK_COL)
    percent_diffs = {}
    for malloc, col in malloc_columns:
        percent_diffs[malloc] = df[col]

    # Create a new DataFrame with benchmarks as index
    result_df = pd.DataFrame(percent_diffs)
    
    # Compute percent differences relative to glibc
    glibc_col = result_df[GLIBC_NAME]
    for malloc in result_df.columns:
        if malloc != GLIBC_NAME:
            result_df[malloc] = 100 * (result_df[malloc] / glibc_col - 1.0)
    
    return result_df

def plot_metric(df, metric, malloc_columns, output):
    """
    Generate a single PDF with subplots showing relative % difference to glibc.
    """
    df.dropna(inplace=True)
    num_benchmarks = len(df)
    differences = prepare_precent_differences(df, malloc_columns)
    num_mallocs = len(differences.columns)
    benchmarks = differences.index.tolist()
    mallocs = [m for m in differences.columns if m != GLIBC_NAME]

    all_values = pd.concat([differences[m] for m in mallocs])
    y_min = min(-10, all_values.min() - 10)
    y_max = max(10, all_values.max() + 10)

    with PdfPages(output) as pdf:
        for malloc in mallocs:
            plt.figure(figsize=(10, 6))
            y = differences[malloc]
            y_sorted = y.sort_values(ascending=False)
            plt.bar(y_sorted.index, y_sorted, color='skyblue')
            plt.axhline(0, color='gray', linestyle='--', linewidth=1)
            plt.title(f"{malloc}: % Difference vs {GLIBC_NAME} ({metric})")
            plt.xlabel("Benchmark")
            plt.ylabel("Percent Difference (%)")
            plt.xticks(rotation=45, ha='right', fontsize=8)
            plt.tight_layout()
            plt.ylim(y_min, y_max)
            pdf.savefig()
            plt.close()
  
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot a single metric across benchmarks.')
    parser.add_argument('-o', '--output', type=str, required=True, help='PDF file')
    parser.add_argument('-m', '--metric', required=True, help='Metric name to plot')
    args = parser.parse_args()
    df = pd.read_csv(sys.stdin)
    colmap = parse_columns(df.columns)

    if args.metric not in colmap:
        print(f"Error: Metric '{args.metric}' not found in CSV headers.", file=sys.stderr)
        print(f"Available metrics: {list(colmap.keys())}", file=sys.stderr)
        sys.exit(1)

    malloc_columns = colmap[args.metric]
    plot_metric(df, args.metric, malloc_columns, args.output)