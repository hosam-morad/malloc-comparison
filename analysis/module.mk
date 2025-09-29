##### constants
analysis_calculate := analysis/calculate.py
analysis_calculate_raw := analysis/calculate_raw.py
analysis_plot_ranked := analysis/plot.py

# analysis_metrics := run_time memory_consumption
analysis_metric := run_time

##### outputs & dirs
# per-mode analysis directories
multi_analysis_dir := analysis/multi_threaded
single_analysis_dir := analysis/single_threaded

multi_analysis_csv := $(multi_analysis_dir)/summary_$(analysis_metric).csv
multi_analysis_raw_csv := $(multi_analysis_dir)/summary_raw_$(analysis_metric).csv
multi_analysis_pdf := $(multi_analysis_dir)/summary_$(analysis_metric).pdf

single_analysis_csv := $(single_analysis_dir)/summary_$(analysis_metric).csv
single_analysis_raw_csv := $(single_analysis_dir)/summary_raw_$(analysis_metric).csv
single_analysis_pdf := $(single_analysis_dir)/summary_$(analysis_metric).pdf


merge_analysis_dir := analysis/merged

# put our ranked CSV outputs in the per-mode analysis dir when plotting
multi_ranked_csvs := \
	$(multi_analysis_dir)/mean.csv \
	$(multi_analysis_dir)/median.csv \
	$(multi_analysis_dir)/mad.csv \
	$(multi_analysis_dir)/abs_median.csv

single_ranked_csvs := \
	$(single_analysis_dir)/mean.csv \
	$(single_analysis_dir)/median.csv \
	$(single_analysis_dir)/mad.csv \
	$(single_analysis_dir)/abs_median.csv

##### rules
##### rules
.PHONY: analysis analysis/multi_threaded analysis/single_threaded analysis/clean analysis/multi_threaded_clean analysis/single_threaded_clean analysis/merged

# Top-level analysis builds both modes
analysis: analysis/multi_threaded analysis/single_threaded

# Multi-threaded analysis: build CSVs and PDF under $(multi_analysis_dir)
analysis/multi_threaded: $(multi_analysis_pdf) $(multi_analysis_raw_csv)

$(multi_analysis_csv):
	mkdir -p $(dir $@)
	$(analysis_calculate) -b $(BENCHMARK_LIST) -met $(analysis_metric) -m $(MALLOC_LIST) -p 2 -r results/multi_threaded > $@

$(multi_analysis_raw_csv):
	mkdir -p $(dir $@)
	$(analysis_calculate_raw) -b $(BENCHMARK_LIST) -met $(analysis_metric) -m $(MALLOC_LIST) -p 2 -r results/multi_threaded > $@

$(multi_analysis_pdf): $(multi_analysis_csv)
	mkdir -p $(dir $@)
	$(analysis_plot_ranked) -i $< -o $@ --csv-dir $(multi_analysis_dir)

# Single-threaded analysis: build CSVs and PDF under $(single_analysis_dir)
analysis/single_threaded: $(single_analysis_pdf) $(single_analysis_raw_csv)

$(single_analysis_csv):
	mkdir -p $(dir $@)
	$(analysis_calculate) -b $(BENCHMARK_LIST) -met $(analysis_metric) -m $(MALLOC_LIST) -p 2 -r results/single_threaded > $@

$(single_analysis_raw_csv):
	mkdir -p $(dir $@)
	$(analysis_calculate_raw) -b $(BENCHMARK_LIST) -met $(analysis_metric) -m $(MALLOC_LIST) -p 2 -r results/single_threaded > $@

$(single_analysis_pdf): $(single_analysis_csv)
	mkdir -p $(dir $@)
	$(analysis_plot_ranked) -i $< -o $@ --csv-dir $(single_analysis_dir)

merge_analysis_dir := analysis/merged

# Dynamically generate the list of merged files based on single-threaded CSVs
MERGED_CSV_FILES := $(patsubst $(single_analysis_dir)/%.csv,$(merge_analysis_dir)/%.csv,$(wildcard $(single_analysis_dir)/*.csv))

# Rule to create the merged directory and ensure all merged files are generated
analysis/merged: $(MERGED_CSV_FILES)
	mkdir -p $(merge_analysis_dir)

# Rule to merge single-threaded and multi-threaded CSVs into the merged directory
$(merge_analysis_dir)/%.csv: $(single_analysis_dir)/%.csv $(multi_analysis_dir)/%.csv
	mkdir -p $(dir $@)
	python analysis/merge_csvs.py $(single_analysis_dir)/$*.csv $(single_analysis_dir) $(multi_analysis_dir)/$*.csv $(multi_analysis_dir) $@
analysis/clean:
	rm -f $(multi_analysis_csv) $(multi_analysis_pdf) $(multi_ranked_csvs) $(multi_analysis_raw_csv)
	rm -f $(single_analysis_csv) $(single_analysis_pdf) $(single_ranked_csvs) $(single_analysis_raw_csv)

analysis/multi_threaded_clean:
	rm -f $(multi_analysis_csv) $(multi_analysis_pdf) $(multi_ranked_csvs) $(multi_analysis_raw_csv)

analysis/single_threaded_clean:
	rm -f $(single_analysis_csv) $(single_analysis_pdf) $(single_ranked_csvs) $(single_analysis_raw_csv)
