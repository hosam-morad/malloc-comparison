# Analysis

This folder contains the analysis and plotting pipeline for processing experiment results.  
It provides Makefile rules to generate summary data, plots, and merged results for both **multi-threaded** and **single-threaded** modes.

---

## Files

- **`calculate.py`** – computes summary statistics and writes aggregated CSV files.  
- **`calculate_raw.py`** – produces raw, unprocessed CSV data.  
- **`plot.py`** – generates ranked plots (PDF) and per-statistic CSVs (`mean`, `median`, `mad`, `abs_median`).  
- **`merge_csvs.py`** – merges single-threaded and multi-threaded CSVs into unified merged files.  
- **`Makefile`** – automates all analysis steps.

---

## Makefile Targets

### `analysis`
Runs both:
- `analysis/multi_threaded`
- `analysis/single_threaded`

Generates CSV summaries, raw CSVs, and PDF plots for both modes.

---

### `analysis/multi_threaded`
Creates outputs under `analysis/multi_threaded/`:
- `summary_run_time.csv`  
- `summary_raw_run_time.csv`  
- `summary_run_time.pdf`  
- ranked CSVs (`mean.csv`, `median.csv`, `mad.csv`, `abs_median.csv`)

---

### `analysis/single_threaded`
Creates outputs under `analysis/single_threaded/`:
- `summary_run_time.csv`  
- `summary_raw_run_time.csv`  
- `summary_run_time.pdf`  
- ranked CSVs (`mean.csv`, `median.csv`, `mad.csv`, `abs_median.csv`)

---

### `analysis/merged`
Produces merged CSVs under `analysis/merged/` by combining corresponding files from:
- `analysis/single_threaded/`
- `analysis/multi_threaded/`

Each merged file is generated using `merge_csvs.py`.

---

### Cleaning
- `analysis/clean` – removes all generated outputs.  
- `analysis/single_threaded_clean` – cleans only single-threaded outputs.  
- `analysis/multi_threaded_clean` – cleans only multi-threaded outputs.

---

## Output Structure
analysis/
├── multi_threaded/
│ ├── summary_run_time.csv
│ ├── summary_raw_run_time.csv
│ ├── summary_run_time.pdf
│ ├── mean.csv
│ ├── median.csv
│ ├── mad.csv
│ └── abs_median.csv
├── single_threaded/
│ ├── summary_run_time.csv
│ ├── summary_raw_run_time.csv
│ ├── summary_run_time.pdf
│ ├── mean.csv
│ ├── median.csv
│ ├── mad.csv
│ └── abs_median.csv
└── merged/
└── *.csv
