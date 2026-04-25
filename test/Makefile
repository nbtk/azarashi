# test/Makefile — ホストビルド (ESP32不要)
CXX      = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -I../src -I../src/internal -DARDUINO=0
TESTS    = test_crc test_json test_framer test_tsunami

.PHONY: all clean run

all: $(TESTS)

test_crc: test_crc.cpp \
          ../src/internal/Decoder.cpp \
          ../src/internal/Dedup.cpp
	$(CXX) $(CXXFLAGS) $^ -o $@

test_json: test_json.cpp \
           ../src/Parser.cpp \
           ../src/internal/Decoder.cpp \
           ../src/internal/JsonSerializer.cpp \
           ../src/internal/Dedup.cpp
	$(CXX) $(CXXFLAGS) $^ -o $@

test_framer: test_framer.cpp \
             ../src/internal/UbxFramer.cpp \
             ../src/internal/NmeaFramer.cpp
	$(CXX) $(CXXFLAGS) $^ -o $@

test_tsunami: test_tsunami.cpp \
              ../src/internal/Decoder.cpp \
              ../src/internal/Dedup.cpp
	$(CXX) $(CXXFLAGS) $^ -o $@

run: all
	./test_crc
	./test_json
	./test_framer
	./test_tsunami

clean:
	rm -f $(TESTS)
