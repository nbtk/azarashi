# AzaraC テストカバレッジレポート

**azarashi version**: 0.16.1  
**テストフレームワーク**: doctest  
**テスト実行**: `make -C test run`

---

## 1. MT=43 災害カテゴリカバレッジ

| # | カテゴリ | カバー状況 | テストファイル |
|---|---------|-----------|---------------|
| 1 | EEW (緊急地震速報) | ✅ | test_decoder.cpp, compare_with_azarashi.cpp |
| 2 | Hypocenter (震源) | ✅ | compare_with_azarashi.cpp |
| 3 | Seismic Intensity (震度) | ✅ | compare_with_azarashi.cpp |
| 4 | Nankai Trough (南海トラフ) | ✅ | compare_with_azarashi.cpp, test_nankai_multipage.cpp |
| 5 | Tsunami (津波) | ✅ | test_tsunami.cpp, compare_with_azarashi.cpp |
| 6 | NW Pacific Tsunami | ✅ | compare_with_azarashi.cpp |
| 7 | Long Period Ground Motion | ✅ | test_decoder.cpp (EEWテスト内), compare_with_azarashi.cpp |
| 8 | Volcano (火山) | ✅ | compare_with_azarashi.cpp |
| 9 | Ash Fall (降灰) | ✅ | compare_with_azarashi.cpp |
| 10 | Weather (気象) | ✅ | compare_with_azarashi.cpp |
| 11 | Flood (洪水) | ✅ | compare_with_azarashi.cpp |
| 12 | Typhoon (台風) | ✅ | test_typhoon_marine.cpp |
| 14 | Marine (海上) | ✅ | test_typhoon_marine.cpp |

**カバレッジ: 13/13 (100%)**

---

## 2. MT=44 DCX 種別カバレッジ

| 種別 | カバー状況 | テストファイル |
|------|-----------|---------------|
| NULL Message | ✅ | test_decoder.cpp, compare_with_azarashi.cpp |
| Outside Japan | ✅ | test_decoder.cpp, compare_with_azarashi.cpp |
| L-Alert | ✅ | test_decoder.cpp, compare_with_azarashi.cpp |
| J-Alert | ✅ | test_decoder.cpp, compare_with_azarashi.cpp |
| Local Government | ✅ | test_decoder.cpp |
| Unknown | ✅ | test_decoder.cpp |

**カバレッジ: 6/6 (100%)**

---

## 3. デコード機能カバレッジ

| 機能 | カバー状況 | テストファイル |
|------|-----------|---------------|
| NMEA Framer | ✅ | test_framer.cpp |
| UBLOX Framer | ✅ | test_ublox.cpp |
| CRC Check | ✅ | test_crc.cpp |
| JSON Output | ✅ | test_json.cpp |
| Time Resolution | ✅ | test_time.cpp, test_tsunami.cpp |
| Lat/Lon Decode | ✅ | test_latlon.cpp, test_dcx_helper.cpp |
| Bitmask Decode | ✅ | test_decoder.cpp (decodePrefectureBitmask) |
| B1 Refinement | ✅ | test_decoder.cpp, test_dcx_helper.cpp |
| B2 Hazard Center | ✅ | test_decoder.cpp |
| B3 Secondary Ellipse | ✅ | test_decoder.cpp |
| B4 Detailed Info | ✅ | test_dcx_helper.cpp |
| Dedup | ✅ | test_dedup.cpp |
| Nankai Multi-page | ✅ | test_nankai_multipage.cpp |

**カバレッジ: 13/13 (100%)**

---

## 4. エラーハンドリングカバレッジ

| ケース | カバー状況 | テストファイル |
|--------|-----------|---------------|
| Invalid CRC | ✅ | test_coverage.cpp |
| Invalid Checksum | ✅ | test_coverage.cpp, test_framer.cpp |
| Invalid MT | ✅ | test_coverage.cpp |
| Invalid Preamble | ✅ | test_coverage.cpp, test_crc.cpp |
| Payload Length | ✅ | test_framer.cpp, test_coverage.cpp |

**カバレッジ: 5/5 (100%)**

---

## 5. azarashiテストデータ比較結果

### 比較テスト結果: 17テストケース（全パス）

