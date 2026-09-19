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

## Common Fields
`base.Base` のフィールドです。どのレポートにもあります。
| フィールド | 型 |
|---|---|
| `sentence` | `str \| bytes` |
| `raw` | `bytes` |
| `timestamp` | `datetime` |

メッセージを取り出せたレポートには、`base.MessagePartial` のフィールドが加わります。
| フィールド | 型 |
|---|---|
| `message` | `bytes` |
| `nmea` | `str` |
| `message_header` | `str \| bytes \| None` |
| `satellite_id` | `int \| None` |
| `satellite_prn` | `int \| None` |
| `satellite_svid` | `int \| None` |

`hex` 形式のようにヘッダや衛星の情報を持たないメッセージでは、`message_header` と `satellite_id` と `satellite_prn` は `None` です。`satellite_svid` は u-blox から受け取ったときだけ値が入ります。

DCR と DCX のレポートには、さらに `base.MessageBase` の次のフィールドがあります。
| フィールド | 型 |
|---|---|
| `preamble` | `str` |
| `message_type` | `str` |

## Message Formats
メッセージ形式が2つあり、返るクラスもフィールドも形式で変わります。仕様書も2冊に分かれています。

- [DCR (MT43)](dcr.md): 気象庁が発表する防災気象情報です。災害種別ごとにクラスが分かれます。
- [DCX (MT44)](dcx.md): 気象庁以外の機関が発表するメッセージです。発信機関ごとにクラスが分かれます。
