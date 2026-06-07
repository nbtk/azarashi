#!/usr/bin/env python3
"""全テストベクター生成スクリプト"""
import azarashi
import json
import os
import sys
from datetime import datetime

def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, bytes):
        return obj.hex()
    if isinstance(obj, set):
        return list(obj)
    # azarashi のカスタムオブジェクトを再帰的にdictに変換
    if hasattr(obj, '__dict__'):
        return {k: json_serial(v) for k, v in obj.__dict__.items()}
    # その他の型は文字列化
    try:
        return str(obj)
    except:
        return repr(obj)

def decode_nmea(nmea_str):
    try:
        r = azarashi.decode(nmea_str.strip())
        return {"nmea": nmea_str.strip(), "type": type(r).__name__, "params": r.get_params()}
    except Exception as e:
        return {"nmea": nmea_str.strip(), "error": str(e)}

def decode_ublox(data_hex):
    try:
        r = azarashi.decode(bytes.fromhex(data_hex), 'ublox')
        return {"type": type(r).__name__, "nmea": r.nmea, "satellite_id": r.satellite_id,
                "satellite_prn": r.satellite_prn, "params": r.get_params()}
    except Exception as e:
        return {"error": str(e)}

def process_log(input_path, output_path):
    results = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            results.append(decode_nmea(line))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=json_serial)
    print(f"  {len(results)} messages -> {output_path}")

