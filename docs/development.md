[azarashi](../README.md) / Development

# Development
リポジトリを取得して開発用のツールをインストールすると、テストと静的解析を実行できます。GitHub Actions も、push と pull request のたびに同じチェックを実行します。
```shell
$ pip install -e . pytest pytest-cov 'jsonschema[format]' ruff mypy 'pyright[nodejs]' types-pyserial
$ python -m pytest tests        # CI は Python 3.11 から 3.14 で実行します
$ python -m pytest --cov=azarashi tests  # カバレッジも測るとき。設定: pyproject.toml の [tool.coverage]
$ ruff check .                  # 規則: pyproject.toml の [tool.ruff]
$ mypy --strict azarashi/       # 型検査
$ pyright                       # 設定: pyproject.toml の [tool.pyright]
```
GitHub Actions の typing ジョブは、ビルドした wheel をインストールして、利用者と同じ立場で型検査をします。確かめている内容は次のとおりです。

- `tests/typing/consumer.py` の正しい使い方が、エラーなく通ること
- `tests/typing/consumer_mistakes.py` の誤った使い方が、エラーとして検出されること
- `tests/typing/generate_mistakes.py` が作る誤用が、すべて検出されること。誤用は、公開している関数とメソッドのすべての引数と戻り値、およびプロパティの戻り値について作ります

CI は、内部のデコーダー間の受け渡しも検査します。`tests/typing/decoder_mistakes.py` は、
QZSS L1S デコーダーへの必須値の欠落・型違い・引数名の誤記と、DCR と DCX のデコーダーへの誤った context の受け渡しを含みます。
CI は mypy と Pyright の両方で、各行が意図した種類のエラーになることを確認します。
`decoders.qzss.l1s.Decoder` の `sentence`・`message`・`timestamp` には既定値がありません。入力のデコーダーは、この3つを渡し、`timestamp` には自分が決めた受信時刻を渡します。

