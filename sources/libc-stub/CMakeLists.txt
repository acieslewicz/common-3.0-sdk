cmake_minimum_required(VERSION 3.20)

project(libsystem VERSION 1.0.0 LANGUAGES C)

set(LIB_NAME "libSystem.B.dylib")
set(INSTALL_PATH /usr/lib)
set(VERSION 1.0.0)
set(COMPAT_VERSION 1.0.0)

set(LIBSYSTEM_SOURCES
    libc_stub.c
)

add_library(${LIB_NAME} SHARED ${LIBSYSTEM_SOURCES})

set_target_properties(${LIB_NAME} PROPERTIES
    OUTPUT_NAME "System.B"
    OSX_ARCHITECTURES "armv6;armv7"
    MACHO_COMPATIBILITY_VERSION ${COMPAT_VERSION}
    MACHO_CURRENT_VERSION ${VERSION} 
    POSITION_INDEPENDENT_CODE OFF
    C_STANDARD 99
)

target_compile_options(${LIB_NAME} 
    PRIVATE
        -mthumb
        -Xclang
        -mframe-pointer=none
        -nostdlib
        -fno-builtin
        -fno-stack-protector
        -Wno-deprecated-non-prototype
        -Wno-expansion-to-defined 
)

target_link_options(${LIB_NAME}
    PRIVATE
        -dead_strip
        -dead_strip_dylibs
        -dylib
        -single_module
        -dynamic
        -twolevel_namespace
        -twolevel_namespace_hints
        -install_name
        ${INSTALL_PATH}/${LIB_NAME}
        -nostdlib
)

install(TARGETS ${LIB_NAME}
    LIBRARY DESTINATION lib
)

# Also install as libSystem.dylib.
# Ideally, this would be symlinked but that's flaky on windows.
install(FILES $<TARGET_FILE:${LIB_NAME}>
    DESTINATION lib
    RENAME libSystem.dylib
)