import os
from pprint import pprint

import pytest

import azarashi


def test_scenario1():
    # 緊急地震速報
    report = azarashi.decode('$QZQSM,58,9AAF899C80000324000039000548C5E2C000000003DFF8001C000012FE4B0FC*7F')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaEarthquakeEarlyWarning
    # 震度
    report = azarashi.decode('$QZQSM,58,C6AF999C828001C82CB25AE775A8D4CA854AB8000000000000000011E027E5C*76')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaSeismicIntensity
    # 震源
    report = azarashi.decode('$QZQSM,58,9AAF919C82800388000039051440C5C82A0108300000000000000012497DA18*0A')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaHypocenter
    # 津波
    report = azarashi.decode('$QZQSM,58,9AAFA99C828001E8F67C31053960414E621053BE00000000000000132735038*0F')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaTsunami


def test_scenario2():
    # 津波(更新)
    report = azarashi.decode('$QZQSM,58,9AAFA99C8C8001E8F67C31193960464E621193BBC464EF80000000109DB7028*09')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaTsunami


def test_scenario3():
    # 南海トラフ地震
    report = azarashi.decode('$QZQSM,58,C6AFA19C918002F2C6CBF35ADBF1C1C471C1D4F1C1CAF3595F82D81262EF438*02')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,9AAFA19C918002F1C0D471C0D1F1C0D371C0C7F1C0D071C0CAB4D812D45BCD0*06')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,9AAFA19C918002F1C0CFF4CC5973C0DEF2D7DF72DFCE71C14932D813A64867C*0C')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,53AFA19C918002F1C0C5F1C0C8F3D6C4F1C0D5F2DFCE71C0CC30D81029188EC*0F')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,C6AFA19C918002F1C0D4F1C0C5F1C144F1C0D772C8DE71C0D9AED8108F361A8*7A')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,9AAFA19C918002F2DD4E71C1427443D573595DF25EC9F1C0D52CD81113EFC54*00')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,9AAFA19C918002F1C0CCF1C041725DC572DF4671C0D7734A5FAAD811D504B9C*09')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,53AFA19C918002F1C0D4744041F1C0C471C144F1C14671C0DF28D8127EDCCCC*02')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,C6AFA19C918002F4D5CC71C0DF71C0D1F1C0D371C0C271C145A6D812E9F0C70*03')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,9AAFA19C918002F1C0DCF1C0D373CDDC72D7DF73CD4271C0D5A4D813579A170*78')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,9AAFA19C918002F1C0C672DCD9F2DC5C734CC171C0D5F357CA22D8100D3A898*07')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,53AFA19C918002F1C0D773CCDD73CA4FF2C7D7F441DEF34053A0D8108524298*01')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,C6AFA19C918002F1C040F2D253F45347F35450F2CE5874CE439ED8113990640*7D')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,9AAFA19C918002F2D74D74CE43F35D4872CFCFF1C0D3F1C0D79CD8118D63AC8*07')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,9AAFA19C918002F1C1D4F1C1CAF2CE5874CE43F1C0D77341D99AD81268C2E7C*73')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,53AFA19C918002F1C14471C14571C040F2C6CBF35ADBF1C1C418D812DC94FA0*7F')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,C6AFA19C918002F1C0DCF1C14571C0D773CCDD73CA4FF1C0D596D81357F75D0*74')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,9AAFA19C918002F1C145F1C14371C0D1F1C0C7F1C14571C0CC94D813ED6741C*0C')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,9AAFA19C918002F4C04D72DC5C71C0D471C0D7F3CAD871C0D512D810ADB00F0*78')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,53AFA19C918002F1C14671C0DF71C0CCF1C04171C0C9F1C0D710D8112F31B60*73')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,C6AFA19C918002F1C0C9F1C0D471C0C673475472D74D71C0CA8ED8118DCA59C*7E')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,9AAFA19C918002F3CCDD73CA4FF1C0CBF1C0D371C0C271C1458CD81215E2B50*08')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,9AAFA19C918002F1C0C7F1C14571C0CCF1C0DCF1C14571C0C60AD812CB85F9C*06')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,53AFA19C918002F1C0D7F3CAD871C0D571C145F1C14371C0D188D81363A8A1C*7E')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,C6AFA19C918002F2D141F3CAC671C0D3F4C04D72DC5C71C0D406D813ECF2998*05')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    report = azarashi.decode('$QZQSM,58,9AAFA19C918002F1C0C271C0D771C1CBF1C1D671C1DE71C1C404D8104D300D8*7F')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    assert report.completed is False
    report = azarashi.decode('$QZQSM,58,9AAFA19C918002F1C0C271C04100000000000000000000000036D81121AA2D0*07')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNankaiTroughEarthquake
    assert report.completed is True


def test_scenario4():
    # 火山
    report = azarashi.decode('$QZQSM,58,C6AFC19CA50001CA5341F783E0F10910421230200000000000000011B086438*70')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaVolcano
    # 降灰(速報)
    report = azarashi.decode('$QZQSM,58,9AAFC99CA50001CA523EE4C1F07826122081309181000000000000121BAF1C0*71')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaAshFall


