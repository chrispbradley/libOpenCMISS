cmake_path(SET _DIRECTORY_PATH "${OpenCMISS_OPENCMISS_PYTHON_PY}")
cmake_path(REMOVE_FILENAME _DIRECTORY_PATH)
file(MAKE_DIRECTORY "${_DIRECTORY_PATH}")
unset(_DIRECTORY_PATH)
execute_process(
  COMMAND "${OpenCMISS_Python_EXECUTABLE}" generate_bindings "${OpenCMISS_ROOT}" Python "${OpenCMISS_Python_MODULE_NAME}" "${OpenCMISS_OPENCMISS_PYTHON_PY}" 
  RESULT_VARIABLE OpenCMISS_Python_RESULT_VAR
  OUTPUT_VARIABLE OpenCMISS_Python_OUTPUT_VAR
  ERROR_VARIABLE OpenCMISS_Python_ERROR_VAR
  WORKING_DIRECTORY ${OpenCMISS_BINDINGS_DIR}
)
if(NOT OpenCMISS_Python_RESULT_VAR EQUAL 0)
  message(STATUS "Generate Python module file failed.")
  message(STATUS "  Result: '${OpenCMISS_Python_RESULT_VAR}'")
  message(STATUS "  Output: '${OpenCMISS_Python_OUTPUT_VAR}'")
  message(STATUS "  Error: '${OpenCMISS_Python_ERROR_VAR}'")
endif()
