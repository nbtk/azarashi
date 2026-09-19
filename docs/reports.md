[azarashi](../README.md) / Reports

# Reports
`decode()` と `decode_stream()` が返すレポートオブジェクトの一覧です。メッセージの種類によって、返るクラスが変わります。
どのクラスが返るかは `isinstance()` で確かめてください。使い方は [API](api.md) を見てください。

フィールドは `get_params()` で辞書としても取り出せます。名前には決まりがあります。

- `_raw`: 受信した値そのものです。名前を持たない値でも、ここには残ります。
- `_en`: 英語の表記です。
- `_no`: azarashi が処理の分岐に使う番号です。
- `DayHourMinute` と `Coordinates` は辞書です。前者は `day`、`hour`、`minute` を、後者は緯度と経度を持ちます。
- 時刻として読めない値が届いたときは、その時刻のフィールドは `None` になります。

## すべてのレポートに共通するフィールド
`base.Base` のフィールドです。どのレポートにもあります。
| フィールド | 型 |
|---|---|
| `sentence` | `str \| bytes` |
| `raw` | `bytes` |
| `timestamp` | `datetime` |

メッセージを取り出せたレポートには、`base.MessagePartial` のフィールドが加わります。
| フィールド | 型 |
|---|---|
| `message` | `bytes` |
| `nmea` | `str` |
| `message_header` | `str \| bytes \| None` |
| `satellite_id` | `int \| None` |
| `satellite_prn` | `int \| None` |
| `satellite_svid` | `int \| None` |

`hex` 形式のようにヘッダや衛星の情報を持たないメッセージでは、`message_header` と `satellite_id` と `satellite_prn` は `None` です。`satellite_svid` は u-blox から受け取ったときだけ値が入ります。

DCR と DCX のレポートには、さらに `base.MessageBase` の次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `preamble` | `str` |
| `message_type` | `str` |