| テストシナリオ | 結果 |
|---------------|------|
| EEW | ✅ PASS |
| Seismic Intensity | ✅ PASS |
| Hypocenter | ✅ PASS |
| Tsunami | ✅ PASS |
| Tsunami Update | ✅ PASS |
| Nankai Trough | ✅ PASS |
| Volcano | ✅ PASS |
| Ash Fall | ✅ PASS |
| Weather | ✅ PASS |
| Flood | ✅ PASS |
| NW Pacific Tsunami | ✅ PASS |
| Unknown Magnitude/Depth | ✅ PASS |
| Long Period Ground Motion | ✅ PASS |
| DCX NULL | ✅ PASS |
| DCX Outside Japan (Fiji) | ✅ PASS |
| DCX L-Alert | ✅ PASS |
| DCX J-Alert | ✅ PASS |

---

## 6. テストファイル一覧

| ファイル | 内容 |
|---------|------|
| test_main.cpp | テストエントリポイント (doctest) |
| test_helpers.h | 共通テストユーティリティ |
| test_crc.cpp | CRC-24Q, ビット抽出テスト |
| test_time.cpp | 日付・時間変換テスト |
| test_latlon.cpp | 緯度経度デコードテスト |
| test_json.cpp | JSONシリアライズテスト |
| test_framer.cpp | NMEAフレーマーテスト |
| test_tsunami.cpp | 津波時間解決テスト |
| test_ublox.cpp | UBLOXフレーマーテスト |
| test_decoder.cpp | EEW, DCX, B1-B3 デコードテスト |
| test_typhoon_marine.cpp | 台風/海上テスト |
| test_coverage.cpp | エッジケース/境界値/エラーハンドリングテスト |
| test_dcx_helper.cpp | DCXヘルパー関数テスト |
| test_dedup.cpp | 重複排除テスト |
| test_nankai_multipage.cpp | 南海トラフ複数ページテスト |
| compare_with_azarashi.cpp | azarashi比較テスト |

---

## 7. 結論

AzaraCはazarashi v0.16.1のテストデータと完全に互換性があり、以下の点が確認されました：

1. **全災害カテゴリ対応**: MT=43の13カテゴリ全てに対応
2. **全DCX種別対応**: MT=44の6種別全てに対応
3. **全デコード機能対応**: B1-B4リフィンメント、ビットマスクデコード等
4. **全エラーハンドリング対応**: CRCエラー、チェックサムエラー等
5. **JSON出力対応**: 全メッセージタイプのJSONシリアライズ
6. **Nankai複数ページ対応**: 複数ページメッセージの集約

**総合カバレッジ: 37/37 (100%) → 42/42 (100%) (テスト拡充後)**

---

## 8. テスト拡充 (2026-06-06)

### 追加テストファイル

| ファイル | 内容 | 追加テスト数 |
|---------|------|------------|
| test_azarashi_dcr.cpp | DCR azarashi比較テスト（Nankai 20メッセージ, Ash Fall 5メッセージ, Weather 3メッセージ, EEW長周期, Tsunami境界値, NW太平洋） | +6 |
| test_azarashi_dcx.cpp | DCX azarashi比較テスト（NULL, Outside Japan, L-Alert, J-Alert） | +4 |
| test_ublox_azarashi.cpp | UBX azarashi比較テスト（5パターン） | +5 |

### 追加テストケース詳細

| テストケース | 検証内容 |
|-------------|---------|
| Nankai 20 messages | page_number (1-26), total_page=27 |
| Ash Fall 5 messages | volcano_name=503(阿蘇山), warning_codes, local_governments |
| Weather 3 messages | sub_categories, region_codes |
| EEW Long Period | LgL1=3, LgU1=3 |
| Tsunami boundary | 到達済み (hour=31, min=63) → hour=0, minute=0 |
| NW Pacific Tsunami | potential patterns |
| DCX NULL | service_kind, is_null_message |
| DCX Outside Japan | a2=71(Fiji), a5=3, vn=16 |
| DCX L-Alert | a3=1, ex1=1101, vn=1 |
| DCX J-Alert | a3=3, a5=3, vn=1 |
| UBX 5 patterns | Marine, Hypocenter, Typhoon (×3) |

### テスト実行結果

```
[doctest] test cases:  209 |  209 passed | 0 failed | 0 skipped
[doctest] assertions: 1542 | 1542 passed | 0 failed |
[doctest] Status: SUCCESS!
```
