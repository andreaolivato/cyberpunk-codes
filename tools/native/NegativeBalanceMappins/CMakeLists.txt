cmake_minimum_required(VERSION 3.21)
project(NegativeBalanceMappins LANGUAGES CXX ASM_MASM)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

option(RED4EXT_HEADER_ONLY "" ON)
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../vendor/RED4ext.SDK" RED4ext.SDK)

add_library(${PROJECT_NAME} SHARED src/Main.cpp src/Hook.asm)
target_link_libraries(${PROJECT_NAME} PRIVATE RED4ext::SDK)
target_compile_definitions(${PROJECT_NAME} PRIVATE WINVER=0x0A00 NOMINMAX WIN32_LEAN_AND_MEAN)
set_target_properties(${PROJECT_NAME} PROPERTIES OUTPUT_NAME "NegativeBalanceMappins")
