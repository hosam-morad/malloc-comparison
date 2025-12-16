# results/

This directory contains **processed experiment outputs** in CSV format, ready for analysis.

Raw measurements produced by the experiment modules are converted into structured CSV files for both **multi-threaded** and **single-threaded** runs.

---

## What This Module Does

* Collects raw timing outputs from experiment runs
* Converts key–value measurement files into CSV format
* Organizes results by allocator, benchmark, and repetition
* Prepares data for downstream analysis

---

## Directory Structure

```
results/
├── multi_threaded/
│   └── <malloc>/<benchmark>/<repeat>/time.csv
└── single_threaded/
    └── <malloc>/<benchmark>/<repeat>/time.csv
```

Each `time.csv` contains a single measurement instance.

---

## Input Sources

* Multi-threaded results are read from:

  ```
  experiments/<malloc>/<benchmark>/<repeat>/time.out
  ```

* Single-threaded results are read from:

  ```
  experiments-singlethreaded/<malloc>/<benchmark>/<repeat>/time.out
  ```

---

## Processing Script

Raw outputs are processed using:

```
results/kv_to_csv.py
```

The script:

* Parses `key,value` pairs from `time.out`
* Emits a two-row CSV:

  * Header row (keys)
  * Value row
* Skips invalid or missing entries
* Detects crashes by checking `benchmark.log` for `"core dumped"`

---

## Make Targets

```bash
make results                  # generate all results (single + multi)
make results/multi_threaded   # generate multi-threaded CSVs
make results/single_threaded  # generate single-threaded CSVs

make results/clean             # remove all CSVs
make results/multi_threaded_clean
make results/single_threaded_clean
```

---

## Notes

* Results are grouped by allocator, benchmark, and repetition
* CSV files are intentionally minimal and machine-readable
* This module performs **no analysis**—only data preparation