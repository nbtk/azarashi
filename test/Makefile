# test/Makefile — ホストビルド

CXX      = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -I../include -I. -DARDUINO=0 -DAZARAC_LANG_JA=1 -DAZARAC_LANG_EN=1 -g -MMD -MP

# MinGW-w64 bin path (override on command line if needed, e.g. make MINGW64_BIN=C:\mingw64\bin)
MINGW64_BIN ?= D:\apps\mingw64\bin

# OS detection
ifeq ($(OS),Windows_NT)
  TEST_BIN   = run_tests.exe
  RUN_PREFIX =
  RM         = cmd /c "del /F /Q"
  ifneq ($(MINGW64_BIN),)
    export PATH := $(PATH);$(MINGW64_BIN)
  endif
  LDFLAGS = -Wl,--stack,33554432
else
  TEST_BIN   = run_tests
  RUN_PREFIX = ./
  RM         = rm -f
  LDFLAGS =
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

# Object files - サブディレクトリの.oはそのまま保持、ライブラリはカレントに
TEST_OBJS = $(TEST_SRCS:.cpp=.o)
LIB_OBJS = $(notdir $(LIB_SRCS:.cpp=.o))
OBJS = $(TEST_OBJS) $(LIB_OBJS)

# VPATH for library sources
VPATH = ../src:../src/decoder:../src/framer:../src/json:../src/helper

.PHONY: all clean run fuzz

all: $(TEST_BIN)

# Rule to build the test binary
$(TEST_BIN): $(OBJS)
	$(CXX) $(CXXFLAGS) $^ -o $@ $(LDFLAGS)

# Pattern rules for test sources (サブディレクトリ対応)
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

run: all
	$(RUN_PREFIX)$(TEST_BIN)

# Fuzz target
FUZZ_BIN = fuzz_decoder
FUZZ_SRCS = fuzz/fuzz_decoder.cpp
FUZZ_OBJS = $(FUZZ_SRCS:.cpp=.o)

fuzz: $(FUZZ_BIN)
	$(RUN_PREFIX)$(FUZZ_BIN)

$(FUZZ_BIN): $(FUZZ_OBJS) $(LIB_OBJS)
	$(CXX) $(CXXFLAGS) $^ -o $@ $(LDFLAGS)

# Include dependency files
-include $(TEST_OBJS:.o=.d) $(LIB_OBJS:.o=.d) $(FUZZ_OBJS:.o=.d)

clean:
	-$(RM) *.o *.exe *.d
	-$(RM) core\*.o core\*.d
	-$(RM) decoder\*.o decoder\*.d
	-$(RM) framer\*.o framer\*.d
	-$(RM) json\*.o json\*.d
	-$(RM) integration\*.o integration\*.d
	-$(RM) fuzz\*.o fuzz\*.d
