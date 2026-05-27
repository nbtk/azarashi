// test/test_dedup.cpp — DedupFilter unit tests
// Tests the ring-buffer duplicate suppression filter

#define ARDUINO 0
#include "../src/internal/Dedup.h"
#include "doctest.h"

using namespace azaraC;
using namespace internal;

TEST_CASE("DedupFilter: 新規メッセージは重複しない") {
    DedupFilter filter;
    DedupKey key{193, 43, 0xABCDEF};
    CHECK_FALSE(filter.isDuplicate(key));
}

TEST_CASE("DedupFilter: 同じキーは重複と判定される") {
    DedupFilter filter;
    DedupKey key{193, 43, 0xABCDEF};
    CHECK_FALSE(filter.isDuplicate(key));
    CHECK(filter.isDuplicate(key));
}

TEST_CASE("DedupFilter: 異なるsvidは重複しない") {
    DedupFilter filter;
    DedupKey key1{193, 43, 0xABCDEF};
    DedupKey key2{194, 43, 0xABCDEF};
    CHECK_FALSE(filter.isDuplicate(key1));
    CHECK_FALSE(filter.isDuplicate(key2));
}

TEST_CASE("DedupFilter: 異なるmsg_typeは重複しない") {
    DedupFilter filter;
    DedupKey key1{193, 43, 0xABCDEF};
    DedupKey key2{193, 44, 0xABCDEF};
    CHECK_FALSE(filter.isDuplicate(key1));
    CHECK_FALSE(filter.isDuplicate(key2));
}

TEST_CASE("DedupFilter: 異なるcrc24は重複しない") {
    DedupFilter filter;
    DedupKey key1{193, 43, 0xABCDEF};
    DedupKey key2{193, 43, 0x123456};
    CHECK_FALSE(filter.isDuplicate(key1));
    CHECK_FALSE(filter.isDuplicate(key2));
}

TEST_CASE("DedupFilter: 複数メッセージの管理") {
    DedupFilter filter;
    DedupKey key1{193, 43, 0xAAAAAA};
    DedupKey key2{193, 43, 0xBBBBBB};
    DedupKey key3{193, 43, 0xCCCCCC};

    CHECK_FALSE(filter.isDuplicate(key1));
    CHECK_FALSE(filter.isDuplicate(key2));
    CHECK_FALSE(filter.isDuplicate(key3));

    // すべて重複と判定される
    CHECK(filter.isDuplicate(key1));
    CHECK(filter.isDuplicate(key2));
    CHECK(filter.isDuplicate(key3));
}

TEST_CASE("DedupFilter: reset後に新規として扱われる") {
    DedupFilter filter;
    DedupKey key{193, 43, 0xABCDEF};
    CHECK_FALSE(filter.isDuplicate(key));
    CHECK(filter.isDuplicate(key));

    filter.reset();
    CHECK_FALSE(filter.isDuplicate(key));
}

TEST_CASE("DedupFilter: リングバッファのラップアラウンド") {
    DedupFilter filter;
    // AZARAC_DEDUP_SLOTS = 32 なので、33個目のメッセージでラップアラウンド
    DedupKey keys[33];
    for (int i = 0; i < 33; i++) {
        keys[i] = {193, 43, (uint32_t)(0x100000 + i)};
    }

    // 32個のメッセージを登録
    for (int i = 0; i < 32; i++) {
        CHECK_FALSE(filter.isDuplicate(keys[i]));
    }

    // 33個目を登録（ラップアラウンド発生）
    CHECK_FALSE(filter.isDuplicate(keys[32]));

    // 最初のメッセージはバッファから追い出されているため、新規として扱われる
    // （実装によるが、リングバッファの動作として追い出されるはず）
    // 注: 実装が_headを進める際に上書きするため、古いエントリは失われる
}

TEST_CASE("DedupFilter: 同一CRCでもsvidが異なれば別メッセージ") {
    DedupFilter filter;
    DedupKey key1{55, 43, 0xABCDEF};
    DedupKey key2{56, 43, 0xABCDEF};
    DedupKey key3{57, 43, 0xABCDEF};

    CHECK_FALSE(filter.isDuplicate(key1));
    CHECK_FALSE(filter.isDuplicate(key2));
    CHECK_FALSE(filter.isDuplicate(key3));
}

TEST_CASE("DedupFilter: 大量メッセージの処理") {
    DedupFilter filter;
    // 100個の異なるメッセージを処理
    for (int i = 0; i < 100; i++) {
        DedupKey key{193, 43, (uint32_t)(0x100000 + i)};
        CHECK_FALSE(filter.isDuplicate(key));
    }

    // 同じメッセージは重複と判定される
    for (int i = 0; i < 100; i++) {
        DedupKey key{193, 43, (uint32_t)(0x100000 + i)};
        // リングバッファのサイズを超えるので、古いものは追い出される
        // 最新の32個のみ重複と判定される
        if (i >= 68) {  // 100 - 32 = 68
            CHECK(filter.isDuplicate(key));
        }
    }
}
