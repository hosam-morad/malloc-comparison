
# malloc-performance-study

This repository contains an experimental framework for **building, running, and analyzing different memory allocators (`malloc` implementations)** under controlled workloads.
The goal is to **compare allocator behavior and performance** across **single-threaded** and **multi-threaded** environments using real benchmarks.

The project is designed as a **modular, Makefile-driven system**, where each subdirectory represents a logical module (allocators, experiments, analysis, results, etc.), all orchestrated from a **single top-level Makefile**.

---

## Project Motivation

Memory allocation plays a critical role in application performance and scalability. Different allocators make different tradeoffs in:

* Latency vs throughput
* Fragmentation
* Cache behavior
* Contention under multithreading

This project evaluates multiple allocators by running standardized benchmarks in:

* **Single-threaded mode**
* **Multi-threaded mode (using OpenMP)**

The results help expose how allocator design choices affect performance under varying workloads and concurrency levels.

---

## Repository Structure

```
.
├── Makefile                # Root orchestrator Makefile
├── common.mk               # Shared Makefile logic and utilities
├── workloads.mk            # Benchmark/workload definitions
├── mallocs/                # Allocator implementations and builds
├── experiments/            # Multi-threaded (OpenMP) experiments
├── experiments-singlethreaded/  # Single-threaded experiments
├── results/                # Collected raw results
├── analysis/               # Post-processing and analysis scripts
└── scripts/                # Automation and helper scripts
```

Each subdirectory contains its own `module.mk` file and is treated as an independent **Makefile module**.

---

## Build System Design

The project uses a **hierarchical Makefile architecture**:

* The **root Makefile**:

  * Defines global paths and environment variables
  * Exports shared configuration
  * Invokes submodules in a consistent order
* Each subdirectory:

  * Contains a `module.mk`
  * Implements its own build / run / clean logic
  * Can be executed independently or via the root Makefile

### Root Makefile Responsibilities

The root Makefile:

* Exports important environment variables such as:

  * `BENCHMARKS_ROOT`
  * `ROOT_DIR`
* Defines all top-level modules:

  ```make
  SUBMODULES := mallocs experiments experiments-singlethreaded results analysis
  ```
* Includes shared logic:

  ```make
  include workloads.mk
  include common.mk
  ```
* Provides a **global `clean` target** that propagates cleanup to all modules.

This design allows:

* Reproducible experiments
* Easy extension with new allocators or workloads
* Clear separation between build, execution, and analysis phases

---

## Experiment Modes

### Single-Threaded Experiments

* Executed under `experiments-singlethreaded/`
* Focus on allocator baseline behavior
* Useful for isolating allocator logic without synchronization effects

### Multi-Threaded Experiments

* Executed under `experiments/`
* Use **OpenMP** to introduce concurrency
* Stress allocator scalability, locking strategies, and contention handling

---

## Results (Single-Threaded)

We evaluated several benchmarks in a **single-threaded configuration** to isolate allocator behavior.
While most workloads show similar trends across allocators, **a subset of benchmarks exhibits a pronounced difference in kernel execution time**.

In particular, the following benchmarks consistently demonstrate this behavior:

* `502.gcc_r`
* `554.roms_r`

---

### Observed Behavior

For these benchmarks, execution with `dlmalloc` shows:

* Comparable **user-space execution time** to other allocators
* **Significantly higher kernel time**
* Substantially increased total elapsed time as a result

In contrast, allocators such as `ptmalloc2` maintain low kernel time while executing the same workloads.

---

### Example Metrics

Representative single-threaded measurements are shown below.

#### `502.gcc_r`

| Allocator | User Time (s) | Kernel Time (s) |
| --------- | ------------- | --------------- |
| dlmalloc  | ~494          | ~102            |
| ptmalloc2 | ~466          | ~6              |

#### `554.roms_r`

| Allocator | User Time (s) | Kernel Time (s) |
| --------- | ------------- | --------------- |
| dlmalloc  | ~466          | ~83             |
| ptmalloc2 | ~436          | ~0.6            |

---

### Interpretation

The large performance gap observed in these benchmarks is primarily driven by **kernel time**, not by user-space computation.

This suggests that for certain workloads, `dlmalloc` incurs substantially more kernel involvement, likely due to allocator–OS interactions such as:

* Memory growth and release behavior
* Page mapping and page fault handling
* Internal allocator management overhead

Other allocators, such as `ptmalloc2`, handle these workloads with minimal kernel involvement, resulting in significantly lower kernel time.

---

### Notes

* The effect is **benchmark-dependent** and not observed uniformly across all workloads
* These results reflect **single-threaded execution**
* Multi-threaded experiments further explore allocator behavior under contention


---

## How to Use

Typical workflow:

```bash
# Build everything
make

# Run experiments (depending on module targets)
make experiments
make experiments-singlethreaded

# Analyze results
make analysis

# Clean everything
make clean
```

Exact targets and parameters are documented in each module’s `README.md`.

---

## Extending the Project

You can easily extend the framework by:

* Adding a new allocator under `mallocs/`
* Adding new workloads in `workloads.mk`
* Introducing new analysis scripts under `analysis/`

The modular Makefile structure ensures minimal changes to the root logic.

---

## Notes

* The project assumes a Linux environment
* OpenMP is required for multi-threaded experiments
* Benchmarks are expected under `$BENCHMARKS_ROOT`

---