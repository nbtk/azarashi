"""Notifications on disaster prevention, IS-QZSS-DCR-017 Table 4.1.2-6.

The English is JMA's, from its multilingual dictionary of weather information terms
(気象情報等に関する多言語辞書, updated 2026-03-26), where the Japanese is the same. Where the dictionary has the
notification's sentences, not the notification as a whole, the English is put together from them:
107, 109, 121 to 124, 131, 132 and 141. 111 is the dictionary's English for the same sentence with
検潮所で, which its English leaves out.

JMA gives no English for 0, 101, 102, 110, 112 to 115, 216 and 500. So that a warning still reaches
a reader of English, the English for them is azarashi's own until JMA gives its own. It is made of
JMA's wording where JMA has one, and it says no less than the Japanese does. The Japanese is the
notification.
"""
from ...code_table import CodeTable

notification_on_disaster_prevention = CodeTable(
    {
        0: "なし",
        101: "今後若干の海面変動があるかもしれません。",
        102: "今後若干の海面変動があるかもしれませんが、被害の心配はありません。",
        103: "今後もしばらく海面変動が続くと思われます。",
        104: "今後もしばらく海面変動が続くと思われますので、海水浴や磯釣り等を行う際は注意してください。",
        105: "今後もしばらく海面変動が続くと思われますので、磯釣り等を行う際は注意してください。",
        107: "現在、大津波警報・津波警報・津波注意報を発表している沿岸はありません。",
        109: "津波と満潮が重なると、津波はより高くなりますので一層厳重な警戒が必要です。",
        110: "津波と満潮が重なると、津波はより高くなりますので十分な注意が必要です。",
        111: "場所によっては、観測した津波の高さよりさらに大きな津波が到達しているおそれがあります。",
        112: "今後、津波の高さは更に高くなることも考えられます。",
        113: "沖合での観測値をもとに津波が推定されている沿岸では、早いところでは、既に津波が到達していると推定されます。",
        114: "津波による潮位変化が観測されてから最大波が観測されるまでに数時間以上かかることがあります。",
        115: "沖合での観測値であり、沿岸では津波はさらに高くなります。",
        121: "＜大津波警報＞\n" + \
             "大きな津波が襲い甚大な被害が発生します。\n" + \
             "沿岸部や川沿いにいる人はただちに高台や避難ビルなど安全な場所へ避難してください。\n" + \
             "津波は繰り返し襲ってきます。警報が解除されるまで安全な場所から離れないでください。",
        122: "＜津波警報＞\n" + \
             "津波による被害が発生します。\n" + \
             "沿岸部や川沿いにいる人はただちに高台や避難ビルなど安全な場所へ避難してください。\n" + \
             "津波は繰り返し襲ってきます。警報が解除されるまで安全な場所から離れないでください。",
        123: "＜津波注意報＞\n" + \
             "海の中や海岸付近は危険です。\n" + \
             "海の中にいる人はただちに海から上がって、海岸から離れてください。\n" + \
             "潮の流れが速い状態が続きますので、注意報が解除されるまで海に入ったり海岸に近づいたりしないようにしてください。",
        124: "＜津波予報(若干の海面変動)＞\n" + \
             "若干の海面変動が予想されますが、被害の心配はありません。",
        131: "警報が発表された沿岸部や川沿いにいる人はただちに高台や避難ビルなど安全な場所へ避難してください。\n" + \
             "到達予想時刻は、予報区のなかで最も早く津波が到達する時刻です。場所によっては、この時刻よりもかなり遅れて津波が襲ってくることがあります。\n" + \
             "到達予想時刻から津波が最も高くなるまでに数時間以上かかることがありますので、観測された津波の高さにかかわらず、警報が解除されるまで安全な場所から離れないでください。",
        132: "場所によっては津波の高さが「予想される津波の高さ」より高くなる可能性があります。",
        141: "東日本大震災クラスの津波が来襲します。",
        142: "沖合で高い津波を観測したため大津波警報・津波警報に切り替えました。",
        143: "沖合で高い津波を観測したため大津波警報・津波警報を切り替えました。",
        144: "沖合で高い津波を観測したため大津波警報に切り替えました。",
        145: "沖合で高い津波を観測したため大津波警報を切り替えました。",
        146: "沖合で高い津波を観測したため津波警報に切り替えました。",
        147: "沖合で高い津波を観測したため津波警報を切り替えました。",
        148: "沖合で高い津波を観測したため予想される津波の高さを切り替えました。",
        149: "ただちに避難してください。",
        150: "南海トラフ地震臨時情報を発表しています。",
        201: "強い揺れに警戒してください。",
        211: "津波警報等(大津波警報・津波警報あるいは津波注意報)を発表中です。",
        212: "この地震により、日本の沿岸では若干の海面変動があるかもしれませんが、被害の心配はありません。",
        213: "今後もしばらく海面変動が続くと思われますので、海水浴や磯釣り等を行う際は注意してください。",
        214: "今後もしばらく海面変動が続くと思われますので、磯釣り等を行う際は注意してください。",
        215: "この地震による津波の心配はありません。",
        216: "震源が海底の場合、津波が発生するおそれがあります。",
        217: "今後の情報に注意してください。",
        221: "太平洋の広域に津波発生の可能性があります。",
        222: "太平洋で津波発生の可能性があります。",
        223: "北西太平洋で津波発生の可能性があります。",
        224: "インド洋の広域に津波発生の可能性があります。",
        225: "インド洋で津波発生の可能性があります。",
        226: "震源の近傍で津波発生の可能性があります。",
        227: "震源の近傍で小さな津波発生の可能性がありますが、被害をもたらす津波の心配はありません。",
        228: "一般的に、この規模の地震が海域の浅い領域で発生すると、津波が発生することがあります。",
        229: "日本への津波の有無については現在調査中です。",
        230: "この地震による日本への津波の影響はありません。",
        241: "この地震について、緊急地震速報を発表しています。",
        242: "この地震について、緊急地震速報を発表しています。この地震の最大震度は2でした。",
        243: "この地震について、緊急地震速報を発表しています。この地震の最大震度は1でした。",
        244: "この地震について、緊急地震速報を発表しています。この地震で震度1以上は観測されていません。",
        245: "この地震で緊急地震速報を発表しましたが、強い揺れは観測されませんでした。",
        256: "震源要素を訂正します。",
        500: "その他の防災上の留意事項",
        # "NNN*": "防災上の留意事項(コード番号：NNN)",
    },
    undefined="防災上の留意事項(コード番号：%d)"
)


notification_on_disaster_prevention_en = CodeTable(
    {
        0: "None",
        101: "There may be slight sea-level changes from now on.",
        102: "There may be slight sea-level changes from now on, but no damage is expected.",
        103: "Sea-level changes may be observed.",
        104: "Pay attention when fishing, swimming or engaging in other marine activities, as there may still be slight sea-level changes.",
        105: "Pay attention when fishing or engaging in other marine activities, as there may still be slight sea-level changes.",
        107: "No Major Tsunami Warnings, Tsunami Warnings or Advisories are currently in effect.",
        109: "Exercise extreme caution if a tsunami arrives at high tide, as this boosts the height of waves.",
        110: "Pay full attention if a tsunami arrives at high tide, as this boosts the height of waves.",
        111: "In some coastal regions, tsunami waves higher than those recorded may have arrived.",
        112: "Tsunami heights may become even higher from now on.",
        113: "Along the coasts where the tsunami is estimated from offshore observations, it is estimated to have already arrived at the earliest places.",
        114: "The maximum wave may be observed a few hours or more after a tsunami-driven change in sea level is first observed.",
        115: "These values were observed offshore. The tsunami will be higher on the coast.",
        121: "<Major Tsunami Warning>\nA huge tsunami is expected to hit and cause serious damage.\nEvacuate immediately from coastal regions and riverside areas to a safer place such as high ground or an evacuation building.\nTsunami waves are expected to hit repeatedly. Do not leave safe ground until the warning is lifted.",
        122: "<Tsunami Warning>\nDamage due to tsunami waves is expected.\nEvacuate immediately from coastal regions and riverside areas to a safer place such as high ground or an evacuation building.\nTsunami waves are expected to hit repeatedly. Do not leave safe ground until the warning is lifted.",
        123: "<Tsunami Advisory>\nA marine threat is present.\nGet out of the water and leave coastal regions immediately.\nDue to the risk of ongoing strong currents, do not enter the sea or approach coastal regions until the advisory is lifted.",
        124: "<Tsunami Forecast (Slight sea-level change)>\nSlight sea-level changes may be observed in coastal regions, but no tsunami damage is expected.",
        131: "Evacuate immediately from coastal regions and riverside areas where the warning is issued to a safer place such as high ground or an evacuation building.\nEstimated tsunami arrival times show the earliest expected strikes for each tsunami forecast region. In some coastal regions, tsunami waves may hit after this time.\nAs tsunami waves may reach their maximum height a few hours or more after the estimated arrival time, do not leave safe ground until the warning is lifted regardless of recorded tsunami heights.",
        132: "Actual tsunami heights may exceed estimations in some coastal regions.",
        141: "A gigantic tsunami is expected to hit.",
        142: "Upgrade to Major Tsunami Warnings/Tsunami Warnings implemented in response to high tsunami waves observed offshore",
        143: "Major Tsunami Warnings/Tsunami Warnings updated, in response to high tsunami waves offshore",
        144: "Upgrade to Major Tsunami Warnings implemented in response to high tsunami waves observed offshore",
        145: "Major Tsunami Warnings updated, in response to high tsunami waves offshore",
        146: "Upgrade to Tsunami Warnings implemented high tsunami waves observed offshore",
        147: "Tsunami Warnings updated, in response to high tsunami waves offshore",
        148: "Estimated tsunami heights updated in response to high tsunami waves offshore",
        149: "Evacuate immediately",
        150: "Nankai Trough Earthquake Extra Information is in effect.",
        201: "Watch out for strong tremors.",
        211: "Tsunami warnings or advisories are currently in effect.",
        212: "Although there may be slight sea-level changes in coastal regions/ this earthquake has caused no damage to Japan.",
        213: "Pay attention when fishing, swimming or engaging in other marine activities, as there may still be slight sea-level changes.",
        214: "Pay attention when fishing or engaging in other marine activities, as there may still be slight sea-level changes.",
        215: "This earthquake poses no tsunami risk.",
        216: "If the hypocenter is beneath the sea floor, a tsunami may be generated.",
        217: "Check the information which will be issued from now on.",
        221: "There is a possiblity of a destructive ocean-wide tsunami in the Pacific Ocean.",
        222: "There is a possiblity of a destructive regional tsunami in the Pacific Ocean.",
        223: "There is a possiblity of a destructive regional tsunami in the Northwest Pacific Ocean.",
        224: "There is a possiblity of a destructive ocean-wide tsunami in the Indian Ocean.",
        225: "There is a possiblity of a destructive regional tsunami in the Indian Ocean.",
        226: "There is a possibility of a destructive local tsunami near the epicenter.",
        227: "Minor local tsunami may occur near the epicenter, but no tsunami damage is expected.",
        228: "A shallow earthquake with the same magnitude in a sea area may generate a tsunami.",
        229: "The possibility of tsunami generation toward Japan in currently under evaluation.",
        230: "This earthquake poses no tsunami risk to Japan.",
        241: "Earthquake Early Warning is in effect for this earthquake.",
        242: "Earthquake Early Warning is in effect for this earthquake. Its maximum seismic intensity was 2.",
        243: "Earthquake Early Warning is in effect for this earthquake. Its maximum seismic intensity was 1.",
        244: "Earthquake Early Warning is in effect for this earthquake. There was no observation of seismic intensity 1 or above.",
        245: "Earthquake Early Warning was issued for this earthquake, however no strong tremors were observed.",
        256: "Information related to the hypocenter has been corrected.",
        500: "Other Notes on Disaster Prevention",
    },
    undefined="Undefined Notification on Disaster Prevention (Code: %d)"
)
