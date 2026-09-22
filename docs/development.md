[azarashi](../README.md) / Development

# Development
リポジトリを取得して開発用のツールをインストールすると、テストと静的解析を実行できます。GitHub Actions でも push と pull request のたびに同じチェックを実行しています。
```shell
$ pip install -e . pytest pytest-cov 'jsonschema[format]' ruff mypy 'pyright[nodejs]' types-pyserial
$ python -m pytest tests        # Python 3.11 から 3.14 で実行しています
$ python -m pytest --cov=azarashi tests  # カバレッジも測るとき。設定: pyproject.toml の [tool.coverage]
$ ruff check .                  # 規則: pyproject.toml の [tool.ruff]
$ mypy --strict azarashi/       # 型検査
$ pyright                       # 設定: pyproject.toml の [tool.pyright]
```
GitHub Actions の typing ジョブは、ビルドした wheel をインストールして、利用者と同じ立場で型検査をします。確かめている内容は次のとおりです。

- `tests/typing/consumer.py` の正しい使い方が、エラーなく通ること
- `tests/typing/consumer_mistakes.py` の誤った使い方が、エラーとして検出されること
- `tests/typing/generate_mistakes.py` が作る誤用が、すべて検出されること。誤用は、公開している関数とメソッドのすべての引数と戻り値、およびプロパティの戻り値について作ります

内部のデコーダ間の受け渡しも検査します。`tests/typing/decoder_mistakes.py` は、
QZSS L1S デコーダへの必須値の欠落・型違い・引数名の誤記と、DCR/DCX 下流への誤った context の受け渡しを含みます。
CI は mypy と Pyright の両方で、各行が意図した種類のエラーになることを確認します。
`decoders.qzss.l1s.Decoder` には、
`sentence`・`message`・`nmea`・`timestamp` を明示し、受信時刻は入力段階で決めたものを渡します。

内部では `Frame` → `Message` → `Jma`（DCR）の順に型付き情報を渡し、最終レポートだけを生成します。
入力アダプターは `InputDecoder`、後続段階は `ContextDecoder` を使います。後続段階は
受信時刻や発表時刻などを `self.context` から直接読み、デコーダー自身にはその段階で計算した値を保存します。
DCX のレポートを生成するときは、設定済みのフィールドだけをキーワード引数に変換して渡します。
これにより、`get_params()` が返す辞書には未設定のフィールドが含まれません。
公開レポートで互換性を維持する範囲は [Reports](reports.md#construction-mutation-and-subclassing) を参照してください。

公開レポートの直接生成・変更・継承は `tests/test_reports.py` で検証します。
レポートのコンストラクタ間で受け渡す `**kwargs` には `Any` が含まれるため、自動生成した誤用テストでは
コンストラクタの型の誤りをすべて検出できるわけではありません。コンストラクタでの直接生成はサポートしていますが、型検査にはこの制限があります。

また `tests/test_declared_types.py` は、実際にデコードしたレポートの値が、宣言した型に合っていることを確かめます。

`tests/golden/` には、`tests/*.log` のサンプルログにある全メッセージのデコード結果を保存してあります。保存しているのは、`str()` の文章と全フィールドの値です。出力が変わるとテストが失敗します。意図して出力を変えたときは、`python tests/test_golden.py` で再生成し、差分を確認してからコミットしてください。

テスト用のメッセージは、`tests/qzqsm.py` を使ってフィールドの値から組み立てられます。CRC とチェックサムも自動で計算します。
```python
from qzqsm import jma, sfrbx
sentence = jma(11, [(53, 4, 2), (57, 40, 830303020300)])  # 洪水: 鬼怒川の氾濫警戒情報
frame = sfrbx(sentence)  # 同じメッセージの UBX-RXM-SFRBX
```

## Source Layout

`definitions` と `decoders` は、受信形式・衛星システム・共通警報形式の境界を揃えています。

| 所属 | 定義 | デコード処理 |
|---|---|---|
| NMEA / UBX | `definitions/nmea.py`, `ubx.py` | `decoders/nmea.py`, `ubx.py` |
| QZSS L1S | `definitions/qzss/l1s.py` | `decoders/qzss/l1s.py` |
| 気象庁 DCR | `definitions/qzss/dcr/` | `decoders/qzss/dcr.py` |
| DCX | `definitions/qzss/dcx/` | `decoders/qzss/dcx.py` |
| CAMF 共通部分 | `definitions/camf/` | `decoders/camf/` |

`definitions/code_table.py` の `CodeTable` は、未定義コードの扱いを備えた辞書です。
QZSS の衛星番号と UBX の SVID の対応は `definitions/qzss/ubx.py` に置きます。
入力アダプターは現在 QZSS に対応し、QZSS 固有の context と補助処理は `decoders/qzss/` に置きます。
公開 API の形式名は `ublox` です。

CAMF の共通定義は A1・A5・A6・A9・A17 の表、共通処理は A12〜A15 の座標・半軸長の変換です。
コードの意味と変換は [CAMF Issue 1.1](https://www.gsc-europa.eu/sites/default/files/sites/all/files/EWSS-CAMF_v1.1.pdf)
の 3.1.1、3.2.2、3.3.1、3.5.1、3.6、3.7 節と照合しています。
表示文言と未定義値の扱いはライブラリ側のものです。
その他の表は、国別の定義、対応ライブラリの版、共通仕様との照合範囲を区別するため DCX 側に置いています。
Galileo EWSS を追加する際も、伝送やビット位置の処理を各システムに置き、共通仕様と一致する部分を CAMF 側で共有します。

`definitions` と `decoders` のモジュール経路・クラス名は内部実装です。
公開の入口には `decode()` / `decode_stream()` を使い、レポートは `azarashi.reports` から参照してください。
`tests/test_definition_values.py` は、コード表の値と未定義値の文言を参照スナップショットと比較します。
表を更新する際は `tests/definition_values.json` の該当する期待値も、変更内容と照合して更新してください。
