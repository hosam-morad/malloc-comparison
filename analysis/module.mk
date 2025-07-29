##### constants
analysis_calculate := analysis/calculate.py
analysis_plot := analysis/plot.py

# analysis_metrics := run_time memory_consumption
analysis_metric := memory_consumption

##### targets
analysis_csv := analysis/summary_$(analysis_metric).csv
analysis_pdf := analysis/summary_$(analysis_metric).pdf

##### rules
.PHONY: analysis analysis/clean

analysis: $(analysis_pdf)

$(analysis_pdf): $(analysis_csv)
	$(analysis_plot) -o $@ -m $(analysis_metric) < $<

# $(analysis_csv): $(result_measurements)
$(analysis_csv):
	$(analysis_calculate) -b $(BENCHMARK_LIST) -met $(analysis_metric) -m $(MALLOC_LIST) -p 2 > $@


analysis/clean:
	rm -f $(analysis_csv) $(analysis_pdfs)