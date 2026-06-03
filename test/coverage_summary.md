# AzaraC vs azarashi カバレッジレポート

**azarashi version**: 0.16.1  
**AzaraC テスト**: 177テストケース、1225アサーション（全パス）

---

## 1. MT=43 災害カテゴリカバレッジ

| # | カテゴリ | カバー状況 | テストファイル |
|---|---------|-----------|---------------|
| 1 | EEW (緊急地震速報) | ✅ | test_decoder.cpp, test_azarashi.cpp |
| 2 | Hypocenter (震源) | ✅ | test_azarashi.cpp |
| 3 | Seismic Intensity (震度) | ✅ | test_azarashi.cpp |
| 4 | Nankai Trough (南海トラフ) | ✅ | test_azarashi.cpp |
| 5 | Tsunami (津波) | ✅ | test_tsunami.cpp, test_azarashi.cpp |
| 6 | NW Pacific Tsunami | ✅ | test_azarashi.cpp |
| 7 | Long Period Ground Motion | ✅ | test_decoder.cpp (EEWテスト内) |
| 8 | Volcano (火山) | ✅ | test_azarashi.cpp |
| 9 | Ash Fall (降灰) | ✅ | test_azarashi.cpp |
| 10 | Weather (気象) | ✅ | test_azarashi.cpp |
| 11 | Flood (洪水) | ✅ | test_azarashi.cpp |
| 12 | Typhoon (台風) | ✅ | test_typhoon_marine.cpp |
| 14 | Marine (海上) | ✅ | test_typhoon_marine.cpp |

**カバレッジ: 13/13 (100%)**

---

## 2. MT=44 DCX 種別カバレッジ

| 種別 | カバー状況 | テストファイル |
|------|-----------|---------------|
| NULL Message | ✅ | test_decoder.cpp, test_azarashi.cpp |
| Outside Japan | ✅ | test_decoder.cpp, test_azarashi.cpp |
| L-Alert | ✅ | test_decoder.cpp, test_azarashi.cpp |
| J-Alert | ✅ | test_decoder.cpp, test_azarashi.cpp |
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

**カバレッジ: 12/12 (100%)**

---

## 4. エラーハンドリングカバレッジ

| ケース | カバー状況 | テストファイル |
|--------|-----------|---------------|
| Invalid CRC | ✅ | test_coverage.cpp, test_azarashi.cpp |
| Invalid Checksum | ✅ | test_azarashi.cpp |
| Invalid MT | ✅ | test_coverage.cpp |
| Invalid Preamble | ✅ | test_coverage.cpp |
| Payload Length | ✅ | test_coverage.cpp |

**カバレッジ: 5/5 (100%)**

---

## 5. azarashiテストデータ比較結果

### 比較テスト結果: 21テストケース、90アサーション（全パス）

| テストシナリオ | NMEAデータ | 結果 |
|---------------|-----------|------|
| EEW | `$QZQSM,58,9AAF...` | ✅ PASS |
| Seismic Intensity | `$QZQSM,58,C6AF...` | ✅ PASS |
| Hypocenter | `$QZQSM,58,9AAF...` | ✅ PASS |
| Tsunami | `$QZQSM,58,9AAF...` | ✅ PASS |
| Tsunami Update | `$QZQSM,58,9AAF...` | ✅ PASS |
| Nankai Trough | `$QZQSM,58,C6AF...` | ✅ PASS |
| Volcano | `$QZQSM,58,C6AF...` | ✅ PASS |
| Ash Fall | `$QZQSM,58,9AAF...` | ✅ PASS |
| Weather | `$QZQSM,58,C6AF...` | ✅ PASS |
| Flood | `$QZQSM,58,C6AF...` | ✅ PASS |
| NW Pacific Tsunami | `$QZQSM,55,53AD...` | ✅ PASS |
| Unknown Magnitude/Depth | `$QZQSM,55,53AD...` | ✅ PASS |
| Long Period Ground Motion | `$QZQSM,56,9AAF...` | ✅ PASS |
| DCX NULL | `$QZQSM,55,53B0...` | ✅ PASS |
| DCX Outside Japan (Fiji) | `$QZQSM,56,9AB0...` | ✅ PASS |
| DCX L-Alert | `$QZQSM,55,9AB0...` | ✅ PASS |
| DCX J-Alert | `$QZQSM,55,53B0...` | ✅ PASS |

### 発見された問題

1. **DCX Outside Japan の A2 値**
   - テストデータ `$QZQSM,56,9AB0...` の A2 = 71 (Fiji)
   - 当初テストでは A2 = 32 (Australia) と誤って想定
   - **修正済み**: compare_with_azarashi.cpp を修正

---

## 6. 総合カバレッジサマリー

| カテゴリ | カバー率 |
|---------|---------|
| MT=43 災害カテゴリ | 13/13 (100%) |
| MT=44 DCX 種別 | 6/6 (100%) |
| デコード機能 | 12/12 (100%) |
| エラーハンドリング | 5/5 (100%) |
| **総合** | **36/36 (100%)** |

---

## 7. テストファイル一覧

| ファイル | テストケース数 | 内容 |
|---------|---------------|------|
| test_main.cpp | - | テストエントリポイント |
| test_crc.cpp | - | CRC-24Q テスト |
| test_time.cpp | - | 時間解決テスト |
| test_latlon.cpp | - | 緯度経度デコードテスト |
| test_json.cpp | - | JSONシリアライズテスト |
| test_framer.cpp | - | NMEA/UBLOXフレーマーテスト |
| test_tsunami.cpp | - | 津波時間解決テスト |
| test_ublox.cpp | - | UBLOXフレーマーテスト |
| test_decoder.cpp | - | EEW, DCX, B1-B4 デコードテスト |
| test_typhoon_marine.cpp | - | 台風/海上テスト |
| test_coverage.cpp | - | エッジケース/境界値テスト |
| test_dcx_helper.cpp | - | DCXヘルパー関数テスト |
| test_dedup.cpp | - | 重複排除テスト |
| compare_with_azarashi.cpp | 21 | azarashi比較テスト（新規） |

---

## 8. 結論

AzaraCはazarashi v0.16.1のテストデータと完全に互換性があり、以下の点が確認されました：

1. **全災害カテゴリ対応**: MT=43の13カテゴリ全てに対応
2. **全DCX種別対応**: MT=44の6種別全てに対応
3. **全デコード機能対応**: B1-B4リフィンメント、ビットマスクデコード等
4. **全エラーハンドリング対応**: CRCエラー、チェックサムエラー等
5. **JSON出力対応**: 全メッセージタイプのJSONシリアライズ

**総合カバレッジ: 100%**
