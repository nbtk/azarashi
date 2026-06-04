// test_nankai_multipage.cpp
// Unit tests for Nankai Trough multi-page aggregation

#include <string>
#include <chrono>
#include "doctest.h"
#include "../src/internal/NankaiPageBuffer.h"

using namespace azaraC::internal;

// Helper to get current time in milliseconds (non-Arduino)
static uint32_t currentMillis() {
    auto now = std::chrono::steady_clock::now();
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
        now.time_since_epoch()).count();
    return static_cast<uint32_t>(ms);
}

TEST_CASE("NankaiPageKey equality") {
    NankaiPageKey key1 = {1, 1234567890};
    NankaiPageKey key2 = {1, 1234567890};
    NankaiPageKey key3 = {2, 1234567890};
    NankaiPageKey key4 = {1, 987654321u};
    
    SUBCASE("Same keys are equal") {
        CHECK(key1 == key2);
    }
    
    SUBCASE("Different info_code") {
        CHECK(key1 != key3);
    }
    
    SUBCASE("Different event_time") {
        CHECK(key1 != key4);
    }
    
    SUBCASE("Invalid key") {
        NankaiPageKey invalid = {0, 0};
        CHECK(!invalid.isValid());
    }
}

TEST_CASE("NankaiPageBuffer basic operations") {
    NankaiPageBuffer buffer;
    uint32_t now = currentMillis();
    
    SUBCASE("Initial state") {
        CHECK(buffer.isEmpty());
        CHECK(!buffer.isComplete());
        CHECK(buffer.total_pages == 0);
    }
    
    SUBCASE("Add first page sets total_pages") {
        uint8_t text[18] = {'H', 'e', 'l', 'l', 'o', 0};
        bool result = buffer.addPage(1, 3, text, now);
        
        CHECK(result);
        CHECK(buffer.total_pages == 3);
        CHECK(buffer.received_pages == 1);
        CHECK(!buffer.isComplete());
    }
    
    SUBCASE("Add all pages completes buffer") {
        uint8_t text1[18] = {'P', 'a', 'g', 'e', '1', 0};
        uint8_t text2[18] = {'P', 'a', 'g', 'e', '2', 0};
        uint8_t text3[18] = {'P', 'a', 'g', 'e', '3', 0};
        
        buffer.addPage(1, 3, text1, now);
        buffer.addPage(2, 3, text2, now);
        bool result = buffer.addPage(3, 3, text3, now);
        
        CHECK(result);
        CHECK(buffer.isComplete());
        CHECK(buffer.received_pages == 3);
    }
    
    SUBCASE("Duplicate page is rejected") {
        uint8_t text[18] = {'T', 'e', 's', 't', 0};
        
        buffer.addPage(1, 2, text, now);
        bool result = buffer.addPage(1, 2, text, now);  // Duplicate
        
        CHECK(!result);
        CHECK(buffer.received_pages == 1);
    }
    
    SUBCASE("Invalid page number is rejected") {
        uint8_t text[18] = {'T', 'e', 's', 't', 0};
        
        bool result0 = buffer.addPage(0, 2, text, now);  // Page 0 invalid
        bool result3 = buffer.addPage(3, 2, text, now);  // Page 3 > total_pages
        
        CHECK(!result0);
        CHECK(!result3);
    }
    
    SUBCASE("Mismatched total_pages is rejected") {
        uint8_t text[18] = {'T', 'e', 's', 't', 0};
        
        buffer.addPage(1, 3, text, now);
        bool result = buffer.addPage(2, 2, text, now);  // Different total_pages
        
        CHECK(!result);
    }
}

TEST_CASE("NankaiPageBuffer text aggregation") {
    NankaiPageBuffer buffer;
    uint32_t now = currentMillis();
    
    SUBCASE("Single page text") {
        uint8_t text[18] = {'H', 'e', 'l', 'l', 'o', 0};
        buffer.addPage(1, 1, text, now);
        
        CHECK(buffer.isComplete());
        CHECK(buffer.getTextLength() == 5);
        
        char result[256];
        buffer.getText(result, sizeof(result));
        CHECK(std::string(result) == "Hello");
    }
    
    SUBCASE("Multi-page text concatenation") {
        uint8_t text1[18] = {'P', 'a', 'g', 'e', '1', ' ', 0};
        uint8_t text2[18] = {'P', 'a', 'g', 'e', '2', 0};
        
        buffer.addPage(1, 2, text1, now);
        buffer.addPage(2, 2, text2, now);
        
        CHECK(buffer.isComplete());
        
        char result[256];
        buffer.getText(result, sizeof(result));
        CHECK(std::string(result) == "Page1 Page2");
    }
    
    SUBCASE("Null byte terminates page") {
        uint8_t text[18] = {'A', 'B', 0, 'C', 'D', 0};  // 0x00 at position 2
        buffer.addPage(1, 1, text, now);
        
        CHECK(buffer.getTextLength() == 2);  // Only "AB"
        
        char result[256];
        buffer.getText(result, sizeof(result));
        CHECK(std::string(result) == "AB");
    }
    
    SUBCASE("Empty page handling") {
        uint8_t text1[18] = {'A', 'B', 0};
        uint8_t text2[18] = {0};  // Empty page
        uint8_t text3[18] = {'C', 'D', 0};
        
        buffer.addPage(1, 3, text1, now);
        buffer.addPage(2, 3, text2, now);
        buffer.addPage(3, 3, text3, now);
        
        char result[256];
        buffer.getText(result, sizeof(result));
        CHECK(std::string(result) == "ABCD");
    }
}

