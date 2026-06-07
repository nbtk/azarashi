# AzaraC 開発者ガイド

## 概要

AzaraCライブラリの開発に貢献する開発者向けのガイドです。

## 開発環境のセットアップ

### 必要なツール

| ツール | バージョン | 用途 |
|-------|-----------|------|
| g++ | C++17対応 | ホストテストビルド |
| Python | 3.9+ | 定義ファイル生成 |
| make | - | ビルド自動化 |

### リポジトリのクローン

```bash
git clone https://github.com/A-vrice/azaraC.git
cd azaraC
```

### Python環境のセットアップ

```bash
pip install azarashi
```

## プロジェクト構造

```
azaraC/
├── .github/workflows/        # CI/CD設定
├── docs/                     # ドキュメント
├── examples/                 # サンプルスケッチ
├── include/                  # 公開ヘッダ
│   ├── azaraC.h              # メインヘッダ
│   ├── Message.h             # メッセージ構造体
│   ├── Parser.h              # パーサー
│   ├── definition/           # 定義テーブル
│   └── internal/             # 内部ヘッダ
├── src/                      # 実装ファイル
│   └── Parser.cpp
├── scripts/                  # 定義ファイル生成スクリプト
│   └── gen_definitions.py
├── test/                     # テスト
│   ├── Makefile
│   ├── core/                 # コア機能テスト
│   ├── decoder/              # デコーダテスト
│   ├── framer/               # フレーマーテスト
│   ├── json/                 # JSONシリアライズテスト
│   ├── integration/          # 統合テスト
│   ├── fuzz/                 # ファジングテスト
│   └── data/                 # テストデータ
└── library.properties        # Arduinoライブラリ設定
```

## テスト

### テストの実行

```bash
# Linux / macOS / WSL
make -C test run

# Windows (MinGW-w64)
make -C test run MINGW64_BIN=C:\mingw64\bin
```

### テスト結果例

```
=== azaraC unit tests ===
  PASS  crc_known_zeros
  PASS  crc_known_a5
  ...
=== all passed ===
```

### テストカテゴリ

| ディレクトリ | 内容 |
|-------------|------|
| `core/` | CRC, 時間, 緯度経度, 重複除去 |
| `decoder/` | MT=43/44 デコーダ |
| `framer/` | NMEA/UBXフレーマー |
| `json/` | JSON出力検証 |
| `integration/` | エンドツーエンドテスト |
| `fuzz/` | ファジングテスト |

### ファジングテスト

```bash
make -C test fuzz FUZZ_ITERATIONS=100000
```

## 定義ファイルの自動生成

### 生成の仕組み

```
azarashi (PyPI) → definition/*.py
    ↓ scripts/gen_definitions.py
include/definition/*.h
    ↓ GitHub Actions (毎日 06:00 UTC)
PR自動作成 → レビュー → マージ
```

### 手動での生成

```bash
pip install --upgrade azarashi
python scripts/gen_definitions.py
```

## コーディング規約

### 命名規則

| 項目 | 規則 | 例 |
|------|------|-----|
| 名前空間 | `azaraC`, `azaraC::internal` | `azaraC::Parser` |
| クラス | PascalCase | `DedupFilter` |
| 関数 | camelCase | `feed()`, `decodeEEW()` |
| メンバ変数 | プレフィックス `_` | `_head`, `_mode` |
| 定数 | UPPER_SNAKE | `AZARAC_DEDUP_SLOTS` |

### メモリ管理

- **ヒープアロケーション禁止**: `new`, `malloc` を使用しない
- **静的バッファ**: 固定サイズの配列を使用

## 関連ドキュメント

- [API リファレンス](api-reference.md)
- [アーキテクチャドキュメント](architecture.md)
