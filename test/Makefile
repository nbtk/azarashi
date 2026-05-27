# test/Makefile — ホストビルド (ESP32不要)
CXX      = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -I../src -I../src/internal -DARDUINO=0 -g -MMD -MP

# OS detection
ifeq ($(OS),Windows_NT)
  TEST_BIN   = run_tests.exe
  RUN_PREFIX =
  RM         = del /F /Q
else
  TEST_BIN   = run_tests
  RUN_PREFIX = ./
  RM         = rm -f
endif

# Test executable

# Test sources
TEST_SRCS = \
	test_main.cpp \
	test_crc.cpp \
	test_time.cpp \
	test_latlon.cpp \
	test_json.cpp \
	test_framer.cpp \
	test_tsunami.cpp \
	test_azarashi.cpp \
	test_ublox.cpp \
	test_decoder.cpp \
	test_typhoon_marine.cpp \
	test_coverage.cpp \
	test_dcx_helper.cpp \
	test_dedup.cpp

# Library sources
LIB_SRCS = \
	../src/Parser.cpp \
	../src/internal/Decoder.cpp \
	../src/internal/DecoderDcx.cpp \
	../src/internal/DecoderQzqsm.cpp \
	../src/internal/DcxHelper.cpp \
	../src/internal/JsonWriter.cpp \
	../src/internal/JsonSerializer.cpp \
	../src/internal/JsonSerializerDcx.cpp \
	../src/internal/JsonSerializerQzqsm.cpp \
	../src/internal/Dedup.cpp \
	../src/internal/UbxFramer.cpp \
	../src/internal/NmeaFramer.cpp

# Object files (compiled in current dir to avoid cluttering src/)
OBJS = $(TEST_SRCS:.cpp=.o) $(notdir $(LIB_SRCS:.cpp=.o))

.PHONY: all clean run

all: $(TEST_BIN)

# Rule to build the test binary
$(TEST_BIN): $(OBJS)
	$(CXX) $(CXXFLAGS) $^ -o $@

# Pattern rules for test sources
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Pattern rules for library sources
%.o: ../src/%.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

%.o: ../src/internal/%.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

run: all
	$(RUN_PREFIX)$(TEST_BIN)

-include $(OBJS:.o=.d)
clean:
	-$(RM) $(TEST_BIN) *.o *.exe *.d
