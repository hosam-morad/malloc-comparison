MODULE_NAME := experiments-singlethreaded
SUBMODULES := $(addprefix $(MODULE_NAME)/,$(MALLOC_VERSIONS))

ifndef NUM_OF_REPEATS
NUM_OF_REPEATS := 3
endif # ifndef NUM_OF_REPEATS

BENCHMARK_LIST := experiments-singlethreaded/benchmark_list.txt

##### scripts
RUN_BENCHMARK := $(SCRIPTS_ROOT_DIR)/runBenchmark.py
MEASURE_METRICS := $(SCRIPTS_ROOT_DIR)/measureMetrics.sh
RUN_MALLOC_TOOL := $(SCRIPTS_ROOT_DIR)/runMalloc.py
SET_CPU_MEMORY_AFFINITY := $(SCRIPTS_ROOT_DIR)/setCpuMemoryAffinity.sh

###### global constants
export EXPERIMENTS_ROOT := $(ROOT_DIR)/$(MODULE_NAME)
export EXPERIMENTS_TEMPLATE := $(EXPERIMENTS_ROOT)/template.mk
NUMBER_OF_SOCKETS := $(shell ls -d /sys/devices/system/node/node*/ | wc -w)
export BOUND_MEMORY_NODE := $$(( $(NUMBER_OF_SOCKETS) - 1 ))

.PHONY: experiments-prerequisites
experiments-prerequisites: mallocs

$(MODULE_NAME): $(BENCHMARK_LIST) $(SUBMODULES)

SUBMAKEFILES := $(addsuffix /module.mk,$(SUBMODULES))

$(MODULE_NAME)/%/module.mk: $(MODULE_NAME)/template.mk
	mkdir -p $(dir $@)
	cp $< $@
	sed -i "s/MALLOC_VERSION/$(notdir $(patsubst %/,%,$(dir $@)))/g" $@

$(BENCHMARK_LIST): $(MODULE_NAME)/module.mk
	echo $(benchmarks) | tr " " "\n" | sort > $@

$(MODULE_NAME)/clean: $(addsuffix /clean,$(SUBMODULES))

-include $(SUBMAKEFILES)
