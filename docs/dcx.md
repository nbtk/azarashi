[azarashi](../README.md) / DCX

# DCX
azarashi は DCX メッセージのデコードをサポートしています。DCX は災危通報の拡張メッセージで、L-Alert や J-Alert などを伝えます。下記は L-Alert をデコードする例です。
```python
>>> import azarashi
>>> msg = '$QZQSM,55,53B0604DE19524CDA305B2C1E355B57800000CCC000000000000001022A8188*7E' # l-alert
>>> report = azarashi.decode(msg, 'nmea')
>>> print(report)
```
```
### DCX Message - L-Alert ###
A1 - Message type: Alert
A2 - Country/region name: Japan
A3 - Provider identifier: Foundation for MultiMedia Communications
A4 - Hazard category and type: MET - Rainfall
A4 - Hazard definition: Rainfall greater than or equal to 50 mm in past 24 hours. Note: Precise threshold is according to each local standard.
A5 - Severity: Severe - Significant threat to life or property
A6A7 - Hazard onset: 2024-06-23T13:00:00Z
A8 - Hazard duration: 6H <= Duration < 12H
A11 - Instruction: Keep away from Water area.
A11 - Instruction (ja): 離れろ。水場。
A12 - Ellipse centre latitude: 35.688258
A13 - Ellipse centre longitude: 139.690855
A14 - Ellipse semi - major axis: 10.933
A15 - Ellipse semi - minor axis: 5.979
A16 - Ellipse azimuth: 45.0
A17 - Type of specific settings: B1 - Improved Resolution of Main Ellipse
C1 - Refined latitude of centre of main ellipse: 35.688258
C2 - Refined longitude of centre of main ellipse: 139.690855
C3 - Refined length of semi major axis: 10.933
C4 - Refined length of semi minor axis: 5.979
```
レポートオブジェクトからパラメータを取得するには `get_params()` メソッドを使います。
```python
>>> from pprint import pprint
>>> pprint(report.get_params(), sort_dicts=False)
```
```python
{'sentence': '$QZQSM,55,53B0604DE19524CDA305B2C1E355B57800000CCC000000000000001022A8188*7E',
 'raw': b'M\xe1\x95$\xcd\xa3\x05\xb2\xc1\xe3U\xb5x\x00\x00\x0c\xcc\x00\x00\x00'
        b'\x00\x00\x00\x00\x10',
 'timestamp': datetime.datetime(2024, 6, 21, 6, 9, 5, 433111, tzinfo=datetime.timezone.utc),
 'message': b'S\xb0`M\xe1\x95$\xcd\xa3\x05\xb2\xc1\xe3U\xb5x\x00\x00\x0c\xcc'
            b'\x00\x00\x00\x00\x00\x00\x00\x10"\xa8\x18\x80',
 'nmea': '$QZQSM,55,53B0604DE19524CDA305B2C1E355B57800000CCC000000000000001022A8188*7E',
 'message_header': '$QZQSM',
 'satellite_id': 55,
 'satellite_prn': 183,
 'satellite_svid': None,
 'preamble': 'A',
 'message_type': 'DCX',
 'camf': <azarashi.qzss_dcr_lib.report.qzss_dc_report.QzssDcxCamf object at 0x10aeb3d10>,
 'ignore_a12_to_a16': False,
 'ignore_a17_to_a18': False,
 'ignore_ex1': True,
 'ignore_ex2_to_ex7': True,
 'ignore_ex8_to_ex9': True,
 'satellite_designation_mask_type': 'MT44 is for Japan or for use outside '
                                    'Japan',
 'satellite_designation_mask': ['For Japan',
                                'For Japan',
                                'For use outside Japan',
                                'For use outside Japan',
                                'For Japan',
                                'For Japan',
                                'For Japan',
                                'For Japan',
                                'For Japan'],
 'dcx_message_type': 'L-Alert',
 'a1_message_type': 'Alert',
 'a2_country_region_name': 'Japan',
 'a3_provider_identifier': 'Foundation for MultiMedia Communications',
 'a4_hazard_category': 'MET',
 'a4_hazard_type': 'Rainfall',
 'a4_hazard_definition': 'Rainfall greater than or equal to 50 mm in past 24 '
                         'hours. Note: Precise threshold is according to each '
                         'local standard.',
 'a5_severity': 'Severe - Significant threat to life or property',
 'a6_hazard_onset_week': 'Current',
 'a7_hazard_onset_time_of_week': 'SUNDAY - 01:00 PM',
 'a6a7_hazard_onset_datetime': datetime.datetime(2024, 6, 23, 13, 0, tzinfo=datetime.timezone.utc),
 'a8_hazard_duration': '6H <= Duration < 12H',
 'a9_type_of_library': 'Country/region library',
 'a10_library_version': '#1',
 'a11_japanese_library': 'Keep away from Water area.',
 'a11_japanese_library_ja': '離れろ。水場。',
 'a12_ellipse_centre_latitude': 35.688258,
 'a13_ellipse_centre_longitude': 139.690855,
 'a14_ellipse_semi_major_axis': 10.933,
 'a15_ellipse_semi_minor_axis': 5.979,
 'a16_ellipse_azimuth': 45.0,
 'a17_type_of_specific_settings': 'B1 - Improved Resolution of Main Ellipse',
 'c1_refined_latitude_of_centre_of_main_ellipse': 35.688258,
 'c2_refined_longitude_of_centre_of_main_ellipse': 139.690855,
 'c3_refined_length_of_semi_major_axis': 10.933,
 'c4_refined_length_of_semi_minor_axis': 5.979,
 'dcx_version': 1}
```
デコードする前のビットフィールドの値は、`report.camf` に入っています。
```python
print(report.camf.get_params())
```
```python
{'sdmt': 0, 'sdm': 96, 'a1': 1, 'a2': 111, 'a3': 1, 'a4': 74, 'a5': 2, 'a6': 0, 'a7': 9421, 'a8': 2, 'a9': 1, 'a10': 0, 'a11': 773, 'a12': 45761, 'a13': 116395, 'a14': 13, 'a15': 11, 'a16': 48, 'a17': 0, 'a18': 0, 'ex1': 13104, 'ex2': 0, 'ex3': 0, 'ex4': 0, 'ex5': 0, 'ex6': 0, 'ex7': 0, 'ex8': 0, 'ex9': 7376896189632872448, 'ex10': 0, 'vn': 1, 'c1': 0, 'c2': 0, 'c3': 0, 'c4': 0}
```
## DCX Message Types
DCX メッセージのデコード結果が格納されるレポートオブジェクトは下記のとおりです。フィールドの一覧は [Reports](reports.md#dcx) にあります。
### Null Message
CAMF フィールドを使わないメッセージです。SD フィールドを監視するために使用します。不要なら無視してください。
```python
class QzssDcxNullMsg(QzssDcXtendedMessageBase)
```
### Information from Organizations outside Japan
日本国外の機関から発報されたメッセージです。
```python
class QzssDcxOutsideJapan(QzssDcXtendedMessageBase)
```
### L-Alert
```python
class QzssDcxLAlert(QzssDcXtendedMessageBase)
```
### J-Alert
```python
class QzssDcxJAlert(QzssDcXtendedMessageBase)
```
### Information from Local Government
```python
class QzssDcxMTInfo(QzssDcXtendedMessageBase)
```
### Unknown Message
日本から発報されたメッセージのうち、発信機関が L-Alert、J-Alert、自治体のどれでもないものです。azarashi は正確にデコードできない可能性が高いので、デバッグのとき以外は無視してください。
```python
class QzssDcxUnknown(QzssDcXtendedMessageBase)
```
