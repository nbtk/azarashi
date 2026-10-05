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
`decoders.qzss.l1s.Decoder` には `sentence`・`message`・`timestamp` を明示し、受信時刻は入力段階で決めたものを渡します。

内部では `Frame` → `Message` → `Jma`（DCR）の順に型付き情報を渡し、最終レポートだけを生成します。
入力アダプターは `InputDecoder`、後続段階は `ContextDecoder` を使います。後続段階は
受信時刻や発表時刻などを `self.context` から直接読み、デコーダー自身にはその段階で計算した値を保存します。
DCX のレポートを生成するときは、設定済みのフィールドだけをキーワード引数に変換して渡します。
これにより、`get_params()` が返す辞書には未設定のフィールドが含まれません。
公開レポートで互換性を維持する範囲は [Reports](reports.md#construction-mutation-and-subclassing) を参照してください。

レポートの生成・変更・継承は `tests/test_reports.py` で検証します。
レポートのコンストラクタ間で受け渡す `**kwargs` には `Any` が含まれるため、自動生成した誤用テストでは
コンストラクタの型の誤りをすべて検出できるわけではありません。

また `tests/test_declared_types.py` は、実際にデコードしたレポートの値が、宣言した型に合っていることを確かめます。

`tests/test_v0_16_4.py` は、v0.16.4 のレポートにあった属性とメソッドが、いまのレポートにもあることを確かめます。
一覧の `tests/v0_16_4_reports.json` は、v0.16.4 のタグを取り出してログをデコードし、一度だけ作ったものです。作り直す必要はありません。

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

コード表を置く場所は、**どのフィールドがその表を索くか**で決めます。CAMF のフィールドが索く表は
`definitions/camf/` に置きます。値を誰が決めるかは問いません。A3 の提供者は各国が割り当て、
A11 の国別ライブラリの文言はその国のものですが、CAMF のメッセージを運ぶどのサービスも同じ表を読むので
ここに置きます。新しいサービスが加わっても、表が増えるのではなく項目が増えます。

サービスが CAMF に足したフィールドの表は、そのサービスの下に置きます。DCX の場合は拡張領域の
EX1・EX2・EX9 と、DCX 自身のメッセージ種別の4つです。

`a3_provider_identifier_map` は A2 の国コードをキーにします。国名を識別子にしません。メッセージが
運ぶのはコードで、国名は改称される一方コードは変わらないからです。

JSON 出力は `azarashi/json/` にまとめます。`__init__.py` が公開する入口と、レポートの `to_json_dict()`・`to_ndjson()` が使う変換、`model.py` が
レポートから JSON への対応、`tables.py` がレコードの参照するコード表の一覧、`schemas/` が同梱する
スキーマです。`code_tables()` は `tables.py` からその場で作るので、コード表のファイルは配布物に含めません。
docs の `docs/json/code-tables-v2.json` も `tables.py` から作るので、コードの名前や `special` を変えたら
`PYTHONPATH=.:tests python -m examples.generate` で作り直します。テストが、ファイルと `code_tables()` の一致を確かめます。
スキーマも `tests/examples/schema.py` が変換の表（`model.py` の `PROFILES` など）から作ります。スキーマを変えるときは
このファイルを直し、同じコマンドで作り直します。テストが、配布するスキーマとの一致を確かめます。
スキーマは配布物に含めるので、`setup.py` の `package_data` に `azarashi.json` として登録しています。

`definitions/code_table.py` の `CodeTable` は、未定義コードの扱いを備えた辞書です。
QZSS の PRN と UBX の SVID の対応は `definitions/qzss/ubx.py` に置きます。
入力アダプターは現在 QZSS に対応し、QZSS 固有の context と補助処理は `decoders/qzss/` に置きます。
モジュール名は `ubx` ですが、公開 API の形式名は `ublox` です。

`definitions/camf/` には A1〜A11、A17、C7〜C10、D1〜D36 の表を置きます。共通処理は A12〜A15 の座標・
半軸長の変換で、`decoders/camf/geometry.py` にあります。コードの意味と変換は CAMF Issue 1.2
（2026年3月、現行版）の 3.1、3.2、3.3、3.5、3.6、3.7 節と照合しています。
公開されている [Issue 1.1](https://www.gsc-europa.eu/sites/default/files/sites/all/files/EWSS-CAMF_v1.1.pdf)
は前の版です。表示文言と未定義値の扱いはライブラリ側のものです。
Galileo EWSS を追加する際も、伝送やビット位置の処理を各システムに置き、CAMF のフィールドの表は
そのまま共有します。

`tests/test_definition_values.py` は、コード表の値と未定義値の文言を参照スナップショットと比較します。
表を更新する際は `tests/definition_values.json` の該当する期待値も、変更内容と照合して更新してください。

## Release
リリースは、GitHub のリリースを公開して行います。公開すると `.github/workflows/release.yml` が wheel と sdist を作り、PyPI に公開します。
途中で承認を求められることはありません。PyPI に一度公開した版番号は、取り消しても同じ番号で出し直せません。

版番号は `0.<IS-QZSS-DCR の版>.<修正の番号>` です。IS-QZSS-DCR-017 に対応している間は 0.17.x で、修正や機能の追加では最後の数だけを上げます。
新しい IS-QZSS-DCR の版に対応したら、2番目の数をその版に合わせ、最後の数を0に戻します。IS-QZSS-DCR-018 に対応した版は 0.18.0 です。

タグの名前は、版番号の前に `v` を付けたものです。例えば `v0.17.1` です。リリースの題名もタグと同じにします。
タグは、確かめたコミットに1つだけ付けます。公開したあとは付け直しません。

1. 上の規則で版番号を決め、`setup.py` の `version` を書き換えてコミットします。
2. リリースするコミットを push し、GitHub Actions の Test がすべて通ることを確かめます。同じ push で動く Dependency Graph は、Test ではありません。
3. リリースするコミットからパッケージを作り、中身を確かめます。前の版の wheel と、入っているファイルを比べます。
   新しい環境に wheel を入れ、デコードと CLI が動くことも確かめます。
   ```shell
   $ git archive <commit> | tar -x -C <空のディレクトリ>
   $ python -m build
   $ python -m twine check dist/*
   $ pip download --no-deps azarashi==<前の版> -d <別のディレクトリ>
   ```
4. リリースノートを書きます。リポジトリには置かず、ほかの場所のファイルにします。
   見出しは前の版にならい、`## Highlights`、`## Upgrade Notes`、`## Added`、`## Fixed` などにします。
   最後に `Tested on Python 3.11 to 3.14.` と、`**Full Changelog**: https://github.com/nbtk/azarashi/compare/v<前の版>...v<この版>` を書きます。
5. タグとその版が、まだ GitHub にも PyPI にもないことを確かめてから、リリースを作って公開します。
   ```shell
   $ gh release create v<この版> --target <commit> --title v<この版> --notes-file <リリースノートのファイル>
   ```
6. Actions の Upload Python Package to PyPI が成功したことを確かめます。PyPI の最新版が新しい版になり、`pip install azarashi==<この版>` でその版が入ることも確かめます。
