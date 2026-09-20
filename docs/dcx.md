[azarashi](../README.md) / [Reports](reports.md) / DCX

# DCX (MT44)
気象庁以外の機関が発表するメッセージのレポートです。`dcx.Base` を継承します。仕様は [IS-QZSS-DCX](https://qzss.go.jp/technical/download/pdf/ps-is-qzss/is-qzss-dcx-004.pdf) の Message Type 44 で、CAMF という共通の形式を使います。

MT44 は全員が同じ形式を使い、発信機関によって拡張領域の読み方が変わります。そのためクラスは発信機関ごとに分かれます。

| 発信元 | クラス | 説明 |
|---|---|---|
| L-Alert | `dcx.LAlert` | 一般財団法人マルチメディア振興センターが発表します。 |
| J-Alert | `dcx.JAlert` | 消防庁と関係省庁が発表します。 |
| 自治体 | `dcx.MTInfo` | 地方公共団体が発表します。 |
| 日本国外の機関 | `dcx.OutsideJapan` | 日本国外の機関が発表します。 |
| CAMF フィールドを使わないメッセージ | `dcx.NullMsg` | 警報を持ちません。SD フィールドを監視するために使います。不要なら無視してください。 |
| 上記以外 | `dcx.Unknown` | 日本から発表されたもので、発信機関が上のどれでもないものです。正確にデコードできない可能性が高いので、デバッグのとき以外は無視してください。 |

警報のフィールドは `dcx.AlertBase` で宣言しています。上の表の `dcx.NullMsg` 以外の5クラスが、これを継承します。

メッセージの種類や内容によって設定されないフィールドは `None` になります。型も `float | None` のように宣言してあるので、型検査で気づけます。A1 から A10 までと `dcx_version` は必ず設定されるので `None` になりません。どのフィールド群が読まれたかは `ignore_a12_to_a16` などのフラグで分かります。

`dcx.NullMsg` は警報を持たないメッセージなので、これらのフィールドを一つも持ちません。読もうとすると型検査が止めます。

## Message Type and Satellite Designation
| フィールド | 型 |
|---|---|
| `dcx_message_type` | `str` |
| `dcx_version` | `int` |
| `satellite_designation_mask_type` | `str` |
| `satellite_designation_mask` | `list[str]` |

## A Fields
| フィールド | 型 |
|---|---|
| `a1_message_type` | `str` |
| `a2_country_region_name` | `str` |
| `a3_provider_identifier` | `str` |
| `a4_hazard_category` | `str` |
| `a4_hazard_type` | `str` |
| `a4_hazard_definition` | `str` |
| `a5_severity` | `str` |
| `a6_hazard_onset_week` | `str` |
| `a7_hazard_onset_time_of_week` | `str` |
| `a6a7_hazard_onset_datetime` | `datetime \| None` |
| `a8_hazard_duration` | `str` |
| `a9_type_of_library` | `str` |
| `a10_library_version` | `str` |
| `a11_international_library_code` | `str \| None` |
| `a11_international_library` | `str \| None` |
| `a11_japanese_library` | `str \| None` |
| `a11_japanese_library_ja` | `str \| None` |
| `a12_ellipse_centre_latitude` | `float \| None` |
| `a13_ellipse_centre_longitude` | `float \| None` |
| `a14_ellipse_semi_major_axis` | `float \| None` |
| `a15_ellipse_semi_minor_axis` | `float \| None` |
| `a16_ellipse_azimuth` | `float \| None` |
| `a17_type_of_specific_settings` | `str \| None` |

## C Fields
| フィールド | 型 |
|---|---|
| `c1_refined_latitude_of_centre_of_main_ellipse` | `float \| None` |
| `c2_refined_longitude_of_centre_of_main_ellipse` | `float \| None` |
| `c3_refined_length_of_semi_major_axis` | `float \| None` |
| `c4_refined_length_of_semi_minor_axis` | `float \| None` |
| `c5_latitude_of_centre_of_hazard` | `float \| None` |
| `c6_longitude_of_centre_of_hazard` | `float \| None` |
| `c7_shift_of_second_ellipse_centre` | `int \| None` |
| `c8_homothetic_factor_of_second_ellipse` | `float \| None` |
| `c9_bearing_angle_of_second_ellipse` | `float \| None` |
| `c10_instruction_library_for_second_ellipse_code` | `str \| None` |
| `c10_instruction_library_for_second_ellipse` | `str \| None` |

## D Fields
| フィールド | 型 |
|---|---|
| `d1_magnitude_on_richter_scale` | `str \| None` |
| `d2_seismic_coefficient` | `str \| None` |
| `d3_azimuth_from_centre_of_main_ellipse_to_epicentre` | `float \| None` |
| `d4_vector_length_between_centre_of_main_ellipse_and_epicentre` | `float \| None` |
| `d5_wave_height` | `str \| None` |
| `d6_temperature_range` | `str \| None` |
| `d7_hurricane_category` | `str \| None` |
| `d8_wind_speed` | `str \| None` |
| `d9_rainfall_amounts` | `str \| None` |
| `d10_damage_category` | `str \| None` |
| `d11_tornado_probability` | `str \| None` |
| `d12_hail_scale` | `str \| None` |
| `d13_visibility` | `str \| None` |
| `d14_snow_depth` | `str \| None` |
| `d15_flood_severity` | `str \| None` |
| `d16_lightning_intensity` | `str \| None` |
| `d17_fog_level` | `str \| None` |
| `d18_drought_level` | `str \| None` |
| `d19_avalanche_warning_level` | `str \| None` |
| `d20_ash_fall_amount_and_impact` | `str \| None` |
| `d21_geomagnetic_scale` | `str \| None` |
| `d22_terrorism_threat_level` | `str \| None` |
| `d23_fire_risk_level` | `str \| None` |
| `d24_water_quality` | `str \| None` |
| `d25_uv_index` | `str \| None` |
| `d26_number_of_cases_per_100000_inhabitants` | `str \| None` |
| `d27_noise_range` | `str \| None` |
| `d28_air_quality_index` | `str \| None` |
| `d29_outage_estimated_duration` | `str \| None` |
| `d30_nuclear_event_scale` | `str \| None` |
| `d31_chemical_hazard_type` | `str \| None` |
| `d32_biohazard_level` | `str \| None` |
| `d33_biohazard_type` | `str \| None` |
| `d34_explosive_hazard_type` | `str \| None` |
| `d35_infection_type` | `str \| None` |
| `d36_typhoon_category` | `str \| None` |

## EX Fields
| フィールド | 型 |
|---|---|
| `ex1_target_area` | `str \| None` |
| `ex1_target_area_ja` | `str \| None` |
| `ex2_evacuate_direction_type` | `str \| None` |
| `ex3_additional_ellipse_centre_latitude` | `float \| None` |
| `ex4_additional_ellipse_centre_longitude` | `float \| None` |
| `ex5_additional_ellipse_semi_major_axis` | `float \| None` |
| `ex6_additional_ellipse_semi_minor_axis` | `float \| None` |
| `ex7_additional_ellipse_azimuth` | `float \| None` |
| `ex8_target_area_list_type` | `str \| None` |
| `ex9_target_area_list` | `list[str] \| None` |
| `ex9_target_area_list_ja` | `list[str] \| None` |

ほかに、ビットフィールドのままの値を持つ `camf` と、どの範囲を読み飛ばしたかを示す `ignore_a12_to_a16`、`ignore_a17_to_a18`、`ignore_ex1`、`ignore_ex2_to_ex7`、`ignore_ex8_to_ex9` があります。

## Example
DCX は災危通報の拡張メッセージで、L-Alert や J-Alert などを伝えます。下記は L-Alert をデコードする例です。
```python
>>> import azarashi
>>> msg = '$QZQSM,55,53B0604DE19524CDA305B2C1E355B57800000CCC000000000000001022A8188*7E' # l-alert
>>> report = azarashi.decode(msg, 'nmea')
>>> print(report)
```
```
### DCX Message - L-Alert ###
A1 - Message type: Alert
A2 - Country/region name: Japan
A3 - Provider identifier: Foundation for MultiMedia Communications
A4 - Hazard category and type: MET - Rainfall
A4 - Hazard definition: Rainfall greater than or equal to 50 mm in past 24 hours. Note: Precise threshold is according to each local standard.
A5 - Severity: Severe - Significant threat to life or property
A6A7 - Hazard onset: 2024-06-23T13:00:00Z
A8 - Hazard duration: 6H <= Duration < 12H
A11 - Instruction: Keep away from Water area.
A11 - Instruction (ja): 離れろ。水場。
A12 - Ellipse centre latitude: 35.688258
A13 - Ellipse centre longitude: 139.690855
A14 - Ellipse semi - major axis: 10.933
A15 - Ellipse semi - minor axis: 5.979
A16 - Ellipse azimuth: 45.0
A17 - Type of specific settings: B1 - Improved Resolution of Main Ellipse
C1 - Refined latitude of centre of main ellipse: 35.688258
C2 - Refined longitude of centre of main ellipse: 139.690855
C3 - Refined length of semi major axis: 10.933
C4 - Refined length of semi minor axis: 5.979
```
レポートオブジェクトからパラメータを取得するには `get_params()` メソッドを使います。
```python
>>> from pprint import pprint
>>> pprint(report.get_params(), sort_dicts=False)
```
```python
{'sentence': '$QZQSM,55,53B0604DE19524CDA305B2C1E355B57800000CCC000000000000001022A8188*7E',
 'raw': b'M\xe1\x95$\xcd\xa3\x05\xb2\xc1\xe3U\xb5x\x00\x00\x0c\xcc\x00\x00\x00'
        b'\x00\x00\x00\x00\x10',
 'timestamp': datetime.datetime(2024, 6, 21, 6, 9, 5, 433111, tzinfo=datetime.timezone.utc),
 'message': b'S\xb0`M\xe1\x95$\xcd\xa3\x05\xb2\xc1\xe3U\xb5x\x00\x00\x0c\xcc'
            b'\x00\x00\x00\x00\x00\x00\x00\x10"\xa8\x18\x80',
 'nmea': '$QZQSM,55,53B0604DE19524CDA305B2C1E355B57800000CCC000000000000001022A8188*7E',
 'message_header': '$QZQSM',
 'satellite_id': 55,
 'satellite_prn': 183,
 'satellite_svid': None,
 'preamble': 'A',
 'message_type': 'DCX',
 'camf': CAMF(sdmt=0, sdm=96, a1=1, a2=111, a3=1, a4=74, a5=2, a6=0, a7=9421, a8=2, a9=1, a10=0, a11=773, a12=45761, a13=116395, a14=13, a15=11, a16=48, a17=0, a18=0, ex1=13104, ex2=0, ex3=0, ex4=0, ex5=0, ex6=0, ex7=0, ex8=0, ex9=7376896189632872448, ex10=0, vn=1, c1=0, c2=0, c3=0, c4=0),
 'ignore_a12_to_a16': False,
 'ignore_a17_to_a18': False,
 'ignore_ex1': True,
 'ignore_ex2_to_ex7': True,
 'ignore_ex8_to_ex9': True,
 'satellite_designation_mask_type': 'MT44 is for Japan or for use outside '
                                    'Japan',
 'satellite_designation_mask': ['For Japan',
                                'For Japan',
                                'For use outside Japan',
                                'For use outside Japan',
                                'For Japan',
                                'For Japan',
                                'For Japan',
                                'For Japan',
                                'For Japan'],
 'dcx_message_type': 'L-Alert',
 'a1_message_type': 'Alert',
 'a2_country_region_name': 'Japan',
 'a3_provider_identifier': 'Foundation for MultiMedia Communications',
 'a4_hazard_category': 'MET',
 'a4_hazard_type': 'Rainfall',
 'a4_hazard_definition': 'Rainfall greater than or equal to 50 mm in past 24 '
                         'hours. Note: Precise threshold is according to each '
                         'local standard.',
 'a5_severity': 'Severe - Significant threat to life or property',
 'a6_hazard_onset_week': 'Current',
 'a7_hazard_onset_time_of_week': 'SUNDAY - 01:00 PM',
 'a6a7_hazard_onset_datetime': datetime.datetime(2024, 6, 23, 13, 0, tzinfo=datetime.timezone.utc),
 'a8_hazard_duration': '6H <= Duration < 12H',
 'a9_type_of_library': 'Country/region library',
 'a10_library_version': '#1',
 'a11_japanese_library': 'Keep away from Water area.',
 'a11_japanese_library_ja': '離れろ。水場。',
 'a12_ellipse_centre_latitude': 35.688258,
 'a13_ellipse_centre_longitude': 139.690855,
 'a14_ellipse_semi_major_axis': 10.933,
 'a15_ellipse_semi_minor_axis': 5.979,
 'a16_ellipse_azimuth': 45.0,
 'a17_type_of_specific_settings': 'B1 - Improved Resolution of Main Ellipse',
 'c1_refined_latitude_of_centre_of_main_ellipse': 35.688258,
 'c2_refined_longitude_of_centre_of_main_ellipse': 139.690855,
 'c3_refined_length_of_semi_major_axis': 10.933,
 'c4_refined_length_of_semi_minor_axis': 5.979,
 'dcx_version': 1}
```
デコードする前のビットフィールドの値は、`report.camf` に入っています。
```python
print(report.camf.get_params())
```
```python
{'sdmt': 0, 'sdm': 96, 'a1': 1, 'a2': 111, 'a3': 1, 'a4': 74, 'a5': 2, 'a6': 0, 'a7': 9421, 'a8': 2, 'a9': 1, 'a10': 0, 'a11': 773, 'a12': 45761, 'a13': 116395, 'a14': 13, 'a15': 11, 'a16': 48, 'a17': 0, 'a18': 0, 'ex1': 13104, 'ex2': 0, 'ex3': 0, 'ex4': 0, 'ex5': 0, 'ex6': 0, 'ex7': 0, 'ex8': 0, 'ex9': 7376896189632872448, 'ex10': 0, 'vn': 1, 'c1': 0, 'c2': 0, 'c3': 0, 'c4': 0}
```
