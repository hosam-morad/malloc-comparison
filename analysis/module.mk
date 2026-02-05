##### constants
analysis_calculate := analysis/calculate.py
analysis_calculate_raw := analysis/calculate_raw.py
analysis_plot_ranked := analysis/plot.py

# analysis_metrics := run_time memory_consumption
analysis_metric := memory_consumption

##### outputs & dirs
# per-mode analysis directories
analysis_dir := analysis

analysis_csv := $(analysis_dir)/summary_$(analysis_metric).csv
analysis_raw_csv := $(analysis_dir)/summary_raw_$(analysis_metric).csv
analysis_pdf := $(analysis_dir)/summary_$(analysis_metric).pdf


# put our ranked CSV outputs in the per-mode analysis dir when plotting
ranked_csvs := \
	$(analysis_dir)/mean.csv \
	$(analysis_dir)/median.csv \
	$(analysis_dir)/mad.csv \
	$(analysis_dir)/abs_median.csv

##### rules
.PHONY: analysis analysis/clean

# Multi-threaded analysis: build CSVs and PDF under $(analysis_dir)
analysis: $(analysis_pdf) $(analysis_raw_csv)

$(analysis_csv):
	mkdir -p $(dir $@)
	$(analysis_calculate) -b $(BENCHMARK_LIST) -met $(analysis_metric) -m $(MALLOC_LIST) -p 2 -r results/ > $@

$(analysis_raw_csv):
	mkdir -p $(dir $@)
	$(analysis_calculate_raw) -b $(BENCHMARK_LIST) -met $(analysis_metric) -m $(MALLOC_LIST) -p 2 -r results/ > $@

$(analysis_pdf): $(analysis_csv)
	mkdir -p $(dir $@)
	$(analysis_plot_ranked) -i $< -o $@ --csv-dir $(analysis_dir)

analysis/clean:
	rm -f $(analysis_csv) $(analysis_pdf) $(ranked_csvs) $(analysis_raw_csv)
