##### constants
kv_to_csv := results/kv_to_csv.py

##### targets

result_measurements_dirs := $(foreach malloc,$(MALLOC_VERSIONS), \
	$(foreach bench,$(benchmarks), \
		results/multi_threaded/$(malloc)/$(bench)))

result_measurements := $(foreach dir,$(result_measurements_dirs), \
	$(foreach repeat,$(REPEATS), \
		$(dir)/$(repeat)/time.csv))

# Single-threaded variant: outputs under results/single_threaded/... and read from experiments-singlethreaded
single_result_measurements_dirs := $(foreach malloc,$(MALLOC_VERSIONS), \
	$(foreach bench,$(benchmarks), \
		results/single_threaded/$(malloc)/$(bench)))

single_result_measurements := $(foreach dir,$(single_result_measurements_dirs), \
	$(foreach repeat,$(REPEATS), \
		$(dir)/$(repeat)/time.csv))

##### rules
.PHONY: results results/multi_threaded results/single_threaded results/clean results/multi_threaded_clean results/single_threaded_clean

results: $(result_measurements) $(single_result_measurements)

results/multi_threaded: $(result_measurements)

# results/%/time.csv: experiments/%/time.out
# 	mkdir -p $(dir $@)
# 	$(kv_to_csv) $< > $@
results/multi_threaded/%/time.csv:
	mkdir -p $(dir $@)
	$(kv_to_csv) $(patsubst results/multi_threaded/%,experiments/%,$(basename $@).out) > $@

# Single-threaded results target: generate results under results/single_threaded
results/single_threaded: $(single_result_measurements)

results/single_threaded/%/time.csv:
	mkdir -p $(dir $@)
	$(kv_to_csv) $(patsubst results/single_threaded/%,experiments-singlethreaded/%,$(basename $@).out) > $@

results/clean:
	rm -f $(result_measurements) $(single_result_measurements)

results/multi_threaded_clean:
	rm -f $(result_measurements)

results/single_threaded_clean:
	rm -f $(single_result_measurements)
