# test/Makefile — ホストビルド (ESP32不要)
CXX      = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -I../src -I../src/internal -DARDUINO=0
TESTS    = test_crc test_json

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

run: all
	./test_crc
	./test_json

clean:
	rm -f $(TESTS)
