// azaraC - src/internal/DecoderDcx.cpp
// MT=44 DCX / CAMF decoder (IS-QZSS-DCX-003)

#include "internal/Decoder.h"
#include "internal/DcxHelper.h"

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

    // Initialize B1 fields
    d.camf.b1_present = false;
    d.camf.b1_c1 = 0;
    d.camf.b1_c2 = 0;
    d.camf.b1_c3 = 0;
    d.camf.b1_c4 = 0;

    // Initialize B2 fields
    d.camf.b2_present = false;
    d.camf.b2_c5 = 0;
    d.camf.b2_c6 = 0;

    // Initialize B3 fields
    d.camf.b3_present = false;
    d.camf.b3_c7 = 0;
    d.camf.b3_c8 = 0;
    d.camf.b3_c9 = 0;
    d.camf.b3_c10 = 0;
    d.camf.b3_shift_km = 0.0;
    d.camf.b3_homothetic_factor = 0.0;
    d.camf.b3_bearing_deg = 0.0;

    // Initialize B4 fields
    d.camf.b4_present = false;
    // Initialize presence flags to false
    d.camf.b4_d1_present = false;  d.camf.b4_d2_present = false;  d.camf.b4_d3_present = false;  d.camf.b4_d4_present = false;
    d.camf.b4_d5_present = false;  d.camf.b4_d6_present = false;  d.camf.b4_d7_present = false;  d.camf.b4_d8_present = false;
    d.camf.b4_d9_present = false;  d.camf.b4_d10_present = false; d.camf.b4_d11_present = false; d.camf.b4_d12_present = false;
    d.camf.b4_d13_present = false; d.camf.b4_d14_present = false; d.camf.b4_d15_present = false; d.camf.b4_d16_present = false;
    d.camf.b4_d17_present = false; d.camf.b4_d18_present = false; d.camf.b4_d19_present = false; d.camf.b4_d20_present = false;
    d.camf.b4_d21_present = false; d.camf.b4_d22_present = false; d.camf.b4_d23_present = false; d.camf.b4_d24_present = false;
    d.camf.b4_d25_present = false; d.camf.b4_d26_present = false; d.camf.b4_d27_present = false; d.camf.b4_d28_present = false;
    d.camf.b4_d29_present = false; d.camf.b4_d30_present = false; d.camf.b4_d31_present = false; d.camf.b4_d32_present = false;
    d.camf.b4_d33_present = false; d.camf.b4_d34_present = false; d.camf.b4_d35_present = false; d.camf.b4_d36_present = false;
    // Initialize D-field values to 0
    d.camf.b4_d1 = 0;  d.camf.b4_d2 = 0;  d.camf.b4_d3 = 0;  d.camf.b4_d4 = 0;
    d.camf.b4_d5 = 0;  d.camf.b4_d6 = 0;  d.camf.b4_d7 = 0;  d.camf.b4_d8 = 0;
    d.camf.b4_d9 = 0;  d.camf.b4_d10 = 0; d.camf.b4_d11 = 0; d.camf.b4_d12 = 0;
    d.camf.b4_d13 = 0; d.camf.b4_d14 = 0; d.camf.b4_d15 = 0; d.camf.b4_d16 = 0;
    d.camf.b4_d17 = 0; d.camf.b4_d18 = 0; d.camf.b4_d19 = 0; d.camf.b4_d20 = 0;
    d.camf.b4_d21 = 0; d.camf.b4_d22 = 0; d.camf.b4_d23 = 0; d.camf.b4_d24 = 0;
    d.camf.b4_d25 = 0; d.camf.b4_d26 = 0; d.camf.b4_d27 = 0; d.camf.b4_d28 = 0;
    d.camf.b4_d29 = 0; d.camf.b4_d30 = 0; d.camf.b4_d31 = 0; d.camf.b4_d32 = 0;
    d.camf.b4_d33 = 0; d.camf.b4_d34 = 0; d.camf.b4_d35 = 0; d.camf.b4_d36 = 0;

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

        uint32_t y, m, day_val;
        Decoder::civil_from_days(unix / 86400u, y, m, day_val);
        d.onset_time.day    = day_val;
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
            // Discard message (Keep SD)
            // The SD field needs to be processed even if the message is discarded (IS-QZSS-DCX-003 §5.7)
            d.service_kind = Mt44ServiceKind::Unknown;
            d.ex_kind = ExtendedKind::None;
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

        // B1 (A17=00) - Improved Resolution of Main Ellipse (EWSS CAMF v1.1 §3.7.1)
        // A18 (15bit) = C1(3bit)[0:2] + C2(3bit)[3:5] + C3(3bit)[6:8] + C4(3bit)[9:11] + Reserved(3bit)[12:14]
        if (d.camf.a17 == 0) {
            B1Refinement b1 = decodeB1Refinement(d.camf.a18);
            d.camf.b1_present = (b1.c1 != 0 || b1.c2 != 0 || b1.c3 != 0 || b1.c4 != 0);
            d.camf.b1_c1 = b1.c1;
            d.camf.b1_c2 = b1.c2;
            d.camf.b1_c3 = b1.c3;
            d.camf.b1_c4 = b1.c4;

            // Store refinement values in decoded ellipse
            dec.main_ellipse.b1_lat_offset_deg = b1RefinedLatitudeOffset(b1.c1);
            dec.main_ellipse.b1_lon_offset_deg = b1RefinedLongitudeOffset(b1.c2);
            dec.main_ellipse.b1_major_factor = b1InterpolationFactor(b1.c3);
            dec.main_ellipse.b1_minor_factor = b1InterpolationFactor(b1.c4);
        }
        // B2 (A17=01) - Position of the Centre of the Hazard (EWSS CAMF v1.1 §3.7.2)
        // A18 = C5[0:6](7bit) + C6[7:13](7bit) + Reserved[14](1bit)
        else if (d.camf.a17 == 1) {
            uint8_t c5 = (d.camf.a18 >> 0) & 0x7F;  // spec bits[0:6]
            uint8_t c6 = (d.camf.a18 >> 7) & 0x7F;  // spec bits[7:13]
            B2HazardCenter b2 = decodeB2HazardCenter(c5, c6);
            d.camf.b2_present = true;
            d.camf.b2_c5 = c5;
            d.camf.b2_c6 = c6;
            dec.main_ellipse.lat_deg += b2.delta_lat_deg;
            dec.main_ellipse.lon_deg += b2.delta_lon_deg;
        }
        // B3 (A17=10) - Secondary Ellipse Definition (EWSS CAMF v1.1 §3.7.3)
        // A18 = C7[0:1](2bit) + C8[2:4](3bit) + C9[5:9](5bit) + C10[10:14](5bit)
        else if (d.camf.a17 == 2) {
            uint8_t c7  = (d.camf.a18 >> 0)  & 0x03;  // spec bits[0:1]
            uint8_t c8  = (d.camf.a18 >> 2)  & 0x07;  // spec bits[2:4]
            uint8_t c9  = (d.camf.a18 >> 5)  & 0x1F;  // spec bits[5:9]
            uint8_t c10 = (d.camf.a18 >> 10) & 0x1F;  // spec bits[10:14]
            B3SecondaryEllipse b3 = decodeB3SecondaryEllipse(c7, c8, c9, c10, dec.main_ellipse.semi_major_km);
            d.camf.b3_present = true;
            d.camf.b3_c7 = c7;
            d.camf.b3_c8 = c8;
            d.camf.b3_c9 = c9;
            d.camf.b3_c10 = c10;
            // Store decoded B3 values for JSON output
            d.camf.b3_shift_km = b3.shift_km;
            d.camf.b3_homothetic_factor = b3.homothetic_factor;
            d.camf.b3_bearing_deg = b3.bearing_deg;
        }
        // B4 (A17=11) - Quantitative and Detailed Information (EWSS CAMF v1.1 §3.7.4)
        else if (d.camf.a17 == 3) {
            B4DetailedInfo b4 = decodeB4DetailedInfo(d.camf.a18, d.camf.a4);
            d.camf.b4_present = true;
            // Copy presence flags
            d.camf.b4_d1_present = b4.d1_present;   d.camf.b4_d2_present = b4.d2_present;
            d.camf.b4_d3_present = b4.d3_present;   d.camf.b4_d4_present = b4.d4_present;
            d.camf.b4_d5_present = b4.d5_present;   d.camf.b4_d6_present = b4.d6_present;
            d.camf.b4_d7_present = b4.d7_present;   d.camf.b4_d8_present = b4.d8_present;
            d.camf.b4_d9_present = b4.d9_present;   d.camf.b4_d10_present = b4.d10_present;
            d.camf.b4_d11_present = b4.d11_present; d.camf.b4_d12_present = b4.d12_present;
            d.camf.b4_d13_present = b4.d13_present; d.camf.b4_d14_present = b4.d14_present;
            d.camf.b4_d15_present = b4.d15_present; d.camf.b4_d16_present = b4.d16_present;
            d.camf.b4_d17_present = b4.d17_present; d.camf.b4_d18_present = b4.d18_present;
            d.camf.b4_d19_present = b4.d19_present; d.camf.b4_d20_present = b4.d20_present;
            d.camf.b4_d21_present = b4.d21_present; d.camf.b4_d22_present = b4.d22_present;
            d.camf.b4_d23_present = b4.d23_present; d.camf.b4_d24_present = b4.d24_present;
            d.camf.b4_d25_present = b4.d25_present; d.camf.b4_d26_present = b4.d26_present;
            d.camf.b4_d27_present = b4.d27_present; d.camf.b4_d28_present = b4.d28_present;
            d.camf.b4_d29_present = b4.d29_present; d.camf.b4_d30_present = b4.d30_present;
            d.camf.b4_d31_present = b4.d31_present; d.camf.b4_d32_present = b4.d32_present;
            d.camf.b4_d33_present = b4.d33_present; d.camf.b4_d34_present = b4.d34_present;
            d.camf.b4_d35_present = b4.d35_present; d.camf.b4_d36_present = b4.d36_present;
            // Copy D-field values
            d.camf.b4_d1 = b4.d1;   d.camf.b4_d2 = b4.d2;
            d.camf.b4_d3 = b4.d3;   d.camf.b4_d4 = b4.d4;
            d.camf.b4_d5 = b4.d5;   d.camf.b4_d6 = b4.d6;
            d.camf.b4_d7 = b4.d7;   d.camf.b4_d8 = b4.d8;
            d.camf.b4_d9 = b4.d9;   d.camf.b4_d10 = b4.d10;
            d.camf.b4_d11 = b4.d11; d.camf.b4_d12 = b4.d12;
            d.camf.b4_d13 = b4.d13; d.camf.b4_d14 = b4.d14;
            d.camf.b4_d15 = b4.d15; d.camf.b4_d16 = b4.d16;
            d.camf.b4_d17 = b4.d17; d.camf.b4_d18 = b4.d18;
            d.camf.b4_d19 = b4.d19; d.camf.b4_d20 = b4.d20;
            d.camf.b4_d21 = b4.d21; d.camf.b4_d22 = b4.d22;
            d.camf.b4_d23 = b4.d23; d.camf.b4_d24 = b4.d24;
            d.camf.b4_d25 = b4.d25; d.camf.b4_d26 = b4.d26;
            d.camf.b4_d27 = b4.d27; d.camf.b4_d28 = b4.d28;
            d.camf.b4_d29 = b4.d29; d.camf.b4_d30 = b4.d30;
            d.camf.b4_d31 = b4.d31; d.camf.b4_d32 = b4.d32;
            d.camf.b4_d33 = b4.d33; d.camf.b4_d34 = b4.d34;
            d.camf.b4_d35 = b4.d35; d.camf.b4_d36 = b4.d36;
        }
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