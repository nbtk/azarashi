# Changelog

## [0.3.2] - 2026-05-12

### Fixed

- `test/test_json.cpp`: MT=43 Seismic Intensity テストケースのカテゴリIDミスを修正 (5 → 3)
- `test/test_azarashi.cpp`: 実態と乖離していたテストケース名 (`DCX: Null Msg`) を修正
- `test/test_crc.cpp`: DCXデコード時の誤解を招くコメントを修正
- `src/internal/JsonSerializer.cpp`: `writeInt32` における `INT32_MIN` 処理時の潜在的な未定義動作を回避

### Changed

- `src/internal/Dedup.h`: `AZARAC_DEDUP_SLOTS` のデフォルト値を 8 から 32 に拡張 (重複排除の耐性向上)

## [0.3.1] - 2026-04-28

### Fixed

- Definition headers: `static constexpr` → `inline constexpr` 変更
  (linker-scope symbol となり、複数のソースからの参照が可能)
- `Decoder::decodeQzqsm` の unused-parameter 警告削除

## [0.3.0] - 2026-04-19

### Added (Phase 3)

- `examples/with_sntp`: Wi-Fi + SNTP 時刻解決 + EEW フィルタ付きサンプル
- `test/test_crc.cpp`: CRC-24Q / getBits / MT=44 合成フレーム 12 テスト
- `test/test_json.cpp`: DCX・EEW・震度・津波キー検証 + 全 disaster_category
  ブレースバランス検証 (28 テスト)
- `test/Makefile`: ホストビルド (`make -C test run`)
- CI: `host-test` ジョブ追加 (g++ ホストテスト → arduino-cli コンパイル の順)
- README: クイックスタート・API・JSON 出力例・定義自動生成フロー

### Fixed

- `JsonSerializer.h` / `PrintShim.h` / `azaraC.h`: `#ifdef ARDUINO` ガードを
  `#if defined(ARDUINO) && ARDUINO >= 1` に統一 (ARDUINO=0 ホストビルド対応)
- `Decoder.h`: テスト用サブクラスアクセスのため `private` → `protected`
- `Decoder.cpp`: `decodeTsunami` / `decodeNwPacTsu` の unused-parameter 警告修正


## [0.2.0] - 2026-04-19

### Added (Phase 2)

- MT=43 JMA DC Report full sub-type decode (all 12 categories):
  EEW, Hypocenter, Seismic Intensity, Nankai Trough, Tsunami,
  NW Pacific Tsunami, Volcano, Ash Fall, Weather, Flood, Marine, Typhoon
- `Message` struct extended with per-category fields and repeating record arrays
- `JsonSerializer`: MT=43 full JSON output with `detail` sub-object per category
- All label strings resolved via auto-generated `definition/_index.h` lookup functions
  (no disaster strings hardcoded — fully azarashi-driven)

### Changed

- `Decoder::decodeQzqsm` promoted from skeleton to full implementation
- `Message.h` restructured with sub-structs:
  `TsunamiEntry`, `SeismicEntry`, `WeatherEntry`, `FloodEntry`,
  `MarineEntry`, `NwPacTsunamiEntry`, `TyphoonPos`

## [0.1.0] - 2026-04-19

### Added (Phase 1)

- UBX (RXM-SFRBX) and NMEA ($QZQSM) framers
- CRC-24Q verification
- MT=44 DCX/CAMF full field extraction (A1-A13)
- MT=43 outer frame decode (skeleton)
- DedupFilter: ring-buffer keyed on {svid, msg_type, crc24}
- JsonSerializer: heap-free Print& output
- Parser: UBX/NMEA auto-detect, pluggable IFramer interface
- 102 definition headers auto-generated from azarashi 0.15.1
- CI: arduino-cli compile check on ESP32-C3
- CI: auto PR on azarashi version bump (daily schedule)
