EXPERIMENT_DIR := experiments/MALLOC_VERSION

##### constants
REPEATS := $(shell seq 1 $(NUM_OF_REPEATS))
REPEATS := $(addprefix repeat,$(REPEATS)) 
MALLOC_TOOL := $(ROOT_DIR)/mallocs/MALLOC_VERSION/libMALLOC_VERSION.so
##### targets
EXPERIMENTS := $(addprefix $(EXPERIMENT_DIR)/, $(benchmarks))
EXPERIMENT_REPEATS := $(foreach experiment,$(EXPERIMENTS),$(foreach repeat,$(REPEATS),$(experiment)/$(repeat)))
MEASUREMENTS := $(addsuffix /time.out,$(EXPERIMENT_REPEATS))


$(EXPERIMENT_DIR): $(MEASUREMENTS)
$(EXPERIMENTS): $(EXPERIMENT_DIR)/%: $(foreach repeat,$(REPEATS),$(addsuffix /$(repeat)/time.out,$(EXPERIMENT_DIR)/%))
$(EXPERIMENT_REPEATS): %: %/time.out

$(MEASUREMENTS): $(MALLOC_TOOL)
	echo ========== [INFO] start MALLOC_VERSION ==========
	benchmark=$$(echo $(dir $@) | cut -d/ -f3-4); \
	$(RUN_BENCHMARK) --submit_command "$(MEASURE_METRICS) $(SET_CPU_MEMORY_AFFINITY) $(BOUND_MEMORY_NODE) \
		$(RUN_MALLOC_TOOL) --library $(MALLOC_TOOL)" -- $(benchmarks_root)/$$benchmark $(dir $@)

DELETED_TARGETS := $(EXPERIMENTS) $(EXPERIMENT_REPEATS)
CLEAN_TARGETS := $(addsuffix /clean,$(DELETED_TARGETS))
$(CLEAN_TARGETS): %/clean: %/delete
$(MODULE_NAME)/clean: $(CLEAN_TARGETS)

