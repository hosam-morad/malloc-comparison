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

def plot_metric(df, metric, malloc_columns, output):
    """
    Generate a single PDF with subplots showing relative % difference to glibc.
    """
    pdf = PdfPages(output)
    num_benchmarks = len(df)
    num_figures = math.ceil(num_benchmarks / SUBPLOTS_PER_FIGURE)

    for fig_idx in range(num_figures):
        fig, axes = plt.subplots(NROWS, NCOLS, figsize=(16, 10))
        axes = axes.flatten()

        for i in range(SUBPLOTS_PER_FIGURE):
            row_idx = fig_idx * SUBPLOTS_PER_FIGURE + i
            if row_idx >= num_benchmarks:
                axes[i].axis('off')
                continue

            row = df.iloc[row_idx]
            benchmark = row[BENCHMARK_COL]

            values = {}
            glibc_val = None
            for malloc, col in malloc_columns:
                val = row[col]
                if pd.isna(val):
                    continue
                values[malloc] = val
                if malloc == GLIBC_NAME:
                    glibc_val = val

            if glibc_val is None or glibc_val == 0:
                axes[i].set_title(f"{benchmark} (glibc missing/zero)")
                axes[i].axis('off')
                continue

            # Compute percent difference to glibc
            percent_diffs = {
                m: 100 * (v / glibc_val - 1.0)
                for m, v in values.items() if m != GLIBC_NAME
            }

            mallocs = list(percent_diffs.keys())
            diffs = [percent_diffs[m] for m in mallocs]

            axes[i].bar(mallocs, diffs, color=plt.cm.tab10.colors[:len(mallocs)])
            axes[i].axhline(0, color='black', linestyle='--', linewidth=0.8)
            axes[i].set_title(benchmark)
            axes[i].tick_params(axis='x', rotation=45)
            axes[i].set_ylabel(f'relative {metric} to glibc [%]')
            axes[i].grid(True, linestyle=':', linewidth=0.5)

        plt.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

    pdf.close()

    
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