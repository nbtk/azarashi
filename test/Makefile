# test/Makefile — ホストビルド (ESP32不要)
# 新しいディレクトリ構造に対応

CXX      = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -I../include -I. -DARDUINO=0 -DAZARAC_LANG_JA=1 -DAZARAC_LANG_EN=1 -g -MMD -MP

# MinGW-w64 bin path (override on command line if needed, e.g. make MINGW64_BIN=C:\mingw64\bin)
MINGW64_BIN ?= D:\apps\mingw64\bin

# OS detection
ifeq ($(OS),Windows_NT)
  TEST_BIN   = run_tests.exe
  RUN_PREFIX =
  RM         = cmd /c del /F /Q
  ifneq ($(MINGW64_BIN),)
    export PATH := $(PATH);$(MINGW64_BIN)
  endif
else
  TEST_BIN   = run_tests
  RUN_PREFIX = ./
  RM         = rm -f
endif

# Test sources (機能別ディレクトリ)
TEST_SRCS = \
	test_main.cpp \
	core/test_core.cpp \
	decoder/test_qzqsm.cpp \
	decoder/test_dcx.cpp \
	framer/test_framer.cpp \
	framer/test_ublox_azarashi.cpp \
	json/test_json.cpp \
	integration/test_parser.cpp \
	integration/test_nankai.cpp \
	integration/test_azarashi.cpp \
	integration/test_azarashi_dcr.cpp \
	integration/test_azarashi_dcx.cpp

# Library sources (src/ 配下の実装ファイル)
LIB_SRCS = \
	../src/Parser.cpp \
	../src/decoder/Decoder.cpp \
	../src/decoder/DecoderDcx.cpp \
	../src/decoder/DecoderQzqsm.cpp \
	../src/framer/UbxFramer.cpp \
	../src/framer/NmeaFramer.cpp \
	../src/json/JsonWriter.cpp \
	../src/json/JsonSerializer.cpp \
	../src/json/JsonSerializerDcx.cpp \
	../src/json/JsonSerializerQzqsm.cpp \
	../src/helper/DcxHelper.cpp \
	../src/helper/Dedup.cpp

# Object files
OBJS = $(TEST_SRCS:.cpp=.o) $(notdir $(LIB_SRCS:.cpp=.o))

.PHONY: all clean run

all: $(TEST_BIN)

# Rule to build the test binary
$(TEST_BIN): $(OBJS)
	$(CXX) $(CXXFLAGS) $^ -o $@ -Wl,--stack,33554432

# Pattern rules for test sources
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Pattern rules for library sources
%.o: ../src/%.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

%.o: ../src/decoder/%.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

%.o: ../src/framer/%.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

%.o: ../src/json/%.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

%.o: ../src/helper/%.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

run: all
	$(RUN_PREFIX)$(TEST_BIN)

-include $(OBJS:.o=.d)
clean:
	-$(RM) $(TEST_BIN) *.o *.exe *.d
