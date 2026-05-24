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
    out.service_kind = Mt44ServiceKind::Unknown;
    out.is_null_message = false;
    out.ex_kind = ExtendedKind::None;

    // SD (Satellite Designation)
    out.sd.sdmt = getBits(bits, 14, 1);
    out.sd.sdm  = getBits(bits, 15, 9);

    // CAMF (A1 - A18)
    out.camf.a1  = getBits(bits, 24, 2);
    out.camf.a2  = getBits(bits, 26, 9);
    out.camf.a3  = getBits(bits, 35, 5);
    out.camf.a4  = getBits(bits, 40, 7);
    out.camf.a5  = getBits(bits, 47, 2);
    out.camf.a6  = getBits(bits, 49, 1);
    out.camf.a7  = getBits(bits, 50, 14);
    out.camf.a8  = getBits(bits, 64, 2);
    out.camf.a9  = getBits(bits, 66, 1);
    out.camf.a10 = getBits(bits, 67, 3);
    out.camf.a11 = getBits(bits, 70, 10);
    // A12/A13: unsigned codes decoded via formula (not two's complement)
    out.camf.a12 = getBits(bits, 80, 16);
    out.camf.a13 = getBits(bits, 96, 17);
    out.camf.a14 = getBits(bits, 113, 5);
    out.camf.a15 = getBits(bits, 118, 5);
    out.camf.a16 = getBits(bits, 123, 6);
    out.camf.a17 = getBits(bits, 129, 2);
    out.camf.a18 = getBits(bits, 131, 15);

    // Null Message Check (IS-QZSS-DCX-003 §4.3)
    // All fields except PAB, MT, SD, Reserved, CRC must be 0
    // A2 must be Japan (001101111 = 111), A3 must be 0
    if (out.camf.a1 == 0 && out.camf.a2 == 111 && out.camf.a3 == 0 &&
        out.camf.a4 == 0 && out.camf.a5 == 0 && out.camf.a6 == 0 &&
        out.camf.a7 == 0 && out.camf.a8 == 0 && out.camf.a9 == 0 &&
        out.camf.a10 == 0 && out.camf.a11 == 0 &&
        out.camf.a12 == 0 && out.camf.a13 == 0 && out.camf.a14 == 0 &&
        out.camf.a15 == 0 && out.camf.a16 == 0 && out.camf.a17 == 0 &&
        out.camf.a18 == 0) {
        // Extended Message must also be all 0 (bits 146..219 = 74 bits)
        // Check using getBits for correctness
        uint32_t ex_part1 = getBits(bits, 146, 32);  // bits 146..177
        uint32_t ex_part2 = getBits(bits, 178, 32);  // bits 178..209
        uint32_t ex_part3 = getBits(bits, 210, 10);  // bits 210..219
        if (ex_part1 == 0 && ex_part2 == 0 && ex_part3 == 0) {
            out.is_null_message = true;
            out.service_kind = Mt44ServiceKind::NullMessage;
            out.ex_kind = ExtendedKind::None;
            out.valid = true;
            return true;
        }
    }

    // Resolve onset time from GPS week-mod-4 + minute-of-week
    // Use report_unix (GPS time from receiver) for accurate onset calculation
    if (out.camf.a7 > 0 && out.camf.a7 <= 10080 && report_unix > 315964800u) {
        // GPS epoch 1980-01-06 00:00:00 UTC, +18 leap seconds (post-2017)
        uint32_t gps  = report_unix - 315964800u + 18u;
        uint32_t week = gps / 604800u;
        int32_t diff = (int32_t)(out.camf.a6 & 3u) - (int32_t)(week & 3u);
        if (diff < -2) diff += 4;
        else if (diff > 1) diff -= 4;
        uint32_t base = week + diff;

        uint32_t gps_onset = base * 604800u + (uint32_t)(out.camf.a7 - 1u) * 60u;
        uint32_t unix = gps_onset + 315964800u - 18u;
        out.onset_time.unix_time = unix;

        uint32_t y, m, d;
        Decoder::civil_from_days(unix / 86400u, y, m, d);
        out.onset_time.day    = d;
        out.onset_time.hour   = ((out.camf.a7 - 1u) % 1440u) / 60u;
        out.onset_time.minute = (out.camf.a7 - 1u) % 60u;
    }

    // Determine Service Kind based on A2 and A3
    if (out.camf.a2 != 111) { // 111 = 001101111 = Japan
        out.service_kind = Mt44ServiceKind::OutsideJapan;
        out.ex_kind = ExtendedKind::OutsideJapan;
    } else {
        if (out.camf.a3 == 1) {
            out.service_kind = Mt44ServiceKind::LAlert;
            out.ex_kind = ExtendedKind::LAlertOrLocal;
        } else if (out.camf.a3 == 2 || out.camf.a3 == 3) {
            out.service_kind = Mt44ServiceKind::JAlert;
            out.ex_kind = ExtendedKind::JAlert;
        } else if (out.camf.a3 == 4) {
            out.service_kind = Mt44ServiceKind::LocalGovernment;
            out.ex_kind = ExtendedKind::LAlertOrLocal;
        } else {
            // Discard message
            return false;
        }
    }

    // Parse Extended Message
    if (out.ex_kind == ExtendedKind::LAlertOrLocal) {
        out.ex_lalert_local.ex1 = getBits(bits, 146, 16);
        out.ex_lalert_local.ex2 = getBits(bits, 162, 1);
        // EX3/EX4: unsigned codes (latitude/longitude formulas, not two's complement)
        out.ex_lalert_local.ex3 = getBits(bits, 163, 17);
        out.ex_lalert_local.ex4 = getBits(bits, 180, 17);
        out.ex_lalert_local.ex5 = getBits(bits, 197, 5);
        out.ex_lalert_local.ex6 = getBits(bits, 202, 5);
        out.ex_lalert_local.ex7 = getBits(bits, 207, 7);
        out.ex_lalert_local.vn  = getBits(bits, 214, 6);
    } else if (out.ex_kind == ExtendedKind::JAlert) {
        out.ex_jalert.ex8  = getBits(bits, 146, 1);
        uint32_t ex9_hi = getBits(bits, 147, 32);
        uint32_t ex9_lo = getBits(bits, 179, 32);
        out.ex_jalert.ex9  = ((uint64_t)ex9_hi << 32) | ex9_lo;
        out.ex_jalert.ex10 = getBits(bits, 211, 3);
        out.ex_jalert.vn   = getBits(bits, 214, 6);
    } else if (out.ex_kind == ExtendedKind::OutsideJapan) {
        for (int i = 0; i < 8; ++i) {
            out.ex_outside.ex11_raw[i] = getBits(bits, 146 + i * 8, 8);
        }
        out.ex_outside.ex11_raw[8] = getBits(bits, 210, 4) << 4; // remaining 4 bits
        out.ex_outside.vn = getBits(bits, 214, 6);
    }

    // ---------------------------------------------------------------------------
    // Populate decoded structures (IS-QZSS-DCX-003 §15.2)
    // ---------------------------------------------------------------------------

    azaraC::Mt44Decoded& dec = out.mt44_decoded;
    dec.service_kind = out.service_kind;
    dec.is_null_message = out.is_null_message;
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
    dec.alert_identity.a2 = out.camf.a2;
    dec.alert_identity.a3 = out.camf.a3;
    dec.alert_identity.a4 = out.camf.a4;
    dec.alert_identity.ex1 = 0;

    if (out.is_null_message) {
        out.valid = true;
        return true;
    }

    // Main ellipse (A12-A16): present if any of A12..A16 is non-zero
    bool has_main_ellipse = (out.camf.a12 != 0 || out.camf.a13 != 0 ||
                             out.camf.a14 != 0 || out.camf.a15 != 0 ||
                             out.camf.a16 != 0);
    if (has_main_ellipse) {
        dec.main_ellipse_present = true;
        dec.main_ellipse.lat_deg = decodeLatitude16(out.camf.a12);
        dec.main_ellipse.lon_deg = decodeLongitude17(out.camf.a13);
        dec.main_ellipse.semi_major_km = decodeRadiusCode(out.camf.a14);
        dec.main_ellipse.semi_minor_km = decodeRadiusCode(out.camf.a15);
        dec.main_ellipse.azimuth_deg = decodeAzimuth6(out.camf.a16);
    }

    if (out.ex_kind == ExtendedKind::LAlertOrLocal) {
        dec.alert_identity.ex1 = out.ex_lalert_local.ex1;

        // Target area code (EX1): used when main ellipse is absent
        if (!has_main_ellipse && out.ex_lalert_local.ex1 != 0) {
            dec.target_area_code_present = true;
            dec.target_area_code = out.ex_lalert_local.ex1;
        }

        // Additional area (local government only): EX2-EX7
        if (out.service_kind == Mt44ServiceKind::LocalGovernment) {
            bool has_additional = (out.ex_lalert_local.ex2 != 0 ||
                                   out.ex_lalert_local.ex3 != 0 ||
                                   out.ex_lalert_local.ex4 != 0 ||
                                   out.ex_lalert_local.ex5 != 0 ||
                                   out.ex_lalert_local.ex6 != 0 ||
                                   out.ex_lalert_local.ex7 != 0);
            if (has_additional) {
                dec.additional_area.present = true;
                dec.additional_area.head_to_area = (out.ex_lalert_local.ex2 != 0);
                dec.additional_area.ellipse.lat_deg = decodeLatitude17(out.ex_lalert_local.ex3);
                dec.additional_area.ellipse.lon_deg = decodeLongitude17_45_225(out.ex_lalert_local.ex4);
                dec.additional_area.ellipse.semi_major_km = decodeRadiusCode(out.ex_lalert_local.ex5);
                dec.additional_area.ellipse.semi_minor_km = decodeRadiusCode(out.ex_lalert_local.ex6);
                dec.additional_area.ellipse.azimuth_deg = decodeAzimuth7(out.ex_lalert_local.ex7);
            }
        }
    } else if (out.ex_kind == ExtendedKind::JAlert) {
        // J-Alert target area (EX8/EX9)
        dec.jalert_prefecture_mode = (out.ex_jalert.ex8 == 0);
        if (dec.jalert_prefecture_mode) {
            // Prefecture bitmask mode
            uint64_t ex9 = out.ex_jalert.ex9;
            for (uint8_t i = 0; i < 47; ++i) {
                if (ex9 & (1ULL << i)) {
                    // Bit position (47-i) corresponds to prefecture
                    dec.prefecture_positions[dec.prefecture_count++] = 47 - i;
                }
            }
        } else {
            // City/town/village code list mode
            uint64_t ex9 = out.ex_jalert.ex9;
            for (uint8_t i = 0; i < 4; ++i) {
                uint16_t code = static_cast<uint16_t>((ex9 >> (i * 16)) & 0xFFFF);
                if (code != 0) {
                    dec.city_codes[dec.city_code_count++] = code;
                }
            }
        }
    }

    out.valid = true;
    return true;
}

} // namespace internal
} // namespace azaraC
