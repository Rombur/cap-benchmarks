cmake_minimum_required(VERSION 3.1)

project(benchmark LANGUAGES CXX VERSION ${Cap_VERSION})

find_package(Cap REQUIRED PATHS /opt/cap)

add_executable(test_exact_transient_solution-2
  test_exact_transient_solution-2.cc)

set_target_properties(test_exact_transient_solution-2 PROPERTIES
    CXX_STANDARD 14
    CXX_STANDARD_REQUIRED ON
)

include(/opt/cap/lib/cmake/Cap/CapTargets.cmake)

target_link_libraries(test_exact_transient_solution-2 Cap)