def test_scenario5():
    # 降灰(詳細)
    report = azarashi.decode('$QZQSM,58,C6AFC99CAA0001CAA43EE541F0782A1220813091811183E0F000001329B16E0*7F')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaAshFall
    report = azarashi.decode('$QZQSM,58,C6AFC99CAA0001CAA43EE8C2441046123023307C1E19848820000013E2F3E6C*00')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaAshFall
    report = azarashi.decode('$QZQSM,58,9AAFC99CAA0001CAA43EECC24604860F83C430910421848C080000106286874*00')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaAshFall
    report = azarashi.decode('$QZQSM,58,53AFC99CAA0001CAA43EF4C1F078A61220853091813183E0F0000010CE8C39C*77')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaAshFall
    report = azarashi.decode('$QZQSM,58,C6AFC99CAA0001CAA43EF8C24410C61230200000000000000000001148565F4*0A')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaAshFall


def test_scenario6():
    # 気象
    report = azarashi.decode('$QZQSM,58,C6AFD19CB18001113880115F901186A011ADB011D4C011FBD00000135EAA3F8*73')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaWeather
    report = azarashi.decode('$QZQSM,58,9AAFD19CB180011222E0B93880B95F90B986A0B9ADB0B9D4C0000013D276B60*0D')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaWeather
    report = azarashi.decode('$QZQSM,58,53AFD19CB18001B9FBD0BA22E00000000000000000000000000000107AA71EC*76')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaWeather
    # 洪水
    report = azarashi.decode('$QZQSM,58,C6AFD99CB1800160A8F5528600000000000000000000000000000010E502538*0E')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaFlood


def test_scenario7():
    # 洪水(警報解除)
    report = azarashi.decode('$QZQSM,58,C6AFD99CB90000E0A8F5528600000000000000000000000000000013A699D5C*76')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaFlood


def test_hex():
    # Hexadecimal
    azarashi.decode('C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC', 'hex')


def test_ublox():
    # Ublox SFRBX
    report_ublox = azarashi.decode(
            b'\xB5\x62\x02\x13\x2C\x00\x05\x02\x01\x00\x09\x40\x02\x00\xC5\xF1'
            b'\xAD\x9A\x04\x05\x80\x11\x54\x8D\xA0\x60\x3F\x82\xD2\x11\x0F\xAA'
            b'\x7D\x50\x28\x0C\x43\xC9\x10\x00\x50\x7D\x31\x79\xF0\x28\x73\x18'
            b'\x10\xB2\x62\x2F',
            'ublox')
    report_nmea = azarashi.decode(report_ublox.nmea, 'nmea')
    assert report_ublox.nmea == report_nmea.nmea
    assert report_ublox.satellite_id == report_nmea.satellite_id == 56
    assert report_ublox.satellite_prn == report_nmea.satellite_prn == 184

    report_ublox = azarashi.decode(
            b'\xB5\x62\x02\x13\x2C\x00\x05\x02\x01\x00\x09\x40\x02\x00\x76\x14'
            b'\xAD\x53\x5C\x03\x80\x1A\x33\xEC\x00\x00\x49\x48\x2F\x14\x20\x1B'
            b'\x01\x52\x00\x00\x00\x00\x12\x00\x00\x00\xA6\x59\xB0\xC6\x5B\x1F'
            b'\xF3\xB2\x3E\xB6',
            'ublox')
    report_nmea = azarashi.decode(report_ublox.nmea, 'nmea')
    assert report_ublox.nmea == report_nmea.nmea
    assert report_ublox.satellite_id == report_nmea.satellite_id == 56
    assert report_ublox.satellite_prn == report_nmea.satellite_prn == 184

    report_ublox = azarashi.decode(
            b'\xb5\x62\x02\x13\x2c\x00\x05\x03\x01\x00\x09\x41\x02\x00\xa1\xe5'
            b'\xad\xc6\x12\x02\x80\x36\x68\x00\x00\x01\x10\x50\x34\x44\xd4\xee'
            b'\x00\x34\x00\x00\x00\x3c\x11\x00\x00\x00\x14\x9c\x5f\x60\x26\xcb'
            b'\xc0\xf2\xef\x1a',
            'ublox')
    
    report_nmea = azarashi.decode(report_ublox.nmea, 'nmea')
    assert report_ublox.nmea == report_nmea.nmea
    assert report_ublox.satellite_id == report_nmea.satellite_id == 57
    assert report_ublox.satellite_prn == report_nmea.satellite_prn == 185
    
    report_ublox = azarashi.decode(
            b'\xb5\x62\x02\x13\x2c\x00\x05\x07\x01\x00\x09\x45\x02\x00\xa1\xe5'
            b'\xad\xc6\x12\x02\x80\x36\x68\x00\x00\x01\x10\x50\x34\x44\xd4\xee'
            b'\x00\x34\x00\x00\x00\x3c\x11\x00\x00\x00\x14\x9c\x5f\x60\x26\xcb'
            b'\xc0\xf2\xf7\x62',
            'ublox')
    
    report_nmea = azarashi.decode(report_ublox.nmea, 'nmea')
    assert report_ublox.nmea == report_nmea.nmea
    assert report_ublox.satellite_id == report_nmea.satellite_id == 61
    assert report_ublox.satellite_prn == report_nmea.satellite_prn == 189
    
    report_ublox = azarashi.decode( # svid:1 は停波済
            b'\xb5\x62\x02\x13\x2c\x00\x05\x01\x01\x00\x09\x45\x02\x00\xa1\xe5'
            b'\xad\xc6\x12\x02\x80\x36\x68\x00\x00\x01\x10\x50\x34\x44\xd4\xee'
            b'\x00\x34\x00\x00\x00\x3c\x11\x00\x00\x00\x14\x9c\x5f\x60\x26\xcb'
            b'\xc0\xf2\xf1\x60',
            'ublox')
    
    report_nmea = azarashi.decode(report_ublox.nmea, 'nmea')
    assert report_ublox.nmea == report_nmea.nmea
    assert report_ublox.satellite_id == report_nmea.satellite_id == 55
    assert report_ublox.satellite_prn == report_nmea.satellite_prn == 183