def main():
    base = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base, '..', 'data')
    os.makedirs(data_dir, exist_ok=True)

    # DCR vectors from log
    dcr_log = os.path.join(base, '..', '..', '..', 'azarashi', 'tests', 'qzqsm_220307.log')
    if os.path.exists(dcr_log):
        print("Processing DCR log...")
        process_log(dcr_log, os.path.join(data_dir, 'dcr_vectors.json'))

    # DCX vectors from log
    dcx_log = os.path.join(base, '..', '..', '..', 'azarashi', 'tests', 'qzqsm_dcx_240604.log')
    if os.path.exists(dcx_log):
        print("Processing DCX log...")
        process_log(dcx_log, os.path.join(data_dir, 'dcx_vectors.json'))

    # Nankai vectors (test_scenario3)
    print("Processing Nankai vectors...")
    nankai_nmeas = [
        "$QZQSM,58,C6AFA19C918002F2C6CBF35ADBF1C1C471C1D4F1C1CAF3595F82D81262EF438*02",
        "$QZQSM,58,9AAFA19C918002F1C0D471C0D1F1C0D371C0C7F1C0D071C0CAB4D812D45BCD0*06",
        "$QZQSM,58,9AAFA19C918002F1C0CFF4CC5973C0DEF2D7DF72DFCE71C14932D813A64867C*0C",
        "$QZQSM,58,53AFA19C918002F1C0C5F1C0C8F3D6C4F1C0D5F2DFCE71C0CC30D81029188EC*0F",
        "$QZQSM,58,C6AFA19C918002F1C0D4F1C0C5F1C144F1C0D772C8DE71C0D9AED8108F361A8*7A",
        "$QZQSM,58,9AAFA19C918002F2DD4E71C1427443D573595DF25EC9F1C0D52CD81113EFC54*00",
        "$QZQSM,58,9AAFA19C918002F1C0CCF1C041725DC572DF4671C0D7734A5FAAD811D504B9C*09",
        "$QZQSM,58,53AFA19C918002F1C0D4744041F1C0C471C144F1C14671C0DF28D8127EDCCCC*02",
        "$QZQSM,58,C6AFA19C918002F4D5CC71C0DF71C0D1F1C0D371C0C271C145A6D812E9F0C70*03",
        "$QZQSM,58,9AAFA19C918002F1C0DCF1C0D373CDDC72D7DF73CD4271C0D5A4D813579A170*78",
        "$QZQSM,58,9AAFA19C918002F1C0C672DCD9F2DC5C734CC171C0D5F357CA22D8100D3A898*07",
        "$QZQSM,58,53AFA19C918002F1C0D773CCDD73CA4FF2C7D7F441DEF34053A0D8108524298*01",
        "$QZQSM,58,C6AFA19C918002F1C040F2D253F45347F35450F2CE5874CE439ED8113990640*7D",
        "$QZQSM,58,9AAFA19C918002F2D74D74CE43F35D4872CFCFF1C0D3F1C0D79CD8118D63AC8*07",
        "$QZQSM,58,9AAFA19C918002F1C1D4F1C1CAF2CE5874CE43F1C0D77341D99AD81268C2E7C*73",
        "$QZQSM,58,53AFA19C918002F1C14471C14571C040F2C6CBF35ADBF1C1C418D812DC94FA0*7F",
        "$QZQSM,58,C6AFA19C918002F1C0DCF1C14571C0D773CCDD73CA4FF1C0D596D81357F75D0*74",
        "$QZQSM,58,9AAFA19C918002F1C145F1C14371C0D1F1C0C7F1C14571C0CC94D813ED6741C*0C",
        "$QZQSM,58,9AAFA19C918002F4C04D72DC5C71C0D471C0D7F3CAD871C0D512D810ADB00F0*78",
        "$QZQSM,58,53AFA19C918002F1C14671C0DF71C0CCF1C04171C0C9F1C0D710D8112F31B60*73",
    ]
    results = [decode_nmea(n) for n in nankai_nmeas]
    with open(os.path.join(data_dir, 'nankai_vectors.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=json_serial)
    print(f"  {len(results)} Nankai messages")

    # Ash Fall vectors (test_scenario5)
    print("Processing Ash Fall vectors...")
    ash_nmeas = [
        "$QZQSM,58,C6AFC99CAA0001CAA43EE541F0782A1220813091811183E0F000001329B16E0*7F",
        "$QZQSM,58,C6AFC99CAA0001CAA43EE8C2441046123023307C1E19848820000013E2F3E6C*00",
        "$QZQSM,58,9AAFC99CAA0001CAA43EECC24604860F83C430910421848C080000106286874*00",
        "$QZQSM,58,53AFC99CAA0001CAA43EF4C1F078A61220853091813183E0F0000010CE8C39C*77",
        "$QZQSM,58,C6AFC99CAA0001CAA43EF8C24410C61230200000000000000000001148565F4*0A",
    ]
    results = [decode_nmea(n) for n in ash_nmeas]
    with open(os.path.join(data_dir, 'ash_fall_vectors.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=json_serial)
    print(f"  {len(results)} Ash Fall messages")

    # Weather vectors (test_scenario6)
    print("Processing Weather vectors...")
    weather_nmeas = [
        "$QZQSM,58,C6AFD19CB18001113880115F901186A011ADB011D4C011FBD00000135EAA3F8*73",
        "$QZQSM,58,9AAFD19CB180011222E0B93880B95F90B986A0B9ADB0B9D4C0000013D276B60*0D",
        "$QZQSM,58,53AFD19CB18001B9FBD0BA22E00000000000000000000000000000107AA71EC*76",
    ]
    results = [decode_nmea(n) for n in weather_nmeas]
    with open(os.path.join(data_dir, 'weather_vectors.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=json_serial)
    print(f"  {len(results)} Weather messages")

    # DCX vectors (test_dcx)
    print("Processing DCX vectors...")
    dcx_nmeas = [
        "$QZQSM,55,53B0840DE0000000000000000000000000000000000000000000000012ACBD4*0E",
        "$QZQSM,56,9AB08408E0598969E00066AFFE8E6F70091200000000000000000100CD1A410*0C",
        "$QZQSM,55,9AB0840DE10208ADE0000000000000000000011340000000000000132F0D238*04",
        "$QZQSM,55,53B0840DE31188FC208600000000000000001FFFFFFFFFFFC00000120738628*00",
    ]
    results = [decode_nmea(n) for n in dcx_nmeas]
    with open(os.path.join(data_dir, 'dcx_vectors_direct.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=json_serial)
    print(f"  {len(results)} DCX messages")

    # UBX vectors
    print("Processing UBX vectors...")
    ublox_data = [
        {"name": "ublox_sv56_p1", "hex": "B56202132C000502010009400200C5F1AD9A04058011548DA0603F82D2110FAA7D50280C43C91000507D3179F028731810B2622F"},
        {"name": "ublox_sv56_p2", "hex": "B56202132C0005020100094002007614AD535C03801A33EC000049482F14201B01520000000012000000A659B0C65B1FF3B23EB6"},
        {"name": "ublox_sv57", "hex": "B56202132C000503010009410200A1E5ADC6120280366800000110503444D4EE00340000003C11000000149C5F6026CBC0F2EF1A"},
        {"name": "ublox_sv61", "hex": "B56202132C000507010009450200A1E5ADC6120280366800000110503444D4EE00340000003C11000000149C5F6026CBC0F2F762"},
        {"name": "ublox_sv55", "hex": "B56202132C000501010009450200A1E5ADC6120280366800000110503444D4EE00340000003C11000000149C5F6026CBC0F2F160"},
    ]
    results = []
    for u in ublox_data:
        r = decode_ublox(u["hex"])
        r["name"] = u["name"]
        results.append(r)
    with open(os.path.join(data_dir, 'ublox_vectors.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=json_serial)
    print(f"  {len(results)} UBX messages")

    print("\nDone!")

if __name__ == "__main__":
    main()
