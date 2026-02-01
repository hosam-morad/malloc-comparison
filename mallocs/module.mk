##### mallocs/module.mk

MALLOC_ROOT_DIR   := mallocs
MALLOC_BUILD_DIR  := $(MALLOC_ROOT_DIR)/build
MALLOC_CMAKE      := $(MALLOC_ROOT_DIR)/CMakeLists.txt

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
MALLOC_VERSIONS ?= dlmalloc mimalloc malloc-standalone-auto

# If CMake generates versions.mk, this rule will create/update it when CMakeLists changes
$(MALLOC_ROOT_DIR)/versions.mk: $(MALLOC_CMAKE)
	mkdir -p $(MALLOC_BUILD_DIR)
	cd $(MALLOC_BUILD_DIR) && cmake ..

# Optional override; safe if file doesn't exist
-include $(MALLOC_ROOT_DIR)/versions.mk

# --- Libs list & outputs ------------------------------------------------------
MALLOC_LIST     := $(MALLOC_ROOT_DIR)/malloc_list.txt
MALLOC_LIB_DIR  := $(MALLOC_BUILD_DIR)


# Built by CMake: all mallocs except the standalone one
MALLOC_LIBS := $(foreach malloc,$(MALLOC_VERSIONS),$(MALLOC_LIB_DIR)/lib$(malloc).so)

.PHONY: mallocs mallocs/clean
mallocs: $(MALLOC_LIBS) $(MALLOC_LIST)

# --- Build rule for CMake-built mallocs --------------------------------------
$(MALLOC_LIBS): $(MALLOC_CMAKE) | $(MALLOC_BUILD_DIR)
	$(MAKE) -C $(MALLOC_BUILD_DIR)

$(MALLOC_BUILD_DIR):
	mkdir -p $@
	
$(MALLOC_LIB_DIR):
	mkdir -p $@
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

mallocs/clean:
	rm -rf $(MALLOC_BUILD_DIR) $(MALLOC_VERSION_STAMP) $(MALLOC_LIST) $(MALLOC_ROOT_DIR)/versions.mk $(SUBMODULES_STAMP)