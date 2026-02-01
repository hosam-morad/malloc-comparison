cmake_minimum_required(VERSION 3.10)
project(MallocVariants)

set(CMAKE_CXX_STANDARD 11)

# Make CMake prefer the right pthread flag on GNU toolchains, etc.
set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

# Link pthreads to all targets created in this directory and subdirectories
# (directory scope; affects targets defined AFTER this line)
link_libraries(Threads::Threads)

# enable testing
enable_testing()
# Add custom target to run tests verbosely
add_custom_target(check COMMAND ${CMAKE_CTEST_COMMAND} --verbose)

# Define macros required by the code to enable thread-safety code
add_definitions(-DTHREAD_SAFETY)
# Include CompilerFlags cmake file to add extra warning/error compiler flags
include(CompilerFlags.cmake)
# List of all malloc implementation subdirs

set(MALLOC_VERSIONS
    # glibcmalloc
    # dlmalloc
    # mimalloc
    malloc-standalone-auto
)

# Extend the Make-only list by prepending or appending ptmalloc2
set(MALLOC_VERSIONS_MAKE ${MALLOC_VERSIONS} ptmalloc2)

# Convert to Make-space-separated format
string(REPLACE ";" " " MALLOC_VERSIONS_MAKE_STR "${MALLOC_VERSIONS_MAKE}")

# Write to a Make-readable file
file(WRITE "${CMAKE_SOURCE_DIR}/versions.mk"
    "MALLOC_VERSIONS := ${MALLOC_VERSIONS_MAKE_STR}\n")

# Place all shared libs in a central location
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})


# Add a shared library target for each
foreach(dir IN LISTS MALLOC_VERSIONS)
    add_subdirectory(${dir})
endforeach()