TEST_CASE("NankaiPageBuffer clear") {
    NankaiPageBuffer buffer;
    uint32_t now = currentMillis();
    
    SUBCASE("Clear resets buffer") {
        uint8_t text[18] = {'T', 'e', 's', 't', 0};
        buffer.addPage(1, 1, text, now);
        
        CHECK(buffer.isComplete());
        
        buffer.clear();
        
        CHECK(buffer.isEmpty());
        CHECK(buffer.total_pages == 0);
        CHECK(!buffer.isComplete());
    }
}

TEST_CASE("NankaiPageBufferManager") {
    NankaiPageBufferManager manager;
    
    SUBCASE("Add page to new buffer") {
        NankaiPageKey key = {1, 1234567890};
        uint8_t text[18] = {'T', 'e', 's', 't', 0};
        
        NankaiPageBuffer* result = manager.addPage(key, 1, 1, text, currentMillis());
        
        CHECK(result != nullptr);  // Complete immediately (single page)
    }
    
    SUBCASE("Add page to existing buffer") {
        NankaiPageKey key = {1, 1234567890};
        uint8_t text1[18] = {'P', '1', 0};
        uint8_t text2[18] = {'P', '2', 0};
        
        NankaiPageBuffer* result1 = manager.addPage(key, 1, 2, text1, currentMillis());
        CHECK(result1 == nullptr);  // Not complete yet
        
        NankaiPageBuffer* result2 = manager.addPage(key, 2, 2, text2, currentMillis());
        CHECK(result2 != nullptr);  // Complete
    }
    
    SUBCASE("Multiple events") {
        NankaiPageKey key1 = {1, 1234567890};
        NankaiPageKey key2 = {2, 1234567890};
        uint8_t text[18] = {'T', 'e', 's', 't', 0};
        
        manager.addPage(key1, 1, 1, text, currentMillis());
        manager.addPage(key2, 1, 1, text, currentMillis());
        
        CHECK(manager.getBuffer(key1) != nullptr);
        CHECK(manager.getBuffer(key2) != nullptr);
    }
    
    SUBCASE("Clear all buffers") {
        NankaiPageKey key = {1, 1234567890};
        uint8_t text[18] = {'T', 'e', 's', 't', 0};
        
        manager.addPage(key, 1, 1, text, currentMillis());
        manager.clearAll();
        
        CHECK(manager.getBuffer(key) == nullptr);
    }
}

TEST_CASE("NankaiPageBufferManager buffer limit") {
    NankaiPageBufferManager manager;
    
    SUBCASE("Max buffers is 4") {
        uint32_t now = currentMillis();
        // Add 4 different events
        for (uint8_t i = 0; i < 4; i++) {
            NankaiPageKey key = {i, 1234567890};
            uint8_t text[18] = {'T', 'e', 's', 't', 0};
            manager.addPage(key, 1, 1, text, now);
        }
        
        // 5th event should evict oldest
        NankaiPageKey key5 = {4, 1234567890};
        uint8_t text[18] = {'T', 'e', 's', 't', 0};
        manager.addPage(key5, 1, 1, text, now);
        
        // First event should be evicted
        NankaiPageKey key0 = {0, 1234567890};
        CHECK(manager.getBuffer(key0) == nullptr);
        
        // 5th event should exist
        CHECK(manager.getBuffer(key5) != nullptr);
    }
}

TEST_CASE("UTF-8 text handling") {
    NankaiPageBuffer buffer;
    uint32_t now = currentMillis();
    
    SUBCASE("Japanese text") {
        // "こんにちは" in UTF-8 (15 bytes)
        uint8_t text[18] = {
            0xE3, 0x81, 0x93,  // こ
            0xE3, 0x82, 0x93,  // ん
            0xE3, 0x81, 0xAB,  // に
            0xE3, 0x81, 0xA1,  // ち
            0xE3, 0x81, 0xAF,  // は
            0x00
        };
        
        buffer.addPage(1, 1, text, now);
        
        CHECK(buffer.getTextLength() == 15);
        
        char result[256];
        buffer.getText(result, sizeof(result));
        CHECK(std::string(result) == "こんにちは");
    }
    
    SUBCASE("Multi-page Japanese text") {
        // Split "南海トラフ地震" across two pages
        uint8_t text1[18] = {
            0xE5, 0x8D, 0x97,  // 南
            0xE6, 0xB5, 0xB7,  // 海
            0xE3, 0x83, 0x88,  // ト
            0xE3, 0x83, 0xA9,  // ラ
            0x00
        };
        
        uint8_t text2[18] = {
            0xE3, 0x83, 0x95,  // フ
            0xE5, 0x9C, 0xB0,  // 地
            0xE9, 0x9C, 0x87,  // 震
            0x00
        };
        
        buffer.addPage(1, 2, text1, now);
        buffer.addPage(2, 2, text2, now);
        
        char result[256];
        buffer.getText(result, sizeof(result));
        CHECK(std::string(result) == "南海トラフ地震");
    }
}
