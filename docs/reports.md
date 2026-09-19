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
`QzssDcReportBase` のフィールドです。どのレポートにもあります。
| フィールド | 型 |
|---|---|
| `sentence` | `str \| bytes` |
| `raw` | `bytes` |
| `timestamp` | `datetime` |

メッセージを取り出せたレポートには、`QzssDcReportMessagePartial` のフィールドが加わります。
| フィールド | 型 |
|---|---|
| `message` | `bytes` |
| `nmea` | `str` |
| `message_header` | `str \| bytes \| None` |
| `satellite_id` | `int \| None` |
| `satellite_prn` | `int \| None` |
| `satellite_svid` | `int \| None` |

`hex` 形式のようにヘッダや衛星の情報を持たないメッセージでは、`message_header` と `satellite_id` と `satellite_prn` は `None` です。`satellite_svid` は u-blox から受け取ったときだけ値が入ります。

DCR と DCX のレポートには、さらに `QzssDcReportMessageBase` の次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `preamble` | `str` |
| `message_type` | `str` |

## JMA-DC Report
気象庁が発表する災危通報のレポートです。`QzssDcReportJmaBase` を継承します。共通のフィールドは次のとおりです。
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
| 1 | 緊急地震速報 | `QzssDcReportJmaEarthquakeEarlyWarning` |
| 2 | 震源 | `QzssDcReportJmaHypocenter` |
| 3 | 震度 | `QzssDcReportJmaSeismicIntensity` |
| 4 | 南海トラフ地震 | `QzssDcReportJmaNankaiTroughEarthquake` |
| 5 | 津波 | `QzssDcReportJmaTsunami` |
| 6 | 北西太平洋津波 | `QzssDcReportJmaNorthwestPacificTsunami` |
| 8 | 火山 | `QzssDcReportJmaVolcano` |
| 9 | 降灰 | `QzssDcReportJmaAshFall` |
| 10 | 気象 | `QzssDcReportJmaWeather` |
| 11 | 洪水 | `QzssDcReportJmaFlood` |
| 12 | 台風 | `QzssDcReportJmaTyphoon` |
| 14 | 海上 | `QzssDcReportJmaMarine` |

### QzssDcReportJmaEarthquakeEarlyWarning
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

### QzssDcReportJmaHypocenter
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

### QzssDcReportJmaSeismicIntensity
震度のレポートです。`disaster_category_no` は 3 です。上の共通フィールドに加えて、次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `occurrence_time_of_earthquake` | `datetime \| None` |
| `occurrence_time_of_earthquake_raw` | `DayHourMinute` |
| `seismic_intensities` | `list[str]` |
| `seismic_intensities_raw` | `list[int]` |
| `prefectures` | `list[str]` |
| `prefectures_raw` | `list[int]` |

### QzssDcReportJmaNankaiTroughEarthquake
南海トラフ地震のレポートです。`disaster_category_no` は 4 です。上の共通フィールドに加えて、次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `information_serial_code` | `str` |
| `information_serial_code_raw` | `int` |
| `text_information` | `bytes` |
| `page_number` | `int` |
| `total_page` | `int` |

### QzssDcReportJmaTsunami
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

### QzssDcReportJmaNorthwestPacificTsunami
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

### QzssDcReportJmaVolcano
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

### QzssDcReportJmaAshFall
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

### QzssDcReportJmaWeather
気象のレポートです。`disaster_category_no` は 10 です。上の共通フィールドに加えて、次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `weather_warning_state` | `str` |
| `weather_warning_state_raw` | `int` |
| `weather_related_disaster_sub_categories` | `list[str]` |
| `weather_related_disaster_sub_categories_raw` | `list[int]` |
| `weather_forecast_regions` | `list[str]` |
| `weather_forecast_regions_raw` | `list[int]` |

### QzssDcReportJmaFlood
洪水のレポートです。`disaster_category_no` は 11 です。上の共通フィールドに加えて、次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `flood_warning_levels` | `list[str]` |
| `flood_warning_levels_raw` | `list[int]` |
| `flood_forecast_regions` | `list[str]` |
| `flood_forecast_regions_raw` | `list[int]` |

### QzssDcReportJmaTyphoon
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

### QzssDcReportJmaMarine
海上のレポートです。`disaster_category_no` は 14 です。上の共通フィールドに加えて、次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `marine_warning_codes` | `list[str]` |
| `marine_warning_codes_raw` | `list[int]` |
| `marine_forecast_regions` | `list[str]` |
| `marine_forecast_regions_raw` | `list[int]` |

## DCX
DCX メッセージのレポートです。`QzssDcXtendedMessageBase` を継承します。デコード例は [DCX](dcx.md) を見てください。

発信元ごとに、次のクラスが返ります。

| 発信元 | クラス |
|---|---|
| CAMF フィールドを使わないメッセージ | `QzssDcxNullMsg` |
| 日本国外の機関 | `QzssDcxOutsideJapan` |
| L-Alert | `QzssDcxLAlert` |
| J-Alert | `QzssDcxJAlert` |
| 自治体 | `QzssDcxMTInfo` |
| 上記以外 | `QzssDcxUnknown` |

