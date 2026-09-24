[azarashi](../README.md) / English Translation Policy

# English Translation Policy

Every code table of the JMA-DC Report (DCR) but one has an English version beside its Japanese one,
in a table named `*_en` in `azarashi/definitions/qzss/dcr/`. The JSON output gives it as
`labels.en`. The exception is the Nankai Trough information, described below.
The Python reports and `str(report)` stay Japanese.

This page records where the English comes from, the rules it follows, and every English that is
azarashi's own, so that none of it is forgotten when JMA publishes more English.

## Why azarashi Shows English It Cannot Vouch For

azarashi cannot stand behind a translation the way JMA stands behind its own. A translation can be
wrong, and for a warning, a wrong translation can cost more than none. azarashi shows its English
all the same, for these reasons.

- **Saying nothing is also a message.** To a reader of English, a warning with no English is a
  warning that is not there. If "the tsunami will be higher on the coast" is left out, the report
  reads safer than it is. In disaster prevention, a warning missed costs more than a warning given
  when it was not needed; evacuation orders are issued early for the same reason.
- **Not reading Japanese is itself a risk.** People who cannot read Japanese are among those who
  need particular care in a disaster. JMA publishes its multilingual dictionary so that its
  warnings reach them, and IS-QZSS-DCR-017 follows that dictionary. azarashi's English goes the
  same way where JMA's own does not yet reach.
- **Most of what matters already has JMA's English.** The calls to evacuate, the Major Tsunami
  Warning, the Tsunami Warning and the Tsunami Advisory, and the warnings of a tsunami higher than
  estimated are JMA's English. What azarashi translates fills the gaps between them.

Showing the English is right only on these conditions, and azarashi keeps to them.

| Condition | How azarashi keeps it |
|---|---|
| It must not say less than the Japanese. | What the Japanese states as certain stays certain in English, and おそれ becomes "may", as JMA translates it. |
| It must not say more than the Japanese. | Nothing is added: no advice, no urgency and no detail the Japanese does not give. |
| The Japanese must stay at hand. | The JSON always gives `labels.ja` and the code beside `labels.en`. The Japanese is the meaning. |
| It must not pass for JMA's. | The sentences end in (Translated by azarashi), and this page lists every English that is azarashi's. |

Only the notification sentences carry the note. The short labels azarashi translated, such as
Marine Gale Warning and Other Volcano, carry none, so the JSON alone does not tell them apart from
JMA's English. They are short labels for a category or a value, not sentences. azarashi reviewed
their English and decided not to mark short labels. They are listed on this page instead, and the
JSON always gives the Japanese and the code beside them.

## Rules

1. **The English is JMA's wherever JMA gives it.** IS-QZSS-DCR-017 itself says its phrasing
   follows JMA's multilingual dictionary, and the dictionary is the main source. The sources are
   listed below.
2. **A match counts only within the section of the dictionary that fits the table.** The same
   Japanese can name a different thing in another section: 網走沖 is a marine forecast region and
   also an epicenter, with different English. Regions, volcanoes and epicenters are matched by the
   code of the JMA XML code table, the rest by their Japanese.
3. **The words are JMA's; only the spacing and the case are tidied.** Doubled or invisible spaces
   and full-width brackets are fixed. JMA writes the marine forecast regions in capitals (SEA OFF
   ABASHIRI); they begin each word with a capital here (Sea off Abashiri), as every other table
   does, with of, and, off and around in lower case after the first word. Where azarashi arranges
   JMA's words, it says so below.
4. **Where JMA gives no English, the English is azarashi's own**, so that what a report says,
   danger most of all, still reaches a reader of English. It is made of JMA's wording where JMA
   has one. It never says less than the Japanese: what the Japanese states as certain stays
   certain, and おそれ becomes "may", as JMA itself translates it.
5. **No English is better than an English nobody can stand behind.** The Nankai Trough
   information is an exception, described below. A river's name comes from an English source where
   there is one, then from an official reading of its kanji, and only then from the Japanese
   Wikipedia, with the date it was retrieved.
6. **The sentences azarashi translated carry a note.** Of the disaster prevention notifications,
   the eight sentences with no JMA English end in `(Translated by azarashi)`, so that the note
   goes wherever the sentence goes. Only these carry it, since they are the only sentences
   azarashi translated; the short labels it translated are listed on this page. The note says
   who translated the sentence. It does not mean an English without the note is JMA's.
   azarashi does not call its English official or unofficial.
7. **The Japanese is what JMA sent.** The JSON always gives `labels.ja` beside `labels.en`, and
   the Japanese is the meaning.
8. **azarashi's English stands in until JMA gives its own.** When JMA publishes English for an
   entry, JMA's English replaces azarashi's, the notifications first.
9. **Each module says which of its entries are azarashi's**, in its docstring.

## The Nankai Trough Information

The JMA-DC Report (Nankai Trough Earthquake) is an exception. It carries JMA's own Japanese text,
sent in pages; the JSON gives each page as `page.content_hex`, and `str(report)` shows the text once
the pages are put together. azarashi does not translate that text.

Its information serial codes (`information_serial_code`) are left in Japanese with it, and their
table has no English.

## Kinds of English

| Kind | What it is | Examples |
|---|---|---|
| JMA's | JMA's English as JMA writes it, with the spacing and case tidied | the regions, volcanoes and epicenters matched by code; 37 marine forecast regions; tsunami heights |
| JMA's words, arranged by azarashi | JMA's words put together the way the DCR names the entry | municipalities, flood forecast regions, notifications built from the dictionary's sentences |
| azarashi's | azarashi's translation, where JMA gives none | the entries listed below |

## Sources

| Source | Retrieved | Used for |
|---|---|---|
| JMA multilingual dictionary of weather information terms (気象情報等に関する多言語辞書), updated 2026-03-26 | 2026-09-24 | most tables |
| JMA sea warning page, <https://www.jma.go.jp/bosai/seawarning/#lang=en> | 2026-09-24 | marine forecast regions that are not divided further |
| JMA English marine warnings, <https://www.jma.go.jp/bosai/seawarning/data/warning_en/> | 2026-09-24 | six marine forecast regions that group others, named in NO WARNING FOR ... |
| JMA map of disaster information, <https://www.jma.go.jp/bosai/map.html> | 2026-09-24 | Less than 0.2 m, and Less than for 未満 |
| JMA English guide to tsunami warnings, <https://www.data.jma.go.jp/eqev/data/en/guide/tsunamiinfo.html> | 2026-09-24 | tsunami heights 1 m to 10 m |
| IS-QZSS-DCR-017 | | Analysis, Estimate and Forecast; Preliminary and Detailed; Heavy Rain Emergency Warning; Record-breaking heavy rain in a short time |
| MLIT Kanto Regional Development Bureau, Edogawa River Office, <https://www.ktr.mlit.go.jp/edogawa/edogawa00576.html> | 2026-09-24 | Ootoshi-Furutone River, Nakagawa River |
| MLIT, <https://www.mlit.go.jp/sogoseisaku/region/infratourism/en/infralist/ehime/index05.html> and <https://www.mlit.go.jp/sogoseisaku/region/infratourism/en/infralist/ehime/index04.html> | 2026-09-24 | the readings Ishite and Kanogawa, from Ishitegawa Dam and Kanogawa Dam |
| Tokyo Metropolitan Government, <https://tokyo-resilience.metro.tokyo.lg.jp/en/news/4279/> | 2026-09-24 | Shakujii River, Zenpukuji River; it issues their flood forecasts with JMA |
| Saitama Prefecture, <https://www.pref.saitama.lg.jp/b1015/123-niikatakawa.html>, <https://www.pref.saitama.lg.jp/documents/4589/nakaaya04.pdf> and <https://saitama-riversupporters.pref.saitama.lg.jp/magazine/picture-book-tokigawa/> | 2026-09-24 | the readings にいがたがわ, もとあらかわ and ときがわ |
| Ozu City, <https://www.city.ozu.ehime.jp/reiki/reiki_honbun/r058RG00000002.html> | 2026-09-24 | the reading すげた |
| Japanese Wikipedia, the articles 途別川, 美生川, 越辺川, 高麗川 and 小畔川 | 2026-09-24 | the readings とべつがわ, びせいがわ, おっぺがわ, こまがわ and こあぜがわ, for which no official source was found |

## JMA's words, arranged by azarashi

- **Municipalities** (`local_government`): the municipality's name in the dictionary, then its
  prefecture's, as in Sapporo City, Hokkaido Prefecture. Where the dictionary tells apart
  municipalities of the same name by a region, the region is kept before the prefecture, as in
  Date City, Iburi, Hokkaido Prefecture. Where it tells them apart by the prefecture, the
  prefecture's full name takes its place, as in Chiyoda City, Tokyo Metropolis.
- **Flood forecast regions** (`flood_forecast_region`): the dictionary names a region by its river
  system, where the DCR adds the prefectural region in brackets. A comma sets a river system apart
  from its river, where the dictionary uses spaces.
- **Notifications** (`notification_on_disaster_prevention`) 107, 109, 121 to 124, 131, 132 and
  141 are put together from the dictionary's sentences; 111 is the dictionary's English for the
  same sentence with 検潮所で, which its English leaves out.
- **Words taken from a longer entry**: Very Strong and Violent from Very Strong Typhoon (TY) and
  Violent Typhoon (TY); volcanic warning 24 from Volcanic Warning: extreme caution advised at the
  foot of mountains concerned; Preliminary and Detailed from Volcanic Ash Fall Forecast
  (Preliminary) and (Detailed).
- **Kagoshima Prefecture** for weather forecast region 460000, which the dictionary has only as a
  prefecture.

## azarashi's English

91 entries are listed one by one below. Two more families follow a pattern:

- `local_government`: 47 entries, the other municipalities of each prefecture, as Other
  municipalities in Hokkaido Prefecture.
- `flood_forecast_region`: 57 entries, the other rivers of each prefecture or region, as Other
  rivers in Tohoku Region. Chubu Region is azarashi's, since the dictionary names every other
  region but that one.

### epicenter_and_hypocenter

| Code | Japanese | English |
|---|---|---|
| 0 | 未設定(北西太平洋津波情報) | Not set (Northwest Pacific Tsunami Advisory) |
| 999 | 遠地 | Distant |
| 1000 | その他の震央地名 | Other Epicenter |

### tsunami_forecast_region

| Code | Japanese | English |
|---|---|---|
| 1000 | その他の津波予報区 | Other Tsunami Forecast Region |

### volcano_name

| Code | Japanese | English |
|---|---|---|
| 4000 | その他の火山 | Other Volcano |

### weather_forecast_region

| Code | Japanese | English |
|---|---|---|
| 500000 | その他の府県予報区 | Other Prefectural Forecast Region |

### eew_forecast_region

| Code | Japanese | English |
|---|---|---|
| 80 | その他の府県予報区および地方予報区_緊急地震速報(警報) | Other Forecast Region (Earthquake Early Warning) |

### marine_forecast_region

| Code | Japanese | English |
|---|---|---|
| 1000 | 日本海北部及びオホーツク海南部 | Northern Part of Japan Sea and Southern Part of Okhotsk Sea |
| 1100 | 北海道南方及び東方海上 | Sea South and East of Hokkaido |
| 2000 | 三陸沖 | Sea off Sanriku |
| 3100 | 日本海中部 | Central Part of Japan Sea |
| 4100 | 日本海西部 | Western Part of Japan Sea |
| 10000 | その他の地方海上予報区 | Other Marine Forecast Region |

### seismic_intensity

| Code | Japanese | English |
|---|---|---|
| 1 | 4未満 | Less than 4 |
| 2 | 4 | 4 |
| 7 | 7 | 7 |

### seismic_intensity_lower_limit

| Code | Japanese | English |
|---|---|---|
| 1 | 震度0 | Seismic intensity of 0 |
| 2 | 震度1 | Seismic intensity of 1 |
| 3 | 震度2 | Seismic intensity of 2 |
| 14 | なし | None |

### long_period_ground_motion_lower_limit

| Code | Japanese | English |
|---|---|---|
| 1 | 長周期地震動階級1未満 | Less than Long-Period Ground Motion class of 1 |
| 2 | 長周期地震動階級1 | Long-Period Ground Motion class of 1 |
| 3 | 長周期地震動階級2 | Long-Period Ground Motion class of 2 |
| 4 | 長周期地震動階級3 | Long-Period Ground Motion class of 3 |
| 5 | 長周期地震動階級4 | Long-Period Ground Motion class of 4 |

### seismic_intensity_upper_limit

| Code | Japanese | English |
|---|---|---|
| 1 | 震度0 | Seismic intensity of 0 |
| 2 | 震度1 | Seismic intensity of 1 |
| 3 | 震度2 | Seismic intensity of 2 |
| 14 | なし | None |
| 11 | 〜程度以上 | or greater |

### long_period_ground_motion_upper_limit

| Code | Japanese | English |
|---|---|---|
| 1 | 長周期地震動階級1未満 | Less than Long-Period Ground Motion class of 1 |
| 2 | 長周期地震動階級1 | Long-Period Ground Motion class of 1 |
| 3 | 長周期地震動階級2 | Long-Period Ground Motion class of 2 |
| 4 | 長周期地震動階級3 | Long-Period Ground Motion class of 3 |
| 5 | 長周期地震動階級4 | Long-Period Ground Motion class of 4 |
| 6 | 〜程度以上 | or greater |

