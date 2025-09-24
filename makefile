SHELL := /bin/bash
# run all lines of a recipe in a single invocation of the shell rather than each line being invoked separately
.ONESHELL:
# invoke recipes as if the shell had been passed the -e flag: the first failing command in a recipe will cause the recipe to fail immediately
.POSIX:

MODULE_NAME := all

benchmarks_root := /scratch/hosam.morad/benchmarks
export BENCHMARKS_ROOT = $(benchmarks_root)
export ROOT_DIR := $(PWD)

SCRIPTS_ROOT_DIR := $(ROOT_DIR)/scripts
MALLOCS_ROOT_DIR := $(ROOT_DIR)/mallocs

##### constants

SUBMODULES := mallocs experiments experiments-singlethreaded results analysis

include $(ROOT_DIR)/workloads.mk
include $(ROOT_DIR)/common.mk

# a top-level "clean" target, which calls all/clean
.PHONY: clean
clean: all/clean

# a generic pattern rule for deleting files
.PHONY: %/delete
%/delete:
	rm -rf $*

# empty recipes to prevent make from remaking the makefile and include files
# https://www.gnu.org/software/make/manual/html_node/Remaking-Makefiles.html
makefile: ;
%.mk: ;