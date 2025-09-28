.PHONY: results
results: results/copy_benchmarks results/copy_gmon results/merge

# Copy the benchmark files once per bench into: results/<suite>/<bench>/benchmarkfile/
.PHONY: results/copy_benchmarks
results/copy_benchmarks:
	@set -e; \
	for b in $(benchmarks); do \
	  src="$(benchmarks_root)/$$b"; \
	  dst="results/$$b/benchmarkfile"; \
	  mkdir -p "$$dst"; \
	  if [ -d "$$src" ]; then \
	    cp -a "$$src"/. "$$dst"/; \
	  else \
	    cp -a "$$src" "$$dst/"; \
	  fi; \
	  echo ">> copied $$src -> $$dst"; \
	done
.PHONY: results/copy_gmon
results/copy_gmon:
	@set -e; \
	for m in $(MALLOC_VERSIONS); do \
	  for b in $(benchmarks); do \
	    for r in $(REPEATS); do \
	      src="experiments-singlethreaded/$$m/$$b/$$r"; \
	      dst="results/$$b/$$m/$$r"; \
	      [ -d "$$src" ] || continue; \
	      mkdir -p "$$dst"; \
	      set -- "$$src"/gmon.*; \
	      [ -e "$$1" ] || { echo ">> no gmon.* in $$src"; continue; }; \
	      cp -a "$$src"/gmon.* "$$dst"/; \
	      rm -f "$$dst"/*.out; \
	      echo ">> copied $$src/gmon.* -> $$dst/ (removed *.out)"; \
	    done; \
	  done; \
	done




# merge per repeat (no deletes, same style as manual)
.PHONY: results/merge
results/merge:results/copy_benchmarks results/copy_gmon
	@set -e; \
	for b in $(benchmarks); do \
	  runsh="results/$$b/benchmarkfile/run.sh"; \
	  [ -f "$$runsh" ] || { echo ">> missing $$runsh (skip $$b)"; continue; }; \
	  exe_rel=$$(awk 'NF && $$1 !~ /^#/ {last=$$1} END{gsub(/^\.\//,"",last); print last}' "$$runsh"); \
	  ( cd "results/$$b" && \
	    exe="benchmarkfile/$$exe_rel"; \
	    for m in $(MALLOC_VERSIONS); do \
	      for r in $(REPEATS); do \
	        set -- "$$m/$$r"/gmon.*; \
	        [ -e "$$1" ] || { echo ">> no gmon.* in results/$$b/$$m/$$r"; continue; }; \
	        gprof "$$exe" "$$@" > "$$m/$$r/analysis.txt"; \
	        echo ">> wrote results/$$b/$$m/$$r/analysis.txt"; \
	      done; \
	    done ); \
	done

.PHONY: results/profile_png
results/profile_png:
	@set -e; \
	for b in $(benchmarks); do \
	  for m in $(MALLOC_VERSIONS); do \
	    for r in $(REPEATS); do \
	      rep="results/$$b/$$m/$$r"; \
	      [ -f "$$rep/analysis.txt" ] || { echo ">> no analysis.txt in $$rep (skip)"; continue; }; \
	      if command -v gprof2dot >/dev/null 2>&1 && command -v dot >/dev/null 2>&1; then \
	        gprof2dot < "$$rep/analysis.txt" | dot -Gdpi=300 -Tpng -o "$$rep/profile.png"; \
	        echo ">> wrote $$rep/profile.png"; \
	      else \
	        echo ">> need gprof2dot + graphviz (install via conda-forge)"; exit 1; \
	      fi; \
	    done; \
	  done; \
	done