### tsunami_height

| Code | Japanese | English |
|---|---|---|
| 13 | 該当情報なし | No information |
| 15 | その他の津波の高さ | Other Tsunami Height |

### tsunami_warning_code

| Code | Japanese | English |
|---|---|---|
| 1 | 津波なし | No Tsunami |
| 2 | 警報解除 | Warning Lifted |
| 5 | 大津波警報：発表 | Major Tsunami Warning: Issued |
| 15 | その他の警報 | Other Warning |

### typhoon_intensity_category

| Code | Japanese | English |
|---|---|---|
| 0 | なし | None |
| 1 | 強い | Strong |
| 15 | その他の強さ階級分類 | Other Intensity Category |

### typhoon_scale_category

| Code | Japanese | English |
|---|---|---|
| 0 | なし | None |
| 15 | その他の大きさ階級分類 | Other Scale Category |

### flood_warning_level

| Code | Japanese | English |
|---|---|---|
| 1 | 警報解除 | Warning Lifted |
| 15 | その他の警戒レベル | Other Warning Level |

### marine_warning_code

| Code | Japanese | English |
|---|---|---|
| 0 | 海上警報解除 | Marine Warning Lifted |
| 10 | 海上着氷警報 | Marine Ice Accretion Warning |
| 11 | 海上濃霧警報 | Marine Dense Fog Warning |
| 12 | 海上うねり警報 | Marine Swell Warning |
| 20 | 海上風警報 | Marine Wind Warning |
| 21 | 海上強風警報 | Marine Gale Warning |
| 22 | 海上暴風警報 | Marine Storm Warning |
| 23 | 海上台風警報 | Marine Typhoon Warning |
| 31 | その他の警報等情報要素_海上警報 | Other Marine Warning |

### volcanic_warning_code

| Code | Japanese | English |
|---|---|---|
| 127 | その他の防災気象情報要素 | Other Volcanic Warning |

### weather_related_disaster_sub_category

| Code | Japanese | English |
|---|---|---|
| 7 | 全ての気象特別警報 | All Weather Emergency Warnings |
| 31 | その他の警報等情報要素 | Other Warning |

### ash_fall_warning_code

| Code | Japanese | English |
|---|---|---|
| 7 | その他の防災気象情報要素2 | Other Ash Fall Warning |

### notification_on_disaster_prevention

| Code | Japanese | English |
|---|---|---|
| 0 | なし | None |
| 101 | 今後若干の海面変動があるかもしれません。 | There may be slight sea-level changes from now on. (Translated by azarashi) |
| 102 | 今後若干の海面変動があるかもしれませんが、被害の心配はありません。 | There may be slight sea-level changes from now on, but no damage is expected. (Translated by azarashi) |
| 110 | 津波と満潮が重なると、津波はより高くなりますので十分な注意が必要です。 | Pay full attention if a tsunami arrives at high tide, as this boosts the height of waves. (Translated by azarashi) |
| 112 | 今後、津波の高さは更に高くなることも考えられます。 | Tsunami heights may become even higher from now on. (Translated by azarashi) |
| 113 | 沖合での観測値をもとに津波が推定されている沿岸では、早いところでは、既に津波が到達していると推定されます。 | Along the coasts where the tsunami is estimated from offshore observations, it is estimated to have already arrived at the earliest places. (Translated by azarashi) |
| 114 | 津波による潮位変化が観測されてから最大波が観測されるまでに数時間以上かかることがあります。 | The maximum wave may be observed a few hours or more after a tsunami-driven change in sea level is first observed. (Translated by azarashi) |
| 115 | 沖合での観測値であり、沿岸では津波はさらに高くなります。 | These values were observed offshore. The tsunami will be higher on the coast. (Translated by azarashi) |
| 216 | 震源が海底の場合、津波が発生するおそれがあります。 | If the hypocenter is beneath the sea floor, a tsunami may be generated. (Translated by azarashi) |
| 500 | その他の防災上の留意事項 | Other Notes on Disaster Prevention |

### flood_forecast_region

The dictionary does not have these 19 regions. Their English is written the way the dictionary writes the
others: X River, X River System, The upper, middle or lower Reaches of X River, a hyphen between rivers, and
(Section A to B) for a section. The last column says where each river's name or reading comes from.