## DCR (MT43)
気象庁が発表する防災気象情報のレポートです。`dcr.Base` を継承します。仕様は [IS-QZSS-DCR](https://qzss.go.jp/technical/download/pdf/ps-is-qzss/is-qzss-dcr-017.pdf) の Message Type 43 です。

MT43 は災害種別ごとに電文の構造が違うので、クラスも災害種別ごとに分かれます。共通のフィールドは次のとおりです。
| フィールド | 型 |
|---|---|
| `version` | `int` |
| `report_classification` | `str` |
| `report_classification_en` | `str` |
| `report_classification_no` | `int` |
| `disaster_category` | `str` |
| `disaster_category_en` | `str` |
| `disaster_category_no` | `int` |
| `report_time` | `datetime` |
| `information_type` | `str` |
| `information_type_en` | `str` |
| `information_type_no` | `int` |

災害種別ごとに、次のクラスが返ります。
| `disaster_category_no` | 災害種別 | クラス |
|---|---|---|
| 1 | 緊急地震速報 | `dcr.EarthquakeEarlyWarning` |
| 2 | 震源 | `dcr.Hypocenter` |
| 3 | 震度 | `dcr.SeismicIntensity` |
| 4 | 南海トラフ地震 | `dcr.NankaiTroughEarthquake` |
| 5 | 津波 | `dcr.Tsunami` |
| 6 | 北西太平洋津波 | `dcr.NorthwestPacificTsunami` |
| 8 | 火山 | `dcr.Volcano` |
| 9 | 降灰 | `dcr.AshFall` |
| 10 | 気象 | `dcr.Weather` |
| 11 | 洪水 | `dcr.Flood` |
| 12 | 台風 | `dcr.Typhoon` |
| 14 | 海上 | `dcr.Marine` |

### dcr.EarthquakeEarlyWarning
緊急地震速報のレポートです。`disaster_category_no` は 1 です。上の共通フィールドに加えて、次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `long_period_ground_motion_lower_limit` | `str \| None` |
| `long_period_ground_motion_lower_limit_raw` | `int` |
| `long_period_ground_motion_upper_limit` | `str \| None` |
| `long_period_ground_motion_upper_limit_raw` | `int` |
| `notifications_on_disaster_prevention` | `list[str]` |
| `notifications_on_disaster_prevention_raw` | `list[int]` |
| `occurrence_time_of_earthquake` | `datetime \| None` |
| `occurrence_time_of_earthquake_raw` | `DayHourMinute` |
| `depth_of_hypocenter` | `str` |
| `depth_of_hypocenter_raw` | `int` |
| `magnitude` | `str` |
| `magnitude_raw` | `int` |
| `assumptive` | `bool` |
| `seismic_epicenter` | `str` |
| `seismic_epicenter_raw` | `int` |
| `seismic_intensity_lower_limit` | `str` |
| `seismic_intensity_lower_limit_raw` | `int` |
| `seismic_intensity_upper_limit` | `str` |
| `seismic_intensity_upper_limit_raw` | `int` |
| `eew_forecast_regions` | `list[str]` |
| `eew_forecast_regions_raw` | `list[int]` |

### dcr.Hypocenter
震源のレポートです。`disaster_category_no` は 2 です。上の共通フィールドに加えて、次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `notifications_on_disaster_prevention` | `list[str]` |
| `notifications_on_disaster_prevention_raw` | `list[int]` |
| `occurrence_time_of_earthquake` | `datetime \| None` |
| `occurrence_time_of_earthquake_raw` | `DayHourMinute` |
| `depth_of_hypocenter` | `str` |
| `depth_of_hypocenter_raw` | `int` |
| `magnitude` | `str` |
| `magnitude_raw` | `int` |
| `seismic_epicenter` | `str` |
| `seismic_epicenter_raw` | `int` |
| `coordinates_of_hypocenter` | `str` |
| `coordinates_of_hypocenter_raw` | `Coordinates` |

### dcr.SeismicIntensity
震度のレポートです。`disaster_category_no` は 3 です。上の共通フィールドに加えて、次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `occurrence_time_of_earthquake` | `datetime \| None` |
| `occurrence_time_of_earthquake_raw` | `DayHourMinute` |
| `seismic_intensities` | `list[str]` |
| `seismic_intensities_raw` | `list[int]` |
| `prefectures` | `list[str]` |
| `prefectures_raw` | `list[int]` |

### dcr.NankaiTroughEarthquake
南海トラフ地震のレポートです。`disaster_category_no` は 4 です。上の共通フィールドに加えて、次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `information_serial_code` | `str` |
| `information_serial_code_raw` | `int` |
| `text_information` | `bytes` |
| `page_number` | `int` |
| `total_page` | `int` |

### dcr.Tsunami
津波のレポートです。`disaster_category_no` は 5 です。上の共通フィールドに加えて、次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `notifications_on_disaster_prevention` | `list[str]` |
| `notifications_on_disaster_prevention_raw` | `list[int]` |
| `tsunami_warning_code` | `str` |
| `tsunami_warning_code_raw` | `int` |
| `expected_tsunami_arrival_times` | `list[datetime \| None]` |
| `expected_tsunami_arrival_times_raw` | `list[DayHourMinute]` |
| `expected_tsunami_arrival_time_types` | `list[str]` |
| `tsunami_heights` | `list[str]` |
| `tsunami_heights_raw` | `list[int]` |
| `tsunami_forecast_regions` | `list[str]` |
| `tsunami_forecast_regions_raw` | `list[int]` |

### dcr.NorthwestPacificTsunami
北西太平洋津波のレポートです。`disaster_category_no` は 6 です。上の共通フィールドに加えて、次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `tsunamigenic_potential_en` | `str` |
| `tsunamigenic_potential_raw` | `int` |
| `expected_tsunami_arrival_times` | `list[datetime \| None]` |
| `expected_tsunami_arrival_times_raw` | `list[DayHourMinute]` |
| `expected_tsunami_arrival_time_types_en` | `list[str]` |
| `tsunami_heights_en` | `list[str]` |
| `tsunami_heights_raw` | `list[int]` |
| `coastal_regions_en` | `list[str]` |
| `coastal_regions_raw` | `list[int]` |

### dcr.Volcano
火山のレポートです。`disaster_category_no` は 8 です。上の共通フィールドに加えて、次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `ambiguity_of_activity_time_no` | `int` |
| `activity_time` | `datetime \| None` |
| `activity_time_raw` | `DayHourMinute` |
| `volcanic_warning_code` | `str` |
| `volcanic_warning_code_raw` | `int` |
| `volcano_name` | `str` |
| `volcano_name_raw` | `int` |
| `local_governments` | `list[str]` |
| `local_governments_raw` | `list[int]` |

### dcr.AshFall
降灰のレポートです。`disaster_category_no` は 9 です。上の共通フィールドに加えて、次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `activity_time` | `datetime \| None` |
| `activity_time_raw` | `DayHourMinute` |
| `ash_fall_warning_type` | `str` |
| `ash_fall_warning_type_raw` | `int` |
| `volcano_name` | `str` |
| `volcano_name_raw` | `int` |
| `expected_ash_fall_times` | `list[str]` |
| `expected_ash_fall_times_raw` | `list[int]` |
| `ash_fall_warning_codes` | `list[str]` |
| `ash_fall_warning_codes_raw` | `list[int]` |
| `local_governments` | `list[str]` |
| `local_governments_raw` | `list[int]` |

### dcr.Weather
気象のレポートです。`disaster_category_no` は 10 です。上の共通フィールドに加えて、次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `weather_warning_state` | `str` |
| `weather_warning_state_raw` | `int` |
| `weather_related_disaster_sub_categories` | `list[str]` |
| `weather_related_disaster_sub_categories_raw` | `list[int]` |
| `weather_forecast_regions` | `list[str]` |
| `weather_forecast_regions_raw` | `list[int]` |

### dcr.Flood
洪水のレポートです。`disaster_category_no` は 11 です。上の共通フィールドに加えて、次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `flood_warning_levels` | `list[str]` |
| `flood_warning_levels_raw` | `list[int]` |
| `flood_forecast_regions` | `list[str]` |
| `flood_forecast_regions_raw` | `list[int]` |

### dcr.Typhoon
台風のレポートです。`disaster_category_no` は 12 です。上の共通フィールドに加えて、次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `reference_time` | `datetime \| None` |
| `reference_time_raw` | `DayHourMinute` |
| `reference_time_type` | `str` |
| `reference_time_type_raw` | `int` |
| `elapsed_time_from_reference_time` | `str` |
| `elapsed_time_from_reference_time_raw` | `int` |
| `typhoon_number` | `str` |
| `typhoon_number_raw` | `int` |
| `typhoon_scale_category` | `str` |
| `typhoon_scale_category_raw` | `int` |
| `typhoon_intensity_category` | `str` |
| `typhoon_intensity_category_raw` | `int` |
| `coordinates_of_typhoon` | `str` |
| `coordinates_of_typhoon_raw` | `Coordinates` |
| `central_pressure` | `str` |
| `central_pressure_raw` | `int` |
| `maximum_wind_speed` | `str` |
| `maximum_wind_speed_raw` | `int` |
| `maximum_gust_wind_speed` | `str` |
| `maximum_gust_wind_speed_raw` | `int` |

### dcr.Marine
海上のレポートです。`disaster_category_no` は 14 です。上の共通フィールドに加えて、次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `marine_warning_codes` | `list[str]` |
| `marine_warning_codes_raw` | `list[int]` |
| `marine_forecast_regions` | `list[str]` |
| `marine_forecast_regions_raw` | `list[int]` |

### デコードした例
`decode()` はレポートオブジェクトを返します。レポートオブジェクトを `str()` に渡すと、災害情報を読みやすい文章にして返します。
```python
>>> import azarashi
>>> msg = '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05'
>>> report = azarashi.decode(msg, 'nmea')
>>> str(report)
'防災気象情報(緊急地震速報)(発表)(訓練/試験)\n*** これは訓練です ***\n緊急地震速報\n強い揺れに警戒してください。\n\n発表時刻: 3月10日10時0分\n\n震央地名: 日向灘\n地震発生時刻: 10日10時0分\n深さ: 10km\nマグニチュード: 7.2\n震度(下限): 震度6弱\n震度(上限): 〜程度以上\n島根、岡山、広島、山口、香川、愛媛、高知、福岡、佐賀、長崎、熊本、大分、宮崎、鹿児島、中国、四国、九州'
```
そのため、レポートオブジェクトを `print()` に渡すと災害情報を表示できます。
```python
>>> print(report)
```
```
防災気象情報(緊急地震速報)(発表)(訓練/試験)
*** これは訓練です ***
緊急地震速報
強い揺れに警戒してください。

発表時刻: 3月10日10時0分

震央地名: 日向灘
地震発生時刻: 10日10時0分
深さ: 10km
マグニチュード: 7.2
震度(下限): 震度6弱
震度(上限): 〜程度以上
島根、岡山、広島、山口、香川、愛媛、高知、福岡、佐賀、長崎、熊本、大分、宮崎、鹿児島、中国、四国、九州
```
レポートオブジェクトのパラメータは、`get_params()` メソッドで辞書として取得できます。時刻のパラメータは、すべて UTC のタイムゾーンが付いた `datetime` です。`str()` が返す文章では、時刻を JST に変換して表示します。

時刻として読めない値が届いたときは、その時刻のパラメータは `None` になります。送られてきた日・時・分は、名前の末尾に `_raw` が付いたパラメータに残ります。例えば `occurrence_time_of_earthquake` なら `occurrence_time_of_earthquake_raw` です。ただし発表時刻の `report_time` だけは、読めない値が届くと `None` にならず、`AzarashiInvalidMessageError` が送出されます。
```python
>>> from pprint import pprint
>>> pprint(report.get_params())
```
```python
{'assumptive': False,
 'depth_of_hypocenter': '10km',
 'depth_of_hypocenter_raw': 10,
 'disaster_category': '緊急地震速報',
 'disaster_category_en': 'Earthquake Early Warning',
 'disaster_category_no': 1,
 'eew_forecast_regions': ['島根', '岡山', '広島', '山口', '香川', '愛媛',
                          '高知', '福岡', '佐賀', '長崎', '熊本', '大分',
                          '宮崎', '鹿児島', '中国', '四国', '九州'],
 'eew_forecast_regions_raw': [37, 38, 39, 40, 42, 43,
                              44, 45, 46, 47, 48, 49,
                              50, 51, 66, 67, 68],
 'information_type': '発表',
 'information_type_en': 'Issue',
 'information_type_no': 0,
 'long_period_ground_motion_lower_limit': None,
 'long_period_ground_motion_lower_limit_raw': 0,
 'long_period_ground_motion_upper_limit': None,
 'long_period_ground_motion_upper_limit_raw': 0,
 'magnitude': '7.2',
 'magnitude_raw': 72,
 'message': b'\xc6\xaf\x89\xa8 \x00\x03$\x00\x00P@\x05H\xc5\xe2\xc0\x00\x00\x00'
            b'\x03\xdf\xf8\x00\x1c\x00\x00\x11\x85D?\xc0',
 'message_header': '$QZQSM',
 'message_type': 'DCR',
 'nmea': '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05',
 'notifications_on_disaster_prevention': ['強い揺れに警戒してください。'],
 'notifications_on_disaster_prevention_raw': [201],
 'occurrence_time_of_earthquake': datetime.datetime(2024, 3, 10, 1, 0, tzinfo=datetime.timezone.utc),
 'occurrence_time_of_earthquake_raw': {'day': 10, 'hour': 1, 'minute': 0},
 'preamble': 'C',
 'raw': b'\xaf\x89\xa8 \x00\x03$\x00\x00P@\x05H\xc5\xe2\xc0\x00\x00\x00\x03'
        b'\xdf\xf8\x00\x1c\x00\x00\x10',
 'report_classification': '訓練/試験',
 'report_classification_en': 'Training/Test',
 'report_classification_no': 7,
 'report_time': datetime.datetime(2024, 3, 10, 1, 0, tzinfo=datetime.timezone.utc),
 'satellite_id': 55,
 'satellite_prn': 183,
 'satellite_svid': None,
 'seismic_epicenter': '日向灘',
 'seismic_epicenter_raw': 791,
 'seismic_intensity_lower_limit': '震度6弱',
 'seismic_intensity_lower_limit_raw': 8,
 'seismic_intensity_upper_limit': '〜程度以上',
 'seismic_intensity_upper_limit_raw': 11,
 'sentence': '$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*05',
 'timestamp': datetime.datetime(2024, 6, 21, 6, 40, 34, 960948, tzinfo=datetime.timezone.utc),
 'version': 1}
```
同じ情報を重複して受信したかどうかは、`==` で比べると判別できます。
```python
>>> msg2 = '$QZQSM,55,9AAF89A820000324000050400548C5E2C000000003DFF8001C0000123FB3EB0*03'
>>> report2 = azarashi.decode(msg2, 'nmea')
>>> report == report2
```
```
True
```

## DCX (MT44)
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

### メッセージの種類と衛星
| フィールド | 型 |
|---|---|
| `dcx_message_type` | `str` |
| `dcx_version` | `int` |
| `satellite_designation_mask_type` | `str` |
| `satellite_designation_mask` | `list[str]` |

### A フィールド
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

### C フィールド
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

### D フィールド
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

### EX フィールド
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

### デコードした例
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
 'camf': Camf(sdmt=0, sdm=96, a1=1, a2=111, a3=1, a4=74, a5=2, a6=0, a7=9421, a8=2, a9=1, a10=0, a11=773, a12=45761, a13=116395, a14=13, a15=11, a16=48, a17=0, a18=0, ex1=13104, ex2=0, ex3=0, ex4=0, ex5=0, ex6=0, ex7=0, ex8=0, ex9=7376896189632872448, ex10=0, vn=1, c1=0, c2=0, c3=0, c4=0),
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
