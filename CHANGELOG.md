# Changelog

## [0.4.0] - 2026-05-20

### Added

- **テストスイートの拡充と検証カバレッジの強化**:
  - `test/test_ublox.cpp`: u-blox SFRBX (RXM-SFRBX) パケットに対するデコーダの動作検証、および NMEA 出力との整合性を確認するテストを新規追加。
  - `test/test_coverage.cpp`: MT=43 各防災カテゴリ（南海トラフ、降灰、洪水、気象、震度、火山等）の詳細フィールド検証、年末年始・うるう年等の日付境界テスト、および NMEA 文字数上限や不正プリアンブル等の異常系に対するエッジケーステストを新規追加。
- **デコーダ内部共通処理の共通関数化と符号付きパース関数の追加**:
  - `Decoder::readNotifications()`: 防災気象情報通知コード（9ビット）読み出しロジックを共通化。
  - `Decoder::resolveArrivalTime()`: 津波予測の到着日時（12ビット）計算ロジックを共通化。
  - `Decoder::extractSignedLatLon()`: 台風中心位置等の符号付き緯度・経度の抽出処理を共通化。
  - `Decoder::getSignedBits()`: 符号付きビットフィールド（2の補数表現）抽出ヘルパーを追加。
- `.gitignore` のアップデート: VSCode設定、エージェント用作業ファイル（`.agents/`）、ビルド中間ファイルなどを除外対象に追加。

### Changed

- **MT=44 (DCX) デコーダの IS-QZSS-DCX-003 仕様適合**:
  - MT=44 DCXメッセージデコーダおよびJSONシリアライズロジックを `IS-QZSS-DCX-003` 仕様に完全に適合するよう改修。
  - サービス種別（Service Kind: J-Alert, L-Alert, 地方自治体, 国外等）の識別ロジックを `A2 Country` および `A3 Provider` に基づき行うように修正。
  - 階層構造化されたCAMF（Common Alert Message Format）および各種拡張メッセージのパース処理を刷新し、テストベクタとシリアライズ出力を完全同期。
  - `Message.h` 上の `dcx_type` を `service_kind` へ変更し、`Mt44ServiceKind` / `ExtendedKind` 列挙型および拡張情報領域の各種サブ構造体（`Mt44Sd`, `Mt44CamfRaw`, `Mt44ExLAlertOrLocal`, `Mt44ExJAlert`, `Mt44ExOutside`）を定義。
- **モダンC++安全性向上 (C++17対応)**:
  - 定義ルックアップ関数の戻り値を `std::string_view` から `std::optional<std::string_view>` へ変更。
  - 値が見つからなかった場合に `std::nullopt` を返却するよう型安全性を強化し、不正なメモリアクセスや未定義動作をコンパイル時に防止。
  - 生成されるすべての検索関数（Switch文、配列、二分探索）に対して `[[nodiscard]]` 属性を付与し、戻り値の無視を防止。
- `scripts/gen_definitions.py`: `std::optional` および `[[nodiscard]]` への移行に伴い、自動生成されるヘッダーのテンプレートおよび生成スクリプトのロジックを更新。
- 手動管理定義ファイル (`qzss_dcx_camf_a3_provider_identifier.h` および `ublox_qzss_svid_prn_map.h`) も上記 C++17 安全設計に同期。
- `src/internal/JsonSerializer.cpp`:
  - `std::optional<std::string_view>` を受け取る `wf_s` 文字列出力関数のオーバーロードを追加・整理。
  - `std::nullopt` を受け取った際には安全に空文字列 (`""`) にフォールバックするよう `v.value_or("")` 処理を追加。
  - 暗黙の型変換に伴うコンパイル時のシグネチャ競合（ambiguous overloads）を解決するため、不要な中間型変換のオーバーロードを削除・最適化。
- **azarashi定義データのアップデート**:
  - 対応リファレンスバージョンを `azarashi 0.15.1` から `azarashi 0.16.1` へ更新（`.azarashi-version`）。
  - 自動生成ヘッダーのコメントテンプレートを `AUTO-GENERATED from azarashi {ver} with CI-CD` へ更新。
- **フレーマーの制限強化と検証精度向上**:
  - `NmeaFramer.cpp`: `IS-QZSS-DCX-003` 仕様に基づき、NMEA の hex 文字数が 63 文字であることを厳密に判定するよう変更。
  - `UbxFramer.cpp`: u-blox の L1S 信号判定において、`sigId == 0` に加えて `sigId == 1` も許容するようサポート範囲を拡大。
  - `PrintShim.h`: `std::string_view` のストリーム出力オーバーロードを追加。
- **テストコードにおけるプレースホルダー検証の修正**:
  - `test_azarashi.cpp` 等における `CHECK((ok || !ok))` のようなプレースホルダーテストを、`CHECK_FALSE(ok)` 等の実際のデコード失敗検証へと修正。

### Fixed

- **ビルド時の曖昧警告・エラーの解消**:
  - `JsonSerializer.cpp` のオーバーロード競合を解消するため、`std::optional` 型文字列解決用の `wf_s` オーバーロードを整理。
  - `make -C test run` が警告・コンパイルエラーなく、全113件のテストケース（578アサーション）を 100% SUCCESS で通過することを確認。

## [0.3.2] - 2026-05-12

### Fixed

- `test/test_json.cpp`: MT=43 Seismic Intensity テストケースのカテゴリIDミスを修正 (5 → 3)
- `test/test_azarashi.cpp`: 実態と乖離していたテストケース名 (`DCX: Null Msg`) を修正
- `test/test_crc.cpp`: DCXデコード時の誤解を招くコメントを修正
- `src/internal/JsonSerializer.cpp`: `writeInt32` における `INT32_MIN` 処理時の潜在的な未定義動作を回避
- `src/internal/JsonSerializer.cpp`: 災害カテゴリ (2, 3, 4, 5, 12, 14) のシリアライザ関数マッピングを修正

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
