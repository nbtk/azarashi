[azarashi](../README.md) / [Reports](reports.md) / DCR

# DCR (MT43)
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

## dcr.EarthquakeEarlyWarning
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

## dcr.Hypocenter
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

## dcr.SeismicIntensity
震度のレポートです。`disaster_category_no` は 3 です。上の共通フィールドに加えて、次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `occurrence_time_of_earthquake` | `datetime \| None` |
| `occurrence_time_of_earthquake_raw` | `DayHourMinute` |
| `seismic_intensities` | `list[str]` |
| `seismic_intensities_raw` | `list[int]` |
| `prefectures` | `list[str]` |
| `prefectures_raw` | `list[int]` |

## dcr.NankaiTroughEarthquake
南海トラフ地震のレポートです。`disaster_category_no` は 4 です。上の共通フィールドに加えて、次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `information_serial_code` | `str` |
| `information_serial_code_raw` | `int` |
| `text_information` | `bytes` |
| `page_number` | `int` |
| `total_page` | `int` |

## dcr.Tsunami
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

## dcr.NorthwestPacificTsunami
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

## dcr.Volcano
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

## dcr.AshFall
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

## dcr.Weather
気象のレポートです。`disaster_category_no` は 10 です。上の共通フィールドに加えて、次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `weather_warning_state` | `str` |
| `weather_warning_state_raw` | `int` |
| `weather_related_disaster_sub_categories` | `list[str]` |
| `weather_related_disaster_sub_categories_raw` | `list[int]` |
| `weather_forecast_regions` | `list[str]` |
| `weather_forecast_regions_raw` | `list[int]` |

## dcr.Flood
洪水のレポートです。`disaster_category_no` は 11 です。上の共通フィールドに加えて、次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `flood_warning_levels` | `list[str]` |
| `flood_warning_levels_raw` | `list[int]` |
| `flood_forecast_regions` | `list[str]` |
| `flood_forecast_regions_raw` | `list[int]` |

## dcr.Typhoon
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

## dcr.Marine
海上のレポートです。`disaster_category_no` は 14 です。上の共通フィールドに加えて、次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `marine_warning_codes` | `list[str]` |
| `marine_warning_codes_raw` | `list[int]` |
| `marine_forecast_regions` | `list[str]` |
| `marine_forecast_regions_raw` | `list[int]` |

## Example
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
