##### mallocs/module.mk

MALLOC_ROOT_DIR   := mallocs
MALLOC_BUILD_DIR  := $(MALLOC_ROOT_DIR)/build
MALLOC_CMAKE      := $(MALLOC_ROOT_DIR)/CMakeLists.txt

# --- Custom standalone malloc -------------------------------------------------
# Logical name inside the framework
STANDALONE_MALLOC_NAME    := malloc-standalone
# Actual prebuilt .so you already have
STANDALONE_MALLOC_SRC_SO  := ../malloc-standalone/automated/build/libmalloc_auto.so

# --- Submodules guard ---------------------------------------------------------
SUBMODULES_STAMP := $(MALLOC_ROOT_DIR)/.submodules-inited

$(SUBMODULES_STAMP): .gitmodules
	git submodule update --init --recursive
	touch $@

.PHONY: mallocs-submodules
mallocs-submodules: $(SUBMODULES_STAMP)

# Ensure submodules exist before configuring/building (order-only)
$(MALLOC_ROOT_DIR)/versions.mk: | $(SUBMODULES_STAMP)
$(MALLOC_BUILD_DIR):            | $(SUBMODULES_STAMP)

# --- Versions discovery -------------------------------------------------------
# Base default; repo / CMake may override this via versions.mk
MALLOC_VERSIONS ?= dlmalloc mimalloc

# If CMake generates versions.mk, this rule will create/update it when CMakeLists changes
$(MALLOC_ROOT_DIR)/versions.mk: $(MALLOC_CMAKE)
	mkdir -p $(MALLOC_BUILD_DIR)
	cd $(MALLOC_BUILD_DIR) && cmake ..

# Optional override; safe if file doesn't exist
-include $(MALLOC_ROOT_DIR)/versions.mk

# Always add our standalone malloc on top of whatever was set
MALLOC_VERSIONS += $(STANDALONE_MALLOC_NAME)

# --- Libs list & outputs ------------------------------------------------------
MALLOC_LIST     := $(MALLOC_ROOT_DIR)/malloc_list.txt
MALLOC_LIB_DIR  := $(MALLOC_BUILD_DIR)/lib

# Built by CMake: all mallocs except the standalone one
MALLOC_BUILT_VERSIONS := $(filter-out $(STANDALONE_MALLOC_NAME),$(MALLOC_VERSIONS))
MALLOC_BUILT_LIBS     := $(foreach malloc,$(MALLOC_BUILT_VERSIONS),$(MALLOC_LIB_DIR)/lib$(malloc).so)

# Our standalone lib inside the framework
MALLOC_STANDALONE_LIB := $(MALLOC_LIB_DIR)/lib$(STANDALONE_MALLOC_NAME).so

MALLOC_LIBS := $(MALLOC_BUILT_LIBS) $(MALLOC_STANDALONE_LIB)

.PHONY: mallocs
mallocs: $(MALLOC_LIBS) $(MALLOC_LIST)

# --- Build rule for CMake-built mallocs --------------------------------------
$(MALLOC_BUILT_LIBS): $(MALLOC_CMAKE) | $(MALLOC_BUILD_DIR)
	$(MAKE) -C $(MALLOC_BUILD_DIR)

$(MALLOC_BUILD_DIR):
	mkdir -p $@

$(MALLOC_LIB_DIR):
	mkdir -p $@

# --- Standalone malloc: ONLY copy, do not build -------------------------------
$(MALLOC_STANDALONE_LIB): $(STANDALONE_MALLOC_SRC_SO) | $(MALLOC_LIB_DIR)
	cp $< $@

# --- Versions list ------------------------------------------------------------
$(MALLOC_LIST): $(MALLOC_ROOT_DIR)/versions.mk | $(MALLOC_ROOT_DIR)
	echo $(MALLOC_VERSIONS) | tr " " "\n" | sort > $@

$(MALLOC_ROOT_DIR):
	mkdir -p $@

# --- Backward-compat stamp for older rules expecting mallocs/version_ ---------
MALLOC_VERSION_STAMP := $(MALLOC_ROOT_DIR)/version_

$(MALLOC_VERSION_STAMP):
	mkdir -p $(MALLOC_ROOT_DIR)
	touch $@
