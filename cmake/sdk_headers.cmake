find_package(Python3 3.12 REQUIRED)

set(VENV_DIR "${CMAKE_BINARY_DIR}/.venv")

if(WIN32)
    set(VENV_BIN_DIR "${VENV_DIR}/Scripts")
else()
    set(VENV_BIN_DIR "${VENV_DIR}/bin")
endif()

add_custom_command(
    OUTPUT ${VENV_DIR}/pyvenv.cfg
    COMMAND ${Python3_EXECUTABLE} -m venv ${VENV_DIR}
    COMMENT "Creating virtual environment"
)

add_custom_target(venv DEPENDS ${VENV_DIR}/pyvenv.cfg)

add_custom_command(
    OUTPUT ${VENV_DIR}/requirements_installed
    COMMAND ${VENV_BIN_DIR}/pip install -r ${HEADERS_SOURCE}/requirements.txt
    COMMAND ${CMAKE_COMMAND} -E touch ${VENV_DIR}/requirements_installed
    DEPENDS venv ${HEADERS_SOURCE}/requirements.txt
    COMMENT "Installing Python requirements"
)

add_custom_target(
    install_requirements
    DEPENDS ${VENV_DIR}/requirements_installed
)

add_custom_command(
    OUTPUT ${CMAKE_BINARY_DIR}/headers_extracted
    COMMAND
        ${VENV_BIN_DIR}/python ${HEADERS_SOURCE}/extract_headers.py --config
        ${HEADERS_SOURCE}/header_sources.yaml --patches
        ${HEADERS_SOURCE}/patches
    COMMAND ${CMAKE_COMMAND} -E touch ${CMAKE_BINARY_DIR}/headers_extracted
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    DEPENDS
        install_requirements
        ${HEADERS_SOURCE}/header_sources.yaml
        ${HEADERS_SOURCE}/extract_headers.py
    COMMENT "Extracting headers from OSS sources"
)

add_custom_target(
    setup_headers
    ALL
    DEPENDS ${CMAKE_BINARY_DIR}/headers_extracted
)

install(
    DIRECTORY ${CMAKE_BINARY_DIR}/extracted_headers/usr
    DESTINATION .
    COMPONENT headers
)

install(
    DIRECTORY ${CMAKE_BINARY_DIR}/extracted_headers/System
    DESTINATION .
    COMPONENT headers
)
