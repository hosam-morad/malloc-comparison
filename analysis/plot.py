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
THINGS_TO_COMPARE=['mean','median','mad_pct']
PARSE_SUFFIXES    = ['mean', 'median', 'mad_pct']
# Plot scale tuning
SYMLOG_LINTHRESH = 5.0   # half-width (in %) of the linear region around 0
SYMLOG_LINSCALE  = 1.0   # visual scaling of that linear region


def parse_columns(columns, things_to_compare=None):
    """
    Build:
      {
        thing_1: [(malloc, col), ...],
        thing_2: [(malloc, col), ...],
        ...
      }
    where each 'thing' comes from THINGS_TO_COMPARE (e.g., mean/median/mad_pct),
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



def prepare_precent_differences(df, colmap, things_to_compare=None, eps_factor=0.5, eps_floor=None):
    """
    Compute % differences vs GLIBC_NAME for each 'thing', using an epsilon
    when baseline is 0 or NaN (no row filtering).

    epsilon policy (per row):
      epsilon_row = eps_factor * min_positive_value_in_row_across_mallocs
      fallback to eps_floor (or machine epsilon) if no positive values exist.

    Args:
        df: DataFrame with BENCHMARK_COL and <malloc>_<...> headers.
        colmap: dict from parse_columns(...): {thing: [(malloc, col), ...], ...}
        things_to_compare: iterable; defaults to THINGS_TO_COMPARE.
        eps_factor: multiplier for row-wise epsilon (default 0.5).
        eps_floor: optional absolute floor for epsilon (default: float eps).

    Returns:
        Dict[str, pandas.DataFrame] (baseline column excluded).
    """
    suffixes = things_to_compare if things_to_compare is not None else THINGS_TO_COMPARE
    if BENCHMARK_COL not in df.columns:
        raise ValueError(f"Missing required column '{BENCHMARK_COL}'.")
    work = df.set_index(BENCHMARK_COL, drop=True)

    global_floor = (np.finfo(float).eps if eps_floor is None else float(eps_floor))
    out = {}

    for thing in suffixes:
        pairs = colmap.get(thing, [])
        if not pairs:
            continue

        cols_by_malloc = {m: c for (m, c) in pairs}
        if GLIBC_NAME not in cols_by_malloc:
            raise ValueError(
                f"Baseline '{GLIBC_NAME}' not found for '{thing}'. "
                f"Available mallocs: {sorted(cols_by_malloc.keys())}"
            )

        # All malloc values for this 'thing'
        vals_df = pd.DataFrame({m: work[c] for (m, c) in pairs}, index=work.index)

        # Row-wise epsilon: half of the smallest positive value in the row (across mallocs)
        row_min_pos = vals_df.where(vals_df > 0).min(axis=1)  # NaN if no positive values in row
        eps_series = (row_min_pos * eps_factor).fillna(global_floor)

        # Baseline with epsilon substituted where 0 or NaN
        baseline_series = work[cols_by_malloc[GLIBC_NAME]]
        base = baseline_series.where(baseline_series.notna() & (baseline_series != 0), eps_series)

        # % diff vs baseline
        diffs = 100.0 * (vals_df.div(base, axis=0) - 1.0)

        # Drop baseline column from output, keep original order otherwise
        ordered_cols = [m for (m, _) in pairs if m != GLIBC_NAME]
        if not ordered_cols:
            continue
        diffs = diffs.reindex(columns=ordered_cols)

        out[thing] = diffs

    return out

def export_diffs_to_csvs(diffs_by_thing, out_dir, float_precision=6):
    """
    Write four CSV files (one per figure) into out_dir:
      - mean.csv        : columns [benchmark, dlmalloc, mimalloc] from diffs_by_thing['mean']
      - median.csv      : columns [benchmark, dlmalloc, mimalloc] from diffs_by_thing['median']
      - mad_pct.csv         : columns [benchmark, dlmalloc, mimalloc] from diffs_by_thing['mad_pct']
      - abs_median.csv  : abs of diffs_by_thing['median'] with same columns
    If a thing is missing, its file is skipped.
    """
    out_path = Path(out_dir)

    def _write_csv(filename, df):
        if df is None or df.empty:
            return
        cols = [c for c in [DL_NAME, MI_NAME] if c in df.columns]
        if not cols:
            cols = list(df.columns)
        out_df = df[cols].copy()
        out_df.insert(0, BENCHMARK_COL, df.index)
        out_df.to_csv(out_path / filename, index=False, float_format=f"%.{float_precision}f")

    _write_csv("mean.csv",   diffs_by_thing.get("mean"))
    _write_csv("median.csv", diffs_by_thing.get("median"))
    _write_csv("mad_pct.csv",    diffs_by_thing.get("mad_pct"))

    med = diffs_by_thing.get("median")
    if med is not None and not med.empty:
        _write_csv("abs_median.csv", med.abs())

# ---------------- Diff computation (epsilon) ----------------
def plot_ranked_percent_diffs(diffs_by_thing, output_pdf, mad_pctpct_by_thing=None):
    """
    Create 4 figures into one PDF.
    On the MEAN panel: draw envelope lines mean±mad_pct% (two extra lines per allocator).
    """
    from matplotlib.backends.backend_pdf import PdfPages
    with PdfPages(output_pdf) as pdf:
        def _draw(metric_name, df, use_abs=False):
            if df is None or df.empty:
                return
            cols = [c for c in [DL_NAME, MI_NAME] if c in df.columns] or list(df.columns)

            fig, ax = plt.subplots(figsize=(10, 6))

            # Keep symlog only for the mean (non-abs) panel
            if metric_name == "mean" and not use_abs:
                ax.set_yscale('symlog', linthresh=SYMLOG_LINTHRESH, linscale=SYMLOG_LINSCALE)

            colors = ['tab:blue', 'tab:orange']
            mad_pct_frame = mad_pctpct_by_thing.get(metric_name) if mad_pctpct_by_thing is not None else None

            for i, col in enumerate(cols):
                color = colors[i % len(colors)]
                s = df[col].dropna()
                s_sorted = (s.abs().sort_values() if use_abs else s.sort_values())
                x = np.arange(1, len(s_sorted) + 1)
                y = s_sorted.values

                # Plot the main mean/median/mad_pct line
                ax.plot(x, y, label=col, color=color, linewidth=1.8, zorder=3)

                # For MEAN panel only, add envelope lines: mean ± mad_pct%
                if (metric_name == "mean") and (not use_abs) and (mad_pct_frame is not None) and (col in mad_pct_frame.columns):
                    # Use vertical error bars instead of upper/lower envelope lines
                    mad_pct_sorted = mad_pct_frame[col].reindex(s_sorted.index).values
                    mad_pct_sorted = np.nan_to_num(mad_pct_sorted, nan=0.0)
                    yerr = mad_pct_sorted
                    ax.errorbar(
                        x, y,
                        yerr=yerr,
                        fmt='none',            # don't draw markers (main line is drawn already)
                        ecolor=color,
                        elinewidth=1.0,
                        capsize=3,
                        alpha=0.9,
                        zorder=2
                    )

                # Horizontal mean line (same as before)
                mean_val = np.nanmean(np.abs(df[col].values)) if use_abs else np.nanmean(df[col].values)
                ax.axhline(mean_val, linestyle="--", linewidth=1, label=f"mean({col})", color=color, alpha=0.7, zorder=1)

            ax.set_xlabel("Rank (sorted per line)")
            ax.set_ylabel("Percent difference vs glibc (%)")
            ax.set_title(f"{metric_name} % diff vs glibc {'(absolute)' if use_abs else ''}".strip())
            ax.legend()
            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

        _draw("mean",   diffs_by_thing.get("mean"),   use_abs=False)  # now shows mean±mad_pct envelopes
        _draw("median", diffs_by_thing.get("median"), use_abs=False)
        _draw("mad_pct",    diffs_by_thing.get("mad_pct"),    use_abs=False)
        _draw("median", diffs_by_thing.get("median"), use_abs=True)



# ---------------- Excel export ----------------
def export_diffs_to_excels(diffs_by_thing, out_dir):
    """
    Write four Excel files (one per figure):
      - mean.xlsx       : columns [benchmark, dlmalloc, mimalloc] from diffs_by_thing['mean']
      - median.xlsx     : columns [benchmark, dlmalloc, mimalloc] from diffs_by_thing['median']
      - mad_pct.xlsx        : columns [benchmark, dlmalloc, mimalloc] from diffs_by_thing['mad_pct']
      - abs_median.xlsx : abs of diffs_by_thing['median'] with same columns
    If a thing is missing, its file is skipped.
    """
    out_dir = str(out_dir)
    def _write_excel(filename, df):
        if df is None or df.empty:
            return
        # Ensure only the mallocs present (prefer dl/mimalloc order if available)
        cols = [c for c in [DL_NAME, MI_NAME] if c in df.columns]
        if not cols:
            cols = list(df.columns)
        out_df = df[cols].copy()
        out_df.insert(0, BENCHMARK_COL, df.index)
        with pd.ExcelWriter(f"{out_dir}/{filename}", engine="xlsxwriter") as writer:
            out_df.to_excel(writer, index=False, sheet_name="diffs")

    _write_excel("mean.xlsx",   diffs_by_thing.get("mean"))
    _write_excel("median.xlsx", diffs_by_thing.get("median"))
    _write_excel("mad_pct.xlsx",    diffs_by_thing.get("mad_pct"))

    # abs median
    med = diffs_by_thing.get("median")
    if med is not None and not med.empty:
        _write_excel("abs_median.xlsx", med.abs())

# ---------------- Plotting (ranked lines) ----------------
def _rank_series(s):
    s = s.dropna()
    s_sorted = s.sort_values(ascending=True)  # no abs here
    x = np.arange(1, len(s_sorted) + 1)
    y = s_sorted.values
    return x, y

def _rank_series_abs(s):
    s = s.dropna().abs()
    s_sorted = s.sort_values(ascending=True)
    x = np.arange(1, len(s_sorted) + 1)
    y = s_sorted.values
    return x, y

def compute_yerr_from_mad_pct_in_csv(df, colmap, *_args, **_kw):
    """
    Build y-error bars for the MEAN plot using MAD% columns straight from the CSV.
    Assumes *_mad_pct columns are already in percent (e.g., 0.14 => ±0.14%).
    """
    if BENCHMARK_COL not in df.columns:
        raise ValueError(f"Missing required column '{BENCHMARK_COL}'.")
    work = df.set_index(BENCHMARK_COL, drop=True)

    pairs_mean    = colmap.get('mean', [])
    pairs_mad_pct = colmap.get('mad_pct', [])
    if not pairs_mean or not pairs_mad_pct:
        return {'mean': None}

    mad_pct_cols = {m: c for (m, c) in pairs_mad_pct}
    allocs = [m for (m, _) in pairs_mean if m != GLIBC_NAME]

    yerr = {}
    for m in allocs:
        if m in mad_pct_cols:
            s = pd.to_numeric(work[mad_pct_cols[m]], errors='coerce')
            yerr[m] = s.abs()  # non-negative whisker lengths, in % units already
        else:
            yerr[m] = pd.Series(np.nan, index=work.index)

    return {'mean': pd.DataFrame(yerr, index=work.index)}



def plot_ranked_percent_diffs(diffs_by_thing, output_pdf, mad_pctpct_by_thing=None):
    """
    Create 4 figures into one PDF.
    On the MEAN panel: draw envelope lines mean±mad_pct% (two extra lines per allocator).
    """
    from matplotlib.backends.backend_pdf import PdfPages
    with PdfPages(output_pdf) as pdf:
        def _draw(metric_name, df, use_abs=False):
            if df is None or df.empty:
                return
            cols = [c for c in [DL_NAME, MI_NAME] if c in df.columns] or list(df.columns)

            fig, ax = plt.subplots(figsize=(10, 6))

            # Keep symlog only for the mean (non-abs) panel
            if metric_name == "mean" and not use_abs:
                #ax.set_yscale('symlog', linthresh=SYMLOG_LINTHRESH, linscale=SYMLOG_LINSCALE)
                ax.set_yscale('linear')

            colors = ['tab:blue', 'tab:orange']
            mad_pct_frame = mad_pctpct_by_thing.get(metric_name) if mad_pctpct_by_thing is not None else None

            for i, col in enumerate(cols):
                color = colors[i % len(colors)]
                s = df[col].dropna()
                s_sorted = (s.abs().sort_values() if use_abs else s.sort_values())
                x = np.arange(1, len(s_sorted) + 1)
                y = s_sorted.values

                # Plot the main mean/median/mad_pct line
                ax.plot(x, y, label=col, color=color, linewidth=1.8, zorder=3)

                # For MEAN panel only, add envelope lines: mean ± mad_pct%
                if (metric_name == "mean") and (not use_abs) and (mad_pct_frame is not None) and (col in mad_pct_frame.columns):
                    mad_pct_sorted = mad_pct_frame[col].reindex(s_sorted.index).values
                    mad_pct_sorted = np.nan_to_num(mad_pct_sorted, nan=0.0)
                    yerr = mad_pct_sorted
                    ax.errorbar(
                        x, y,
                        yerr=yerr,
                        fmt='none',
                        ecolor=color,
                        elinewidth=1.0,
                        capsize=3,
                        alpha=0.9,
                        zorder=2
                    )

                # Horizontal mean line (same as before)
                mean_val = np.nanmean(np.abs(df[col].values)) if use_abs else np.nanmean(df[col].values)
                ax.axhline(mean_val, linestyle="--", linewidth=1, label=f"mean({col})", color=color, alpha=0.7, zorder=1)

            ax.set_xlabel("Rank (sorted per line)")
            ax.set_ylabel("Percent difference vs glibc (%)")
            ax.set_title(f"{metric_name} % diff vs glibc {'(absolute)' if use_abs else ''}".strip())
            ax.legend()
            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

        _draw("mean",   diffs_by_thing.get("mean"),   use_abs=False)  # now shows mean±mad_pct envelopes
        _draw("median", diffs_by_thing.get("median"), use_abs=False)
        _draw("mad_pct",    diffs_by_thing.get("mad_pct"),    use_abs=False)
        _draw("median", diffs_by_thing.get("median"), use_abs=True)

  
# ---------------- CLI ----------------
def main():
    parser = argparse.ArgumentParser(description="Ranked line plots of % diffs vs glibc and Excel exports.")
    parser.add_argument("-i", "--input", default="-", help="CSV input (default: stdin)")
    parser.add_argument("-o", "--output", required=True, help="Output PDF for figures")
    parser.add_argument("--csv-dir", default=None, help="Directory to write the 4 CSV files (optional)")
    parser.add_argument("--float-precision", type=int, default=6, help="CSV float precision (default 6)")
    parser.add_argument("--eps-factor", type=float, default=0.5, help="Row-wise epsilon factor (default 0.5)" )
    parser.add_argument("--eps-floor", type=float, default=None, help="Absolute epsilon floor (default: machine eps)" )
    args = parser.parse_args()

    # Read CSV
    if args.input == "-" or args.input == "":
        df = pd.read_csv(sys.stdin)
    else:
        df = pd.read_csv(args.input)

    colmap = parse_columns(df.columns, PARSE_SUFFIXES)
    diffs_by_thing = prepare_precent_differences(
        df, colmap, THINGS_TO_COMPARE,
        eps_factor=args.eps_factor, eps_floor=args.eps_floor
    )
    mad_by_thing = compute_yerr_from_mad_pct_in_csv(df, colmap)
    


    if args.csv_dir:
        export_diffs_to_csvs(diffs_by_thing, args.csv_dir, float_precision=args.float_precision)

    plot_ranked_percent_diffs(diffs_by_thing, args.output, mad_pctpct_by_thing=mad_by_thing)


if __name__ == "__main__":
    main()