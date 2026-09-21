[azarashi](../README.md) / Development

# Development
リポジトリを取得して開発用のツールをインストールすると、テストと静的解析を実行できます。GitHub Actions でも push と pull request のたびに同じチェックを実行しています。
```shell
$ pip install -e . pytest pytest-cov ruff mypy 'pyright[nodejs]' types-pyserial
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
共通デコーダへの必須値の欠落・型違い・引数名の誤記と、DCR/DCX 下流への誤った context の受け渡しを含みます。
CI は mypy と Pyright の両方で、各行が意図した種類のエラーになることを確認します。
`common.Decoder` は内部実装であり、任意の `**kwargs` を受け取る以前の呼び出し方は維持しません。
`sentence`・`message`・`nmea`・`timestamp` を明示し、受信時刻は入力段階で決めたものを渡します。

内部では `Frame` → `Message` → `Jma`（DCR）の順に型付き情報を渡し、最終レポートだけを生成します。
DCX の最終生成では、未設定フィールドを辞書に含めない公開契約を保つため、キーワード引数への変換を残しています。
公開レポートの互換範囲は [Reports](reports.md#construction-mutation-and-subclassing) を参照してください。

公開レポートの直接生成・変更・継承は `tests/test_reports.py` で検証します。
コンストラクタの継承先へ渡す `**kwargs` は `Any` を含むため、生成誤用テストは
レポートコンストラクタ全体の型安全性を保証しません。直接生成のサポートとは区別します。

また `tests/test_declared_types.py` は、実際にデコードしたレポートの値が、宣言した型に合っていることを確かめます。

`tests/golden/` には、`tests/*.log` のサンプルログにある全メッセージのデコード結果を保存してあります。保存しているのは、`str()` の文章と全フィールドの値です。出力が変わるとテストが失敗します。意図して出力を変えたときは、`python tests/test_golden.py` で再生成し、差分を確認してからコミットしてください。

テスト用のメッセージは、`tests/qzqsm.py` を使ってフィールドの値から組み立てられます。CRC とチェックサムも自動で計算します。
```python
from qzqsm import jma, sfrbx
sentence = jma(11, [(53, 4, 2), (57, 40, 830303020300)])  # 洪水: 鬼怒川の氾濫警戒情報
frame = sfrbx(sentence)  # 同じメッセージの UBX-RXM-SFRBX
```
