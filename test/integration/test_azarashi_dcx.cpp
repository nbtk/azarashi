// test/integration/test_azarashi_dcx.cpp
// MT=44 DCX の azarashi 比較テスト（データ駆動）
// azarashi v0.16.1 のデコード結果と照合

#include "../test_helpers.h"
#include "doctest.h"
#include <cstring>
#include <string>

using namespace azaraC;

// ═══════════════════════════════════════════════════════════════════════════════
// DCX NULL Message — test_dcx
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("DCX: Null Message") {
    Message msg{};
    const char* nmea = "$QZQSM,55,53B0840DE0000000000000000000000000000000000000000000000012ACBD4*0E";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 44);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::NullMessage);
    CHECK(msg.mt44.is_null_message == true);
}

// ═══════════════════════════════════════════════════════════════════════════════
// DCX Outside Japan — test_dcx (Fiji, Tsunami)
// azarashi: a2=71(Fiji), a4=44(GEO/Tsunami), a5=3(Extreme), vn=16
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("DCX: Outside Japan - Fiji Tsunami") {
    Message msg{};
    const char* nmea = "$QZQSM,56,9AB08408E0598969E00066AFFE8E6F70091200000000000000000100CD1A410*0C";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 44);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::OutsideJapan);
    CHECK(msg.mt44.camf.a2 == 71);   // Fiji
    CHECK(msg.mt44.camf.a3 == 0);    // Undefined Provider
    CHECK(msg.mt44.camf.a5 == 3);    // Extreme severity
    CHECK(msg.mt44.ex_outside.vn == 16); // version 16
}

// ═══════════════════════════════════════════════════════════════════════════════
// DCX L-Alert — test_dcx
// azarashi: a2=111(Japan), a3=1(Foundation for MultiMedia Communications),
//           a4=1(CBRNE/Air strike), a5=0(Unknown), ex1=1101(札幌市中央区), vn=1
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("DCX: L-Alert - CBRNE Air Strike") {
    Message msg{};
    const char* nmea = "$QZQSM,55,9AB0840DE10208ADE0000000000000000000011340000000000000132F0D238*04";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 44);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::LAlert);
    CHECK(msg.mt44.camf.a2 == 111);  // Japan
    CHECK(msg.mt44.camf.a3 == 1);    // Foundation for MultiMedia Communications
    CHECK(msg.mt44.ex_lalert_local.ex1 == 1101); // Chuo-ku, Sapporo-shi
    CHECK(msg.mt44.ex_lalert_local.vn == 1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// DCX J-Alert — test_dcx
// azarashi: a2=111(Japan), a3=3(Related Ministries),
//           a4=8(CBRNE/Missile attack), a5=3(Extreme), vn=1
//           ex9: 全47都道府県
// ═══════════════════════════════════════════════════════════════════════════════

TEST_CASE("DCX: J-Alert - Missile Attack") {
    Message msg{};
    const char* nmea = "$QZQSM,55,53B0840DE31188FC208600000000000000001FFFFFFFFFFFC00000120738628*00";
    REQUIRE(decodeNmea(nmea, msg));
    CHECK(msg.msg_type == 44);
    CHECK(msg.payload_type == MsgPayloadType::Mt44);
    CHECK(msg.mt44.service_kind == Mt44ServiceKind::JAlert);
    CHECK(msg.mt44.camf.a2 == 111);  // Japan
    CHECK(msg.mt44.camf.a3 == 3);    // Related Ministries (FDMA -> J-Alert)
    CHECK(msg.mt44.camf.a5 == 3);    // Extreme severity
    CHECK(msg.mt44.ex_jalert.vn == 1);
}