警報のフィールドは `QzssDcxAlertBase` で宣言しています。上の表の `QzssDcxNullMsg` 以外の5クラスが、これを継承します。

メッセージの種類や内容によって設定されないフィールドは `None` になります。型も `float | None` のように宣言してあるので、型検査で気づけます。A1 から A10 までと `dcx_version` は必ず設定されるので `None` になりません。どのフィールド群が読まれたかは `ignore_a12_to_a16` などのフラグで分かります。

`QzssDcxNullMsg` は警報を持たないメッセージなので、これらのフィールドを一つも持ちません。読もうとすると型検査が止めます。

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
| `a11_international_library_code` | `str` |
| `a11_international_library` | `str` |
| `a11_japanese_library` | `str` |
| `a11_japanese_library_ja` | `str` |
| `a12_ellipse_centre_latitude` | `float` |
| `a13_ellipse_centre_longitude` | `float` |
| `a14_ellipse_semi_major_axis` | `float` |
| `a15_ellipse_semi_minor_axis` | `float` |
| `a16_ellipse_azimuth` | `float` |
| `a17_type_of_specific_settings` | `str` |

### C フィールド
| フィールド | 型 |
|---|---|
| `c1_refined_latitude_of_centre_of_main_ellipse` | `float` |
| `c2_refined_longitude_of_centre_of_main_ellipse` | `float` |
| `c3_refined_length_of_semi_major_axis` | `float` |
| `c4_refined_length_of_semi_minor_axis` | `float` |
| `c5_latitude_of_centre_of_hazard` | `float` |
| `c6_longitude_of_centre_of_hazard` | `float` |
| `c7_shift_of_second_ellipse_centre` | `int` |
| `c8_homothetic_factor_of_second_ellipse` | `float` |
| `c9_bearing_angle_of_second_ellipse` | `float` |
| `c10_instruction_library_for_second_ellipse_code` | `str` |
| `c10_instruction_library_for_second_ellipse` | `str` |

### D フィールド
| フィールド | 型 |
|---|---|
| `d1_magnitude_on_richter_scale` | `str` |
| `d2_seismic_coefficient` | `str` |
| `d3_azimuth_from_centre_of_main_ellipse_to_epicentre` | `float` |
| `d4_vector_length_between_centre_of_main_ellipse_and_epicentre` | `float` |
| `d5_wave_height` | `str` |
| `d6_temperature_range` | `str` |
| `d7_hurricane_category` | `str` |
| `d8_wind_speed` | `str` |
| `d9_rainfall_amounts` | `str` |
| `d10_damage_category` | `str` |
| `d11_tornado_probability` | `str` |
| `d12_hail_scale` | `str` |
| `d13_visibility` | `str` |
| `d14_snow_depth` | `str` |
| `d15_flood_severity` | `str` |
| `d16_lightning_intensity` | `str` |
| `d17_fog_level` | `str` |
| `d18_drought_level` | `str` |
| `d19_avalanche_warning_level` | `str` |
| `d20_ash_fall_amount_and_impact` | `str` |
| `d21_geomagnetic_scale` | `str` |
| `d22_terrorism_threat_level` | `str` |
| `d23_fire_risk_level` | `str` |
| `d24_water_quality` | `str` |
| `d25_uv_index` | `str` |
| `d26_number_of_cases_per_100000_inhabitants` | `str` |
| `d27_noise_range` | `str` |
| `d28_air_quality_index` | `str` |
| `d29_outage_estimated_duration` | `str` |
| `d30_nuclear_event_scale` | `str` |
| `d31_chemical_hazard_type` | `str` |
| `d32_biohazard_level` | `str` |
| `d33_biohazard_type` | `str` |
| `d34_explosive_hazard_type` | `str` |
| `d35_infection_type` | `str` |
| `d36_typhoon_category` | `str` |

### EX フィールド
| フィールド | 型 |
|---|---|
| `ex1_target_area` | `str` |
| `ex1_target_area_ja` | `str` |
| `ex2_evacuate_direction_type` | `str` |
| `ex3_additional_ellipse_centre_latitude` | `float` |
| `ex4_additional_ellipse_centre_longitude` | `float` |
| `ex5_additional_ellipse_semi_major_axis` | `float` |
| `ex6_additional_ellipse_semi_minor_axis` | `float` |
| `ex7_additional_ellipse_azimuth` | `float` |
| `ex8_target_area_list_type` | `str` |
| `ex9_target_area_list` | `list[str]` |
| `ex9_target_area_list_ja` | `list[str]` |

ほかに、ビットフィールドのままの値を持つ `camf` と、どの範囲を読み飛ばしたかを示す `ignore_a12_to_a16`、`ignore_a17_to_a18`、`ignore_ex1`、`ignore_ex2_to_ex7`、`ignore_ex8_to_ex9` があります。
