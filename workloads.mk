##### constants

# start with an empty list of benchmarks
all_benchmarks := $(shell cat $(benchmarks_root)/benchmark_list.txt)
benchmarks :=
# include all SPEC CPU 2006/2017 benchmarks
benchmarks += $(filter spec_cpu2006/% spec_cpu2017/%, $(all_benchmarks))
# include all gups, hpcc, xsbench, graph500, and gapbs benchmarks
benchmarks += $(filter graph500-2.1/% gups/% hpcc/% xsbench/% gapbs/%, $(all_benchmarks))
# exclude big benchmarks because they (1) run for long times and (2) show low L1/L2 TLB miss rates
# in terms of MPKC (which make sense because their IPC is relatively low)
benchmarks := $(filter-out %8GB %16GB %32GB %64GB, $(benchmarks))
benchmarks := $(filter-out gapbs/%road gapbs/%web gapbs/%twitter, $(benchmarks))
# exclude multi-thread HPCC benchmarks that have single-thread counterparts
benchmarks := $(filter-out hpcc/star% hpcc/mpi%, $(benchmarks))
# exclude HPCC benchmarks that are irrelevant
benchmarks := $(filter-out hpcc/lat_bw% hpcc/single_stream%, $(benchmarks))
# include the big workloads from ASPLOS'23 submission
#benchmarks += gapbs/pr-kron-32GB gapbs/sssp-kron-32GB

