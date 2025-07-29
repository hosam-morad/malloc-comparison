##### mallocs/module.mk

MALLOC_ROOT_DIR := mallocs
MALLOC_BUILD_DIR := $(MALLOC_ROOT_DIR)/build
MALLOC_CMAKE := $(MALLOC_BUILD_DIR)/CMakeCache.txt

include $(MALLOC_ROOT_DIR)/versions.mk

MALLOC_LIST := $(MALLOC_ROOT_DIR)/malloc_list.txt

# Default CMake .so output layout (subdir per malloc)
MALLOC_LIB_DIR := $(MALLOC_BUILD_DIR)/lib
MALLOC_LIBS := $(foreach malloc,$(MALLOC_VERSIONS),$(MALLOC_LIB_DIR)/lib$(malloc).so)

.PHONY: $(MALLOC_CMAKE) $(MALLOC_LIST) $(MALLOC_ROOT_DIR) 

$(MALLOC_ROOT_DIR): $(MALLOC_LIBS)

$(MALLOC_LIBS): $(MALLOC_CMAKE)
	$(MAKE) -C $(MALLOC_BUILD_DIR)

$(MALLOC_CMAKE):
	mkdir -p $(MALLOC_BUILD_DIR)
	cd $(MALLOC_BUILD_DIR) && cmake ..

$(MALLOC_LIST): $(MALLOC_ROOT_DIR)/module.mk
	echo $(MALLOC_VERSIONS) | tr " " "\n" | sort > $@