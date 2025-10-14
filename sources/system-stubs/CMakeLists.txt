cmake_minimum_required(VERSION 3.20)

project(system_stubs LANGUAGES C)

set(INSTALL_PATH /usr/lib)
set(CURRENT_VERSION 1.0.0)
set(COMPAT_VERSION 1.0.0)

set(DYLIBS System.B objc.A)

foreach(DYLIB ${DYLIBS})
    add_library(${DYLIB} SHARED "src/lib${DYLIB}.dylib.m")

    set_target_properties(
        ${DYLIB}
        PROPERTIES
            OSX_ARCHITECTURES "armv6;armv7"
            MACHO_CURRENT_VERSION ${CURRENT_VERSION}
            MACHO_COMPATIBILITY_VERSION ${COMPAT_VERSION}
            POSITION_INDEPENDENT_CODE OFF
            C_STANDARD 99
    )

    target_compile_options(
        ${DYLIB}
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

    target_link_options(
        ${DYLIB}
        PRIVATE
            -dead_strip
            -dead_strip_dylibs
            -dylib
            -single_module
            -dynamic
            -twolevel_namespace
            -twolevel_namespace_hints
            -install_name
            "${INSTALL_PATH}/$<TARGET_FILE_NAME:${DYLIB}>"
            -nostdlib
    )

    install(TARGETS ${DYLIB} LIBRARY DESTINATION lib)

    string(REGEX REPLACE "\\..*$" "" BASE_NAME ${DYLIB})

    # Also install as non canonical lib name.
    # Ideally, this would be symlinked but that's flaky on windows.
    install(FILES $<TARGET_FILE:${DYLIB}> DESTINATION lib RENAME lib${BASE_NAME}.dylib)
endforeach(DYLIB ${DYLIBS})