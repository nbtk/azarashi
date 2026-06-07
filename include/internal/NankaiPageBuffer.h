#pragma once
// azaraC - src/internal/NankaiPageBuffer.h
// Nankai Trough Earthquake multi-page aggregation buffer

#include <cstdint>
#include <cstring>
#include "TimeFields.h"

namespace azaraC {
namespace internal {

// ---------------------------------------------------------------------------
// NankaiPageKey - Event identifier for page aggregation
// ---------------------------------------------------------------------------
// Note: svid is NOT included in the key because QZSS multiple satellites
// may relay the same message. Using svid would cause duplicate buffers
// for the same event.
// ---------------------------------------------------------------------------
struct NankaiPageKey {
    uint8_t  info_code;        // Information Serial Code (4 bits)
    uint32_t event_time_unix;  // Event time as UNIX timestamp

    bool operator==(const NankaiPageKey& o) const {
        return info_code == o.info_code &&
               event_time_unix == o.event_time_unix;
    }

    bool operator!=(const NankaiPageKey& o) const {
        return !(*this == o);
    }

    bool isValid() const {
        return event_time_unix != 0;
    }

    void clear() {
        info_code = 0;
        event_time_unix = 0;
    }
};

// ---------------------------------------------------------------------------
// NankaiPageBuffer - Page aggregation buffer for single event
// ---------------------------------------------------------------------------
// Specification: Pn/Pm range is 1-63 (6 bits)
// ---------------------------------------------------------------------------
struct NankaiPageBuffer {
    static constexpr uint8_t MAX_PAGES = 63;
    static constexpr uint8_t TEXT_PER_PAGE = 18;
    static constexpr uint32_t TIMEOUT_MS = 60000;  // 60 seconds timeout

    NankaiPageKey key;
    uint8_t total_pages = 0;
    uint8_t received_pages = 0;
    uint8_t text[MAX_PAGES][TEXT_PER_PAGE];
    bool    page_received[MAX_PAGES];
    uint32_t last_update_ms = 0;

    NankaiPageBuffer() {
        clearAll();
    }

    // Add a page to buffer
    // page_num: 1-based page number
    // total_pages: total number of pages (from Pm field)
    // text_data: pointer to 18 bytes of text data
    // current_ms: current timestamp in milliseconds (for consistent time source)
    // Returns true if page was added successfully
    bool addPage(uint8_t page_num, uint8_t total_pages, const uint8_t* text_data, uint32_t current_ms) {
        // Set total_pages on first call
        if (this->total_pages == 0) {
            this->total_pages = total_pages;
        }

        // total_pages must match
        if (this->total_pages != total_pages) {
            return false;
        }

        // Page number range check (1-63)
        if (page_num == 0 || page_num > total_pages) {
            return false;
        }

        // Skip if already received (duplicate check)
        if (page_received[page_num - 1]) {
            return false;
        }

        // Copy text data
        memcpy(text[page_num - 1], text_data, TEXT_PER_PAGE);
        page_received[page_num - 1] = true;
        received_pages++;
        last_update_ms = current_ms;

        return true;
    }

    // Check if all pages have been received
    bool isComplete() const {
        if (total_pages == 0) return false;
        return received_pages >= total_pages;
    }

    // Get combined text as string
    // Stops at first 0x00 byte in each page (null terminator)
    void getText(char* out, uint16_t max_len) const {
        if (!out || max_len == 0) return;

        uint16_t pos = 0;

        for (uint8_t i = 0; i < total_pages && pos < max_len - 1; ++i) {
            if (page_received[i]) {
                for (uint8_t j = 0; j < TEXT_PER_PAGE && pos < max_len - 1; ++j) {
                    if (text[i][j] == 0) {
                        break;  // Null terminator - stop this page
                    }
                    out[pos++] = static_cast<char>(text[i][j]);
                }
            }
        }

        out[pos] = '\0';  // Null terminate
    }

    // Get text length (excluding null terminator)
    uint16_t getTextLength() const {
        uint16_t len = 0;

        for (uint8_t i = 0; i < total_pages; ++i) {
            if (page_received[i]) {
                for (uint8_t j = 0; j < TEXT_PER_PAGE; ++j) {
                    if (text[i][j] == 0) {
                        break;
                    }
                    len++;
                }
            }
        }

        return len;
    }

    // Check if buffer has expired (timeout)
    bool isExpired(uint32_t current_ms) const {
        if (total_pages == 0) return false;
        // uint32_t overflow safe: unsigned arithmetic handles wrap-around
        return (current_ms - last_update_ms) > TIMEOUT_MS;
    }

    // Clear buffer for reuse
    void clear() {
        key.clear();
        total_pages = 0;
        received_pages = 0;
        last_update_ms = 0;
        memset(page_received, 0, sizeof(page_received));
        memset(text, 0, sizeof(text));
    }

    // Clear entire buffer including key
    void clearAll() {
        clear();
        key.clear();
    }

    // Check if buffer is empty (no pages received)
    bool isEmpty() const {
        return total_pages == 0;
    }

    // Check if buffer matches given key
    bool matchesKey(const NankaiPageKey& k) const {
        return key == k;
    }

    // Set key for this buffer
    void setKey(const NankaiPageKey& k) {
        key = k;
    }
};

// ---------------------------------------------------------------------------
// NankaiPageBufferManager - Manages multiple page buffers
// ---------------------------------------------------------------------------
class NankaiPageBufferManager {
public:
    static constexpr uint8_t MAX_BUFFERS = 4;

    NankaiPageBufferManager() {
        for (uint8_t i = 0; i < MAX_BUFFERS; ++i) {
            _buffers[i].clearAll();
        }
    }

    // Add a page to appropriate buffer
    // Returns pointer to completed buffer if all pages received, nullptr otherwise
    NankaiPageBuffer* addPage(const NankaiPageKey& key, uint8_t page_num,
                               uint8_t total_pages, const uint8_t* text_data,
                               uint32_t current_ms) {
        // Expire old buffers
        expireBuffers(current_ms);

        // Find existing buffer for this key
        int8_t idx = findBuffer(key);

        if (idx < 0) {
            // No existing buffer, find empty slot
            idx = findEmptyBuffer();
            if (idx < 0) {
                // No empty slot, use oldest buffer
                idx = findOldestBuffer();
            }
            // Initialize new buffer
            _buffers[idx].clearAll();
            _buffers[idx].setKey(key);
        }

        // Add page to buffer
        if (_buffers[idx].addPage(page_num, total_pages, text_data, current_ms)) {
            // Check if complete
            if (_buffers[idx].isComplete()) {
                return &_buffers[idx];
            }
        }

        return nullptr;
    }

    // Get buffer for given key
    NankaiPageBuffer* getBuffer(const NankaiPageKey& key) {
        int8_t idx = findBuffer(key);
        return (idx >= 0) ? &_buffers[idx] : nullptr;
    }

    // Get buffer for given key (const version)
    const NankaiPageBuffer* getBuffer(const NankaiPageKey& key) const {
        int8_t idx = findBuffer(key);
        return (idx >= 0) ? &_buffers[idx] : nullptr;
    }

    // Clear all buffers
    void clearAll() {
        for (uint8_t i = 0; i < MAX_BUFFERS; ++i) {
            _buffers[i].clearAll();
        }
    }

private:
    NankaiPageBuffer _buffers[MAX_BUFFERS];

    int8_t findBuffer(const NankaiPageKey& key) const {
        for (uint8_t i = 0; i < MAX_BUFFERS; ++i) {
            if (_buffers[i].matchesKey(key)) {
                return i;
            }
        }
        return -1;
    }

    int8_t findEmptyBuffer() {
        for (uint8_t i = 0; i < MAX_BUFFERS; ++i) {
            if (_buffers[i].isEmpty()) {
                return i;
            }
        }
        return -1;
    }

    int8_t findOldestBuffer() {
        uint32_t oldest_ms = UINT32_MAX;
        int8_t oldest_idx = 0;

        for (uint8_t i = 0; i < MAX_BUFFERS; ++i) {
            // Use last_update_ms as proxy for age
            // For empty buffers, this will be 0
            uint32_t update_ms = _buffers[i].isEmpty() ? 0 : _buffers[i].last_update_ms;
            if (update_ms < oldest_ms) {
                oldest_ms = update_ms;
                oldest_idx = i;
            }
        }

        return oldest_idx;
    }

    void expireBuffers(uint32_t current_ms) {
        for (uint8_t i = 0; i < MAX_BUFFERS; ++i) {
            if (!_buffers[i].isEmpty() && _buffers[i].isExpired(current_ms)) {
                _buffers[i].clearAll();
            }
        }
    }
};

} // namespace internal
} // namespace azaraC
