MODULE_NAME := experiments
SUBMODULES := $(addprefix $(MODULE_NAME)/,$(MALLOC_VERSIONS))

ifndef NUM_OF_REPEATS
NUM_OF_REPEATS := 1
endif # ifndef NUM_OF_REPEATS

BENCHMARK_LIST := experiments/benchmark_list.txt

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

# define configuration_array
# $(addprefix configuration,$(shell seq 1 $1))
# endef

#### recipes and rules for prerequisites

# TEST_RUN_MOSALLOC_TOOL := $(SCRIPTS_ROOT_DIR)/testRunMosallocTool.sh
# test-run-mosalloc-tool: $(RUN_MOSALLOC_TOOL) $(MOSALLOC_TOOL)
# 	$(TEST_RUN_MOSALLOC_TOOL) $<

### include common makefile

# include $(ROOT_DIR)/common.mk
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
