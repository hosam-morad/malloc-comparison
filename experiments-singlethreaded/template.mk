EXPERIMENT_DIR := experiments-singlethreaded/MALLOC_VERSION

##### constants
REPEATS := $(shell seq 1 $(NUM_OF_REPEATS))
REPEATS := $(addprefix repeat,$(REPEATS))
MALLOC_VERSION_TOOL := $(ROOT_DIR)/$(MALLOC_LIB_DIR)/libMALLOC_VERSION.so

##### targets
EXPERIMENTS := $(addprefix $(EXPERIMENT_DIR)/, $(benchmarks))
EXPERIMENT_REPEATS := $(foreach experiment,$(EXPERIMENTS),$(foreach repeat,$(REPEATS),$(experiment)/$(repeat)))
MEASUREMENTS := $(addsuffix /time.out,$(EXPERIMENT_REPEATS))

$(EXPERIMENT_DIR): $(MEASUREMENTS)
$(EXPERIMENTS): $(EXPERIMENT_DIR)/%: $(foreach repeat,$(REPEATS),$(addsuffix /$(repeat)/time.out,$(EXPERIMENT_DIR)/%))
$(EXPERIMENT_REPEATS): %: %/time.out

$(MEASUREMENTS): experiments-prerequisites
	echo ========== [INFO] start MALLOC_VERSION ==========
	benchmark=$$(echo $(dir $@) | cut -d/ -f3-4); \
	BINDNODE=$(BOUND_MEMORY_NODE); \
	$(RUN_BENCHMARK) --exclude gmon.* --num_threads 1 \
		--submit_command "$(MEASURE_METRICS) $(SET_CPU_MEMORY_AFFINITY) $$BINDNODE \
		$(RUN_MALLOC_TOOL) --library $(MALLOC_VERSION_TOOL)" -- $(benchmarks_root)/$$benchmark $(dir $@)

DELETED_TARGETS := $(EXPERIMENTS) $(EXPERIMENT_REPEATS)
CLEAN_TARGETS := $(addsuffix /clean,$(DELETED_TARGETS))
$(CLEAN_TARGETS): %/clean: %/delete
$(MODULE_NAME)/clean: $(CLEAN_TARGETS)
