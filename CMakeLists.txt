cmake_minimum_required(VERSION 3.1)

project(benchmark LANGUAGES CXX VERSION ${Cap_VERSION})

find_package(Cap REQUIRED PATHS /opt/cap)

add_executable(test_exact_transient_solution-2
  test_exact_transient_solution-2.cc)
add_executable(charge_curve
  charge_curve.cc)
add_executable(cyclic_voltammetry
  discharge_curve.cc)
add_executable(discharge_curve
  discharge_curve.cc)
add_executable(leakage_current
  leakage_current.cc)
add_executable(lissajous_curve
  lissajous_curve.cc)
add_executable(ragone_chart
  ragone_chart.cc)

set_target_properties(test_exact_transient_solution-2 PROPERTIES
    CXX_STANDARD 14
    CXX_STANDARD_REQUIRED ON
)
set_target_properties(charge_curve PROPERTIES
    CXX_STANDARD 14
    CXX_STANDARD_REQUIRED ON
)
set_target_properties(cyclic_voltammetry PROPERTIES
    CXX_STANDARD 14
    CXX_STANDARD_REQUIRED ON
)
set_target_properties(discharge_curve PROPERTIES
    CXX_STANDARD 14
    CXX_STANDARD_REQUIRED ON
)
set_target_properties(leakage_current PROPERTIES
    CXX_STANDARD 14
    CXX_STANDARD_REQUIRED ON
)
set_target_properties(lissajous_curve PROPERTIES
    CXX_STANDARD 14
    CXX_STANDARD_REQUIRED ON
)
set_target_properties(ragone_chart PROPERTIES
    CXX_STANDARD 14
    CXX_STANDARD_REQUIRED ON
)

include(/opt/cap/lib/cmake/Cap/CapTargets.cmake)

target_link_libraries(test_exact_transient_solution-2 Cap)
target_link_libraries(charge_curve Cap)
target_link_libraries(cyclic_voltammetry Cap)
target_link_libraries(discharge_curve Cap)
target_link_libraries(leakage_current Cap)
target_link_libraries(lissajous_curve Cap)
target_link_libraries(ragone_chart Cap)
