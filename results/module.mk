##### constants
kv_to_csv := results/kv_to_csv.py

##### targets

result_measurements_dirs := $(foreach malloc,$(MALLOC_VERSIONS), \
	$(foreach bench,$(benchmarks), \
		results/$(malloc)/$(bench)))

result_measurements := $(foreach dir,$(result_measurements_dirs), \
	$(foreach repeat,$(REPEATS), \
		$(dir)/$(repeat)/time.csv))



##### rules
.PHONY: results results/clean

results: $(result_measurements)

# results/%/time.csv: experiments/%/time.out
# 	mkdir -p $(dir $@)
# 	$(kv_to_csv) $< > $@
results/%/time.csv:
	mkdir -p $(dir $@)
	$(kv_to_csv) $(patsubst results/%,experiments/%,$(basename $@).out) > $@

results/clean:
	rm -f $(result_measurements) 
