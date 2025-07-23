cmake_minimum_required(VERSION 3.10)
project(MallocVariants)

set(CMAKE_CXX_STANDARD 11)

# enable testing
enable_testing()
# Add custom target to run tests verbosely
add_custom_target(check COMMAND ${CMAKE_CTEST_COMMAND} --verbose)

# Define macros required by the code to enable thread-safety code
add_definitions(-DTHREAD_SAFETY)
# Include CompilerFlags cmake file to add extra warning/error compiler flags
include(CompilerFlags.cmake)
# List of all malloc implementation subdirs

set(MALLOC_DIRS
    # stdmalloc
    dlmalloc
)

# Add a shared library target for each
foreach(dir IN LISTS MALLOC_DIRS)
    add_subdirectory(${dir})
endforeach()
