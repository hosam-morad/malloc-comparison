##### constants
analysis_calculate := analysis/calculate.py
analysis_calculate_raw := analysis/calculate_raw.py
analysis_plot_ranked := analysis/plot.py

# analysis_metrics := run_time memory_consumption
analysis_metric := run_time

##### outputs & dirs
analysis_csv := analysis/summary_$(analysis_metric).csv
# You can override this on the command line:
#   make analysis analysis_raw_csv=analysis/raw_experiment42.csv
analysis_raw_csv := analysis/summary_raw_$(analysis_metric).csv
analysis_pdf := analysis/summary_$(analysis_metric).pdf

# put our ranked Excel outputs directly in the existing analysis/ dir
analysis_ranked_excel_dir := analysis
analysis_ranked_csvs := \
  $(analysis_ranked_excel_dir)/mean.csv \
  $(analysis_ranked_excel_dir)/median.csv \
  $(analysis_ranked_excel_dir)/mad.csv \
  $(analysis_ranked_excel_dir)/abs_median.csv

##### rules
.PHONY: analysis analysis/clean

# Build the PDF summary and (also) produce a raw CSV
analysis: $(analysis_pdf) $(analysis_raw_csv)

$(analysis_pdf): $(analysis_csv)
	$(analysis_plot_ranked) -i $< -o $@ --csv-dir $(analysis_ranked_excel_dir)

# $(analysis_csv): $(result_measurements)
$(analysis_csv):
	$(analysis_calculate) -b $(BENCHMARK_LIST) -met $(analysis_metric) -m $(MALLOC_LIST) -p 2 > $@

# Raw (non-aggregated) CSV; override the filename via analysis_raw_csv=...
$(analysis_raw_csv):
	$(analysis_calculate_raw) -b $(BENCHMARK_LIST) -met $(analysis_metric) -m $(MALLOC_LIST) -p 2 > $@

analysis/clean:
	rm -f $(analysis_csv) $(analysis_pdf) $(analysis_ranked_csvs) $(analysis_raw_csv)