デコーダーは、内部で `Frame` → `Message` → `Jma`（DCR）の順に型付きの情報を渡し、最後のレポートだけを生成します。
入力のデコーダーは `InputDecoder` を、後続の段階のデコーダーは `ContextDecoder` を継承します。後続の段階のデコーダーは、
受信時刻や発表時刻などを `self.context` から直接読み、その段階で計算した値を自身の属性に保存します。
DCX のデコーダーは、レポートを生成するときに、設定済みのフィールドだけをキーワード引数に変換して渡します。
これにより、`get_params()` が返す辞書には未設定のフィールドが含まれません。
公開レポートで互換性を維持する範囲は [Reports](reports.md#construction-mutation-and-subclassing) を参照してください。

`tests/test_reports.py` は、レポートの生成・変更・継承を確かめます。
レポートのコンストラクタ間で受け渡す `**kwargs` には `Any` が含まれるため、自動生成した誤用テストでは
コンストラクタの型の誤りをすべて検出できるわけではありません。

また `tests/test_declared_types.py` は、実際にデコードしたレポートの値が、宣言した型に合っていることを確かめます。

`tests/test_v0_16_4.py` は、v0.16.4 のレポートにあった属性とメソッドが、いまのレポートにもあることを確かめます。
属性とメソッドの一覧 `tests/v0_16_4_reports.json` は、v0.16.4 のタグを取り出してログをデコードし、一度だけ作ったものです。作り直す必要はありません。

`tests/golden/` には、`tests/*.log` のサンプルログにある全メッセージのデコード結果を保存してあります。保存しているのは、`str()` の文章と全フィールドの値です。出力が変わるとテストが失敗します。意図して出力を変えたときは、`python tests/test_golden.py` で再生成し、差分を確認してからコミットしてください。

テスト用のメッセージは、`tests/qzqsm.py` を使ってフィールドの値から組み立てられます。`tests/qzqsm.py` は、CRC とチェックサムも自動で計算します。
```python
from qzqsm import jma, sfrbx
sentence = jma(11, [(53, 4, 2), (57, 40, 830303020300)])  # 洪水: 鬼怒川の氾濫警戒情報
frame = sfrbx(sentence)  # 同じメッセージの UBX-RXM-SFRBX
```

## Source Layout

`definitions` と `decoders` は、どちらも、入力の形式・衛星システム・共通警報形式（CAMF）でディレクトリを分けています。

| 所属 | 定義 | デコード処理 |
|---|---|---|
| NMEA / UBX | `definitions/nmea.py`, `ubx.py` | `decoders/nmea.py`, `ubx.py` |
| QZSS L1S | `definitions/qzss/l1s.py` | `decoders/qzss/l1s.py` |
| 気象庁 DCR | `definitions/qzss/dcr/` | `decoders/qzss/dcr.py` |
| DCX | `definitions/qzss/dcx/` | `decoders/qzss/dcx.py` |
| CAMF 共通部分 | `definitions/camf/` | `decoders/camf/` |

コード表を置く場所は、**どのフィールドがその表を引くか**で決めます。CAMF のフィールドが引く表は
`definitions/camf/` に置きます。値を誰が決めるかは問いません。A3 の提供者は各国が割り当て、
A11 の国別ライブラリの文言はその国のものですが、CAMF のメッセージを運ぶどのサービスも同じ表を読むので
`definitions/camf/` に置きます。新しいサービスが加わっても、表が増えるのではなく項目が増えます。

サービスが CAMF に足したフィールドの表は、そのサービスの下に置きます。DCX の場合、そのような表は、拡張領域の
EX1・EX2・EX9 の表と、DCX 自身のメッセージ種別の表の4つです。

`a3_provider_identifier_map` のキーは、国名ではなく A2 の国コードです。メッセージが
運ぶのはコードで、国名は改称されることがあってもコードは変わらないからです。

JSON 出力のコードは `azarashi/json/` にあります。`__init__.py` は、公開する関数と、レポートの `to_json_dict()`・`to_ndjson()` が使う変換を持ちます。
`model.py` は、レポートから JSON への対応を持ちます。`tables.py` は、レコードが参照するコード表の一覧を持ちます。`schemas/` には、配布するスキーマがあります。
`json_code_tables()` は、呼ばれたときに `tables.py` からコード表を作ります。そのため、コード表のファイルは配布物に含めません。
`docs/json/code-tables-v2.json` も `tables.py` から作ります。コードの名前や `special` を変えたら、
`PYTHONPATH=.:tests python -m examples.generate` で作り直してください。テストは、このファイルと `json_code_tables()` が一致することを確かめます。
スキーマは、`tests/examples/schema.py` が、`model.py` の `PROFILES` などの変換の表から作ります。スキーマを変えるときは、
`tests/examples/schema.py` を直し、同じコマンドで作り直してください。テストは、作ったスキーマと配布するスキーマが一致することを確かめます。
スキーマは配布物に含めるので、`setup.py` の `package_data` に `azarashi.json` として登録しています。

`definitions/code_table.py` の `CodeTable` は、未定義コードの扱いを備えた辞書です。
QZSS の PRN と UBX の SVID の対応は `definitions/qzss/ubx.py` に置きます。
入力のデコーダーが対応している衛星システムは、今は QZSS だけです。QZSS に固有の context と補助処理は `decoders/qzss/` に置きます。
モジュール名は `ubx` ですが、公開 API の形式名は `ublox` です。

`definitions/camf/` には A1〜A11、A17、C7〜C10、D1〜D36 の表を置きます。共通処理は A12〜A15 の座標・
半軸長の変換で、`decoders/camf/geometry.py` にあります。これらの表のコードの意味と変換は、CAMF Issue 1.2
（2026年3月、現行版）の 3.1、3.2、3.3、3.5、3.6、3.7 節と照合しています。
公開されている [Issue 1.1](https://www.gsc-europa.eu/sites/default/files/sites/all/files/EWSS-CAMF_v1.1.pdf)
は前の版です。表示の文言と、未定義の値の扱いは、azarashi が決めたものです。
Galileo EWSS を追加する際も、伝送やビット位置の処理を各システムに置き、CAMF のフィールドの表は
そのまま共有します。

`tests/test_definition_values.py` は、コード表の値と未定義値の文言を参照スナップショットと比較します。
表を更新する際は `tests/definition_values.json` の該当する期待値も、変更内容と照合して更新してください。

DCR の表の英語は、各モジュールの中で、日本語の隣にあります。モジュールの docstring には、英語の出典と、azarashi が訳した項目を書きます。
英語を変えたら、`tests/definition_values.json` の期待値を直し、`PYTHONPATH=.:tests python -m examples.generate` で JSON の例を作り直してください。
英語の方針は [English Translation Policy](english-translation-policy.md) にあります。

## Release
リリースは、GitHub のリリースを公開して行います。公開すると `.github/workflows/release.yml` が wheel と sdist を作り、PyPI に公開します。
途中で承認を求められることはありません。PyPI に一度公開した版番号は、取り消しても同じ番号で出し直せません。

版番号は `0.<IS-QZSS-DCR の版>.<修正の番号>` です。IS-QZSS-DCR-017 に対応している間は 0.17.x で、修正や機能の追加では最後の数だけを上げます。
新しい IS-QZSS-DCR の版に対応したら、2番目の数をその版に合わせ、最後の数を0に戻します。IS-QZSS-DCR-018 に対応した版は 0.18.0 です。

タグの名前は、版番号の前に `v` を付けたものです。たとえば `v0.17.1` です。リリースの題名もタグと同じにします。
タグは、確かめたコミットに1つだけ付けます。公開したあとは付け直しません。

1. 上の規則で版番号を決め、`setup.py` の `version` を書き換えてコミットします。
2. リリースするコミットを push し、GitHub Actions の Test がすべて通ることを確かめます。同じ push で動く Dependency Graph は、Test ではありません。
3. リリースするコミットからパッケージを作り、中身を確かめます。前の版の wheel と、入っているファイルを比べます。
   新しい環境に wheel を入れ、デコードと CLI が動くことも確かめます。
   展開先には空のディレクトリを用意し、その中でビルドします。確認後は、元のリポジトリに戻ります。
   ```shell
   $ git archive <commit> | tar -x -C <展開先のディレクトリ>
   $ cd <展開先のディレクトリ>
   $ python -m build
   $ python -m twine check dist/*
   $ pip download --no-deps azarashi==<前の版> -d <別のディレクトリ>
   $ cd -
   ```
4. リリースノートを書きます。リポジトリには置かず、ほかの場所のファイルにします。
   見出しは前の版にならい、`## Highlights`、`## Upgrade Notes`、`## Added`、`## Fixed` などにします。
   最後に `Tested on Python 3.11 to 3.14.` と、`**Full Changelog**: https://github.com/nbtk/azarashi/compare/v<前の版>...v<この版>` を書きます。
5. タグとその版が、まだ GitHub にも PyPI にもないことを確かめてから、リリースを作って公開します。
   ```shell
   $ gh release create v<この版> --target <commit> --title v<この版> --notes-file <リリースノートのファイル>
   ```
6. Actions の Upload Python Package to PyPI が成功したことを確かめます。PyPI の最新版が新しい版になり、`pip install azarashi==<この版>` でその版が入ることも確かめます。
