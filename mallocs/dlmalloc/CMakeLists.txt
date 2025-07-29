cmake_minimum_required(VERSION 3.10)
project(dlmalloc)

# Use directory name as target name
get_filename_component(ALLOC_NAME ${CMAKE_CURRENT_SOURCE_DIR} NAME)

# Collect source and header files
file(GLOB SRCS "${CMAKE_CURRENT_SOURCE_DIR}/src/*.cc")
file(GLOB HDRS "${CMAKE_CURRENT_SOURCE_DIR}/include/*.h")

# Create shared library
add_library(${ALLOC_NAME} SHARED ${SRCS} ${HDRS})

# Set include path for the allocator's header files
target_include_directories(${ALLOC_NAME} PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# Optional: set the output path of the shared library to the allocator root
# set_target_properties(${ALLOC_NAME} PROPERTIES
#     LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
# )