def test_northwest_pacific_tsunami():
    # 北西太平洋津波
    report = azarashi.decode('$QZQSM,55,53AD360D5B80047FFFFE3000000000000000000000000000000000118372EC8*0C')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNorthwestPacificTsunami
    report = azarashi.decode('$QZQSM,56,9AAD3609E080023AE008D3D1008E449009D457009E3E5011F00000138B3E720*09')
    assert type(report) == azarashi.qzss_dc_report.QzssDcReportJmaNorthwestPacificTsunami


def test_unknown_magnitude_or_depth():
    # 震源 マグニチュード:不明, 深さ:不明
    report = azarashi.decode('$QZQSM,55,53AD160D2800039400001A28FFFFEE601800C8F00000000000000011BF8D908*01')
    assert report.depth_of_hypocenter == '不明'
    assert report.depth_of_hypocenter_raw == 511
    assert report.magnitude == '不明'
    assert report.magnitude_raw == 127


def test_long_period_ground_motion():
    # 緊急地震速報 長周期地震動
    report = azarashi.decode('$QZQSM,56,9AAF88A48000DB24000049000548C5E2C000000003DFF8001C000012101445C*7B')
    assert report.long_period_ground_motion_lower_limit == '長周期地震動階級2'
    assert report.long_period_ground_motion_lower_limit_raw == 3
    assert report.long_period_ground_motion_upper_limit == '長周期地震動階級2'
    assert report.long_period_ground_motion_upper_limit_raw == 3


def test_from_file():
    dir_path = os.path.dirname(os.path.realpath(__file__))

    def handler(report):
        pprint(report.get_params())

    with open(dir_path + '/qzqsm_220307.log', mode='r') as f:
        while True:
            try:
                azarashi.decode_stream(f, msg_type='nmea', callback=handler)
            except EOFError as e:
                print(f'# [{type(e).__name__}] {e}')
                break


def test_decode_error():
    with pytest.raises(azarashi.QzssDcrDecoderException):
        # crc mismatch
        azarashi.decode('C6AF89A820000324000050400548C5E2C000000003DFF8001C000011854432D', 'hex')

    with pytest.raises(azarashi.QzssDcrDecoderException):
        # checksum mismatch
        azarashi.decode('$QZQSM,55,C6AF89A820000324000050400548C5E2C000000003DFF8001C00001185443FC*00')

    with pytest.raises(azarashi.QzssDcrDecoderException):
        # checksum mismatch
        azarashi.decode(b'\xB5\x62\x02\x13\x2C\x00\x05\x02\x01\x00\x09\x40\x02\x00\xC5\xF1'
                        b'\xAD\x9A\x04\x05\x80\x11\x54\x8D\xA0\x60\x3F\x82\xD2\x11\x0F\xAA'
                        b'\x7D\x50\x28\x0C\x43\xC9\x10\x00\x50\x7D\x31\x79\xF0\x28\x73\x18'
                        b'\x10\xB2\x62\x20',
                        'ublox')


def test_dcx():
    null_msg = azarashi.decode('$QZQSM,55,53B0840DE0000000000000000000000000000000000000000000000012ACBD4*0E')
    assert type(null_msg) is azarashi.qzss_dc_report.QzssDcxNullMsg

    org_outside_jpn = azarashi.decode('$QZQSM,56,9AB08408E0598969E00066AFFE8E6F70091200000000000000000100CD1A410*0C')
    assert type(org_outside_jpn) is azarashi.qzss_dc_report.QzssDcxOutsideJapan

    l_alert = azarashi.decode('$QZQSM,55,9AB0840DE10208ADE0000000000000000000011340000000000000132F0D238*04')
    assert type(l_alert) is azarashi.qzss_dc_report.QzssDcxLAlert

    j_alert = azarashi.decode('$QZQSM,55,53B0840DE31188FC208600000000000000001FFFFFFFFFFFC00000120738628*00')
    assert type(j_alert) is azarashi.qzss_dc_report.QzssDcxJAlert