| Code | Japanese | English | Name or reading from |
|---|---|---|---|
| 810103003101 | 石狩川水系豊平川上流(北海道道央) | Ishikari River System, The upper Reaches of Toyohira River | JMA dictionary |
| 810108010400 | 途別川(北海道道東) | Tobetsu River | Japanese Wikipedia (とべつがわ) |
| 810108010401 | 十勝川水系途別川上流(北海道道東) | Tokachi River System, The upper Reaches of Tobetsu River | JMA dictionary; Japanese Wikipedia (とべつがわ) |
| 810108016600 | 十勝川水系美生川(北海道道東) | Tokachi River System, Bisei River | JMA dictionary; Japanese Wikipedia (びせいがわ) |
| 810108017400 | 十勝川水系芽室川(北海道道東) | Tokachi River System, Memuro River | JMA dictionary (Memuro Town) |
| 830303033903 | 中川中流部(埼玉県) | The middle Reaches of Nakagawa River | JMA dictionary; MLIT |
| 830303036900 | 元荒川(埼玉県) | Motoarakawa River | Saitama Prefecture (もとあらかわ) |
| 830303039200 | 新方川(埼玉県) | Niigata River | Saitama Prefecture (にいがたがわ) |
| 830303039800 | 大落古利根川(埼玉県) | Ootoshi-Furutone River | MLIT |
| 830304003200 | 石神井川(東京都) | Shakujii River | Tokyo Metropolitan Government |
| 830304004900 | 善福寺川(東京都) | Zenpukuji River | Tokyo Metropolitan Government |
| 830304006403 | 入間川中流部(埼玉県) | The middle Reaches of Iruma River | JMA dictionary |
| 830304007000 | 越辺川・都幾川・高麗川(埼玉県) | Oppe River-Toki River-Koma River | Japanese Wikipedia (おっぺがわ, こまがわ); Saitama Prefecture (ときがわ) |
| 830304007100 | 入間川・小畔川(埼玉県) | Iruma River-Koaze River | JMA dictionary; Japanese Wikipedia (こあぜがわ) |
| 840403000104 | 信濃川水系千曲川下流(長野県) | Shinano River System, The lower Reaches of Chikuma River | JMA dictionary |
| 840403000105 | 信濃川上流(新潟県) | The upper Reaches of Shinano River | JMA dictionary |
| 880801000200 | 石手川(愛媛県) | Ishite River | MLIT (Ishitegawa Dam) |
| 880802000103 | 肱川水系肱川(菅田〜鹿野川)(愛媛県) | Hiji River System, Hiji River (Section Sugeta to Kanogawa) | JMA dictionary; Ozu City (すげた); MLIT (Kanogawa Dam) |
| 890907000103 | 矢部川中流部(福岡県) | The middle Reaches of Yabe River | JMA dictionary |

### Numbers

The numeric tables are written as the Japanese ones are, with a space before the unit, as JMA's
dictionary writes Over 10 m. Unknown is the dictionary's word for 不明.

| Table | English |
|---|---|
| `depth_of_hypocenter` | 10 km; Deeper than 500 km; Unknown |
| `eew_magnitude`, `hypocenter_magnitude` | 7.2; Over 10.0; Unknown (Over 8.0); Unknown |
| `typhoon_central_pressure` | 1010 hPa |
| `typhoon_maximum_wind_speed`, `typhoon_maximum_gust_wind_speed` | 15 m/s; Unknown |
| `typhoon_elapsed_time_from_reference_time` | 1 hour ahead, 3 hours ahead, as the dictionary's Forecast for X hours ahead |
| `typhoon_number` | No. 1 |
| `expected_ash_fall_time` | 1 hour, 3 hours |

## No English

- `information_serial_code` and the text of the Nankai Trough information: see The Nankai Trough
  Information above.

## Open questions

- **Space before a unit.** The Japanese writes 10km and 1010hPa; the English writes 10 km and
  1010 hPa, as the dictionary writes Over 10 m. Whether the English should follow the Japanese is
  to be decided.
- **Marine warnings.** JMA may use fixed English names for its marine warnings, such as Gale
  Warning. azarashi's Marine Gale Warning and the rest are not checked against them.
- **A slip in the dictionary.** The dictionary calls 美咲町 Misaki Ward; it is a town. azarashi
  keeps the dictionary's English.
- **Words that differ by section.** JMA translates 解除 as Lifted for tsunamis and volcanoes and
  as Cancel for weather warnings, and 発表 as Issue or Announcement. Each table keeps the word
  its own section uses.

## Changing the English

Each table's English is in its module, next to the Japanese, and the module's docstring says
where it comes from. `tests/definition_values.json` pins every table, so a change shows in the
tests; update the pinned value with the change. After a change, regenerate the JSON examples with
`PYTHONPATH=.:tests python -m examples.generate`.
