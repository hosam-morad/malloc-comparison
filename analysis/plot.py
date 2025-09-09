#!/usr/bin/env python3

import sys
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import re
import math
from pathlib import Path

# Constants
BENCHMARK_COL = 'benchmark'
GLIBC_NAME = 'ptmalloc2'
DL_NAME = "dlmalloc"
MI_NAME = "mimalloc"
THINGS_TO_COMPARE=['mean','median','mad']


def parse_columns(columns, things_to_compare=None):
    """
    Build:
      {
        thing_1: [(malloc, col), ...],
        thing_2: [(malloc, col), ...],
        ...
      }
    where each 'thing' comes from THINGS_TO_COMPARE (e.g., mean/median/mad),
    matched by column suffix: "<malloc>_<...>_<thing>" OR "<malloc>_<thing>".
    """
    suffixes = things_to_compare if things_to_compare is not None else THINGS_TO_COMPARE
    out = {thing: [] for thing in suffixes}

    for col in columns:
        if col == BENCHMARK_COL:
            continue
        m = re.match(r'^([^_]+)_(.+)$', col)
        if not m:
            continue
        malloc, rest = m.groups()

        # attach the column to the first matching thing (in the given order)
        for thing in suffixes:
            if rest == thing or rest.endswith(f"_{thing}"):
                out[thing].append((malloc, col))
                break  # stop at first match to avoid double-counting

    for thing in out:
        out[thing].sort(key=lambda t: t[0])

    return out



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
            x = np.arange(len(mallocs))
            bar_width = 0.2
            axes[i].bar(x, diffs, width=bar_width, color=plt.cm.tab10.colors[:len(mallocs)])
            axes[i].set_xticks(x)
            axes[i].set_xticklabels(mallocs, rotation=45)

            # Adjust x-limits only when needed
            if len(mallocs) == 1:
                axes[i].set_xlim(-0.5, 0.5)
            else:
                axes[i].set_xlim(-0.5, len(mallocs) - 0.5)

            axes[i].axhline(0, color='black', linestyle='--', linewidth=0.8)
            axes[i].set_title(benchmark)
            axes[i].tick_params(axis='x', rotation=45)
            
            # Only show ylabel on leftmost subplots
            if i % NCOLS == 0:
                axes[i].set_ylabel(f'relative {metric} to glibc [%]')
            else:
                axes[i].set_ylabel("")

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

    # Read CSV
    if args.input == "-" or args.input == "":
        df = pd.read_csv(sys.stdin)
    else:
        df = pd.read_csv(args.input)

    # Parse and compute diffs
    colmap = parse_columns(df.columns, THINGS_TO_COMPARE)
    diffs_by_thing = prepare_precent_differences(df, colmap, THINGS_TO_COMPARE, eps_factor=args.eps_factor, eps_floor=args.eps_floor)

    # Export csvs
    if args.csv_dir:
        export_diffs_to_csvs(diffs_by_thing, args.csv_dir, float_precision=args.float_precision)
    # Plot
    plot_ranked_percent_diffs(diffs_by_thing, args.output)

if __name__ == "__main__":
    main()
