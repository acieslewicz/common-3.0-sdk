cmake_minimum_required(VERSION 3.20)

set(CMAKE_GENERATOR "Ninja")

project(common-3.0-sdk)

if(
    NOT CMAKE_C_COMPILER_ID STREQUAL "Clang"
    OR NOT CMAKE_CXX_COMPILER_ID STREQUAL "Clang"
)
    message(FATAL_ERROR "LLVM Clang required for building target's components.")
endif()

if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
    set_property(
        CACHE CMAKE_INSTALL_PREFIX
        PROPERTY VALUE "${CMAKE_BINARY_DIR}/common-3.0.sdk"
    )
endif()

set(SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/sources")
set(CSU_SOURCE "${CMAKE_CURRENT_SOURCE_DIR}/sources/csu")
set(HEADERS_SOURCE "${CMAKE_CURRENT_SOURCE_DIR}/sources/sdk-headers")

set(TOOLCHAIN_FILE
    "${CMAKE_CURRENT_SOURCE_DIR}/common-3.0.sdk/cmake/Toolchain/common-3.0.cmake"
    CACHE FILEPATH
    "Path to the toolchain file"
)

if(NOT EXISTS ${TOOLCHAIN_FILE})
    message(FATAL_ERROR "Toolchain file not found: ${TOOLCHAIN_FILE}")
endif()

include(${CMAKE_CURRENT_LIST_DIR}/cmake/sdk_headers.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/cmake/extra_headers.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/cmake/cctools_port.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/cmake/csu.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/cmake/sdk_libs.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/cmake/system_stubs.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/cmake/cmake_toolchain.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/cmake/licenses.cmake)
