// azaraC - src/internal/DecoderDcx.cpp
// MT=44 DCX / CAMF decoder (IS-QZSS-DCX-003)

#include "Decoder.h"
#include "DcxHelper.h"
#include <cstring>
#include <cmath>

namespace azaraC {
namespace internal {

// ---------------------------------------------------------------------------
// MT=44 DCX / CAMF  (IS-QZSS-DCX-003)
// ---------------------------------------------------------------------------
bool Decoder::decodeDcx(const uint8_t* bits, Message& out, uint32_t report_unix) {
    out.payload_type = MsgPayloadType::Mt44;
    Mt44Data& d = out.mt44;

    d.service_kind = Mt44ServiceKind::Unknown;
    d.is_null_message = false;
    d.ex_kind = ExtendedKind::None;

    // SD (Satellite Designation)
    d.sd.sdmt = getBits(bits, 14, 1);
    d.sd.sdm  = getBits(bits, 15, 9);

    // CAMF (A1 - A18)
    d.camf.a1  = getBits(bits, 24, 2);
    d.camf.a2  = getBits(bits, 26, 9);
    d.camf.a3  = getBits(bits, 35, 5);
    d.camf.a4  = getBits(bits, 40, 7);
    d.camf.a5  = getBits(bits, 47, 2);
    d.camf.a6  = getBits(bits, 49, 1);
    d.camf.a7  = getBits(bits, 50, 14);
    d.camf.a8  = getBits(bits, 64, 2);
    d.camf.a9  = getBits(bits, 66, 1);
    d.camf.a10 = getBits(bits, 67, 3);
    d.camf.a11 = getBits(bits, 70, 10);
    // A12/A13: unsigned codes decoded via formula (not two's complement)
    d.camf.a12 = getBits(bits, 80, 16);
    d.camf.a13 = getBits(bits, 96, 17);
    d.camf.a14 = getBits(bits, 113, 5);
    d.camf.a15 = getBits(bits, 118, 5);
    d.camf.a16 = getBits(bits, 123, 6);
    d.camf.a17 = getBits(bits, 129, 2);
    d.camf.a18 = getBits(bits, 131, 15);

    // Null Message Check (IS-QZSS-DCX-003 §4.3)
    // All fields except PAB, MT, SD, Reserved, CRC must be 0
    // A2 must be Japan (001101111 = 111), A3 must be 0
    if (d.camf.a1 == 0 && d.camf.a2 == 111 && d.camf.a3 == 0 &&
        d.camf.a4 == 0 && d.camf.a5 == 0 && d.camf.a6 == 0 &&
        d.camf.a7 == 0 && d.camf.a8 == 0 && d.camf.a9 == 0 &&
        d.camf.a10 == 0 && d.camf.a11 == 0 &&
        d.camf.a12 == 0 && d.camf.a13 == 0 && d.camf.a14 == 0 &&
        d.camf.a15 == 0 && d.camf.a16 == 0 && d.camf.a17 == 0 &&
        d.camf.a18 == 0) {
        // Extended Message must also be all 0 (bits 146..219 = 74 bits)
        // Check using getBits for correctness
        uint32_t ex_part1 = getBits(bits, 146, 32);  // bits 146..177
        uint32_t ex_part2 = getBits(bits, 178, 32);  // bits 178..209
        uint32_t ex_part3 = getBits(bits, 210, 10);  // bits 210..219
        if (ex_part1 == 0 && ex_part2 == 0 && ex_part3 == 0) {
            d.is_null_message = true;
            d.service_kind = Mt44ServiceKind::NullMessage;
            d.ex_kind = ExtendedKind::None;
            out.valid = true;
            return true;
        }
    }

    // Resolve onset time from GPS week-mod-4 + minute-of-week
    // Use report_unix (GPS time from receiver) for accurate onset calculation
    if (d.camf.a7 > 0 && d.camf.a7 <= 10080 && report_unix > 315964800u) {
        // GPS epoch 1980-01-06 00:00:00 UTC, +18 leap seconds (post-2017)
        uint32_t gps  = report_unix - 315964800u + 18u;
        uint32_t week = gps / 604800u;
        int32_t diff = (int32_t)(d.camf.a6 & 3u) - (int32_t)(week & 3u);
        if (diff < -2) diff += 4;
        else if (diff > 1) diff -= 4;
        uint32_t base = week + diff;

        uint32_t gps_onset = base * 604800u + (uint32_t)(d.camf.a7 - 1u) * 60u;
        uint32_t unix = gps_onset + 315964800u - 18u;
        d.onset_time.unix_time = unix;

        uint32_t y, m, d2;
        Decoder::civil_from_days(unix / 86400u, y, m, d2);
        d.onset_time.day    = d2;
        d.onset_time.hour   = ((d.camf.a7 - 1u) % 1440u) / 60u;
        d.onset_time.minute = (d.camf.a7 - 1u) % 60u;
    }

    // Determine Service Kind based on A2 and A3
    if (d.camf.a2 != 111) { // 111 = 001101111 = Japan
        d.service_kind = Mt44ServiceKind::OutsideJapan;
        d.ex_kind = ExtendedKind::OutsideJapan;
    } else {
        if (d.camf.a3 == 1) {
            d.service_kind = Mt44ServiceKind::LAlert;
            d.ex_kind = ExtendedKind::LAlertOrLocal;
        } else if (d.camf.a3 == 2 || d.camf.a3 == 3) {
            d.service_kind = Mt44ServiceKind::JAlert;
            d.ex_kind = ExtendedKind::JAlert;
        } else if (d.camf.a3 == 4) {
            d.service_kind = Mt44ServiceKind::LocalGovernment;
            d.ex_kind = ExtendedKind::LAlertOrLocal;
        } else {
            // Discard message
            return false;
        }
    }

    // Parse Extended Message
    if (d.ex_kind == ExtendedKind::LAlertOrLocal) {
        d.ex_lalert_local.ex1 = getBits(bits, 146, 16);
        d.ex_lalert_local.ex2 = getBits(bits, 162, 1);
        // EX3/EX4: unsigned codes (latitude/longitude formulas, not two's complement)
        d.ex_lalert_local.ex3 = getBits(bits, 163, 17);
        d.ex_lalert_local.ex4 = getBits(bits, 180, 17);
        d.ex_lalert_local.ex5 = getBits(bits, 197, 5);
        d.ex_lalert_local.ex6 = getBits(bits, 202, 5);
        d.ex_lalert_local.ex7 = getBits(bits, 207, 7);
        d.ex_lalert_local.vn  = getBits(bits, 214, 6);
    } else if (d.ex_kind == ExtendedKind::JAlert) {
        d.ex_jalert.ex8  = getBits(bits, 146, 1);
        uint32_t ex9_hi = getBits(bits, 147, 32);
        uint32_t ex9_lo = getBits(bits, 179, 32);
        d.ex_jalert.ex9  = ((uint64_t)ex9_hi << 32) | ex9_lo;
        d.ex_jalert.ex10 = getBits(bits, 211, 3);
        d.ex_jalert.vn   = getBits(bits, 214, 6);
    } else if (d.ex_kind == ExtendedKind::OutsideJapan) {
        for (int i = 0; i < 8; ++i) {
            d.ex_outside.ex11_raw[i] = getBits(bits, 146 + i * 8, 8);
        }
        d.ex_outside.ex11_raw[8] = getBits(bits, 210, 4) << 4; // remaining 4 bits
        d.ex_outside.vn = getBits(bits, 214, 6);
    }

    // ---------------------------------------------------------------------------
    // Populate decoded structures (IS-QZSS-DCX-003 §15.2)
    // ---------------------------------------------------------------------------

    azaraC::Mt44Decoded& dec = d.mt44_decoded;
    dec.service_kind = d.service_kind;
    dec.is_null_message = d.is_null_message;
    dec.country_name = nullptr;
    dec.provider_name = nullptr;
    dec.hazard_name = nullptr;
    dec.severity_name = nullptr;
    dec.guidance_text = nullptr;
    dec.main_ellipse_present = false;
    dec.target_area_code_present = false;
    dec.jalert_prefecture_mode = false;
    dec.prefecture_count = 0;
    dec.city_code_count = 0;
    dec.additional_area.present = false;

    // Alert identity (IS-QZSS-DCX-003 §4.2.3.1)
    dec.alert_identity.a2 = d.camf.a2;
    dec.alert_identity.a3 = d.camf.a3;
    dec.alert_identity.a4 = d.camf.a4;
    dec.alert_identity.ex1 = 0;

    if (d.is_null_message) {
        out.valid = true;
        return true;
    }

    // Main ellipse (A12-A16): present if any of A12..A16 is non-zero
    bool has_main_ellipse = (d.camf.a12 != 0 || d.camf.a13 != 0 ||
                             d.camf.a14 != 0 || d.camf.a15 != 0 ||
                             d.camf.a16 != 0);
    if (has_main_ellipse) {
        dec.main_ellipse_present = true;
        dec.main_ellipse.lat_deg = decodeLatitude16(d.camf.a12);
        dec.main_ellipse.lon_deg = decodeLongitude17(d.camf.a13);
        dec.main_ellipse.semi_major_km = decodeRadiusCode(d.camf.a14);
        dec.main_ellipse.semi_minor_km = decodeRadiusCode(d.camf.a15);
        dec.main_ellipse.azimuth_deg = decodeAzimuth6(d.camf.a16);
    }

    if (d.ex_kind == ExtendedKind::LAlertOrLocal) {
        dec.alert_identity.ex1 = d.ex_lalert_local.ex1;

        // Target area code (EX1): used when main ellipse is absent
        if (!has_main_ellipse && d.ex_lalert_local.ex1 != 0) {
            dec.target_area_code_present = true;
            dec.target_area_code = d.ex_lalert_local.ex1;
        }

        // Additional area (local government only): EX2-EX7
        if (d.service_kind == Mt44ServiceKind::LocalGovernment) {
            bool has_additional = (d.ex_lalert_local.ex2 != 0 ||
                                   d.ex_lalert_local.ex3 != 0 ||
                                   d.ex_lalert_local.ex4 != 0 ||
                                   d.ex_lalert_local.ex5 != 0 ||
                                   d.ex_lalert_local.ex6 != 0 ||
                                   d.ex_lalert_local.ex7 != 0);
            if (has_additional) {
                dec.additional_area.present = true;
                dec.additional_area.head_to_area = (d.ex_lalert_local.ex2 != 0);
                dec.additional_area.ellipse.lat_deg = decodeLatitude17(d.ex_lalert_local.ex3);
                dec.additional_area.ellipse.lon_deg = decodeLongitude17_45_225(d.ex_lalert_local.ex4);
                dec.additional_area.ellipse.semi_major_km = decodeRadiusCode(d.ex_lalert_local.ex5);
                dec.additional_area.ellipse.semi_minor_km = decodeRadiusCode(d.ex_lalert_local.ex6);
                dec.additional_area.ellipse.azimuth_deg = decodeAzimuth7(d.ex_lalert_local.ex7);
            }
        }
    } else if (d.ex_kind == ExtendedKind::JAlert) {
        // J-Alert target area (EX8/EX9)
        dec.jalert_prefecture_mode = (d.ex_jalert.ex8 == 0);
        if (dec.jalert_prefecture_mode) {
            // Prefecture bitmask mode
            dec.prefecture_count = decodePrefectureBitmask(d.ex_jalert.ex9, dec.prefecture_positions);
        } else {
            // City/town/village code list mode
            dec.city_code_count = decodeCityCodeList(d.ex_jalert.ex9, dec.city_codes);
        }
    }

    out.valid = true;
    return true;
}

} // namespace internal
} // namespace azaraC
