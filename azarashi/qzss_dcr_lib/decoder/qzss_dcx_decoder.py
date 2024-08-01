import datetime
import math

from .qzss_dcr_decoder_base import QzssDcrDecoderBase
from ..definition import qzss_dcx_camf_a10_library_version
from ..definition import qzss_dcx_camf_a11_international_library
from ..definition import qzss_dcx_camf_a11_international_library_code
from ..definition import qzss_dcx_camf_a11_japanese_library_en
from ..definition import qzss_dcx_camf_a11_japanese_library_ja
from ..definition import qzss_dcx_camf_a17_main_subject_for_specific_settings
from ..definition import qzss_dcx_camf_a1_message_type
from ..definition import qzss_dcx_camf_a2_country_region_name
from ..definition import qzss_dcx_camf_a3_provider_identifier_map
from ..definition import qzss_dcx_camf_a3_provider_identifier_undefined
from ..definition import qzss_dcx_camf_a4_hazard_category
from ..definition import qzss_dcx_camf_a4_hazard_definition
from ..definition import qzss_dcx_camf_a4_hazard_type
from ..definition import qzss_dcx_camf_a5_severity
from ..definition import qzss_dcx_camf_a6_hazard_onset_week
from ..definition import qzss_dcx_camf_a8_hazard_duration
from ..definition import qzss_dcx_camf_a9_selection_of_library
from ..definition import qzss_dcx_camf_c10_guidance_library_for_second_ellipse
from ..definition import qzss_dcx_camf_c10_guidance_library_for_second_ellipse_code
from ..definition.qzss_dcx_camf_b4_lower_level_fields_tables import *
from ..definition.qzss_dcx_camf_ex1_target_area_code import *
from ..definition.qzss_dcx_camf_ex9_target_area_code import *
from ..definition.qzss_dcx_message_type import *
from ..report import QzssDcReportMessageBase, QzssDcxNullMsg, QzssDcxOutsideJapan, QzssDcxLAlert, QzssDcxJAlert, \
    QzssDcxMTInfo, QzssDcxUnknown


class QzssDcxDecoder(QzssDcrDecoderBase):
    schema = QzssDcReportMessageBase

    def decode(self):
        class CAMF:
            def __str__(self):
                return str(self.get_params())

            def get_params(self):
                return self.__dict__

        self.camf = camf = CAMF()
        camf.sdmt = self.extract_field(14, 1)
        camf.sdm = self.extract_field(15, 9)
        camf.a1 = self.extract_field(24, 2)
        camf.a2 = self.extract_field(26, 9)
        camf.a3 = self.extract_field(35, 5)
        camf.a4 = self.extract_field(40, 7)
        camf.a5 = self.extract_field(47, 2)
        camf.a6 = self.extract_field(49, 1)
        camf.a7 = self.extract_field(50, 14)
        camf.a8 = self.extract_field(64, 2)
        camf.a9 = self.extract_field(66, 1)
        camf.a10 = self.extract_field(67, 3)
        camf.a11 = self.extract_field(70, 10)
        camf.a12 = self.extract_field(80, 16)
        camf.a13 = self.extract_field(96, 17)
        camf.a14 = self.extract_field(113, 5)
        camf.a15 = self.extract_field(118, 5)
        camf.a16 = self.extract_field(123, 6)
        camf.a17 = self.extract_field(129, 2)
        camf.a18 = self.extract_field(131, 15)
        camf.ex1 = self.extract_field(146, 16)
        camf.ex2 = self.extract_field(162, 1)
        camf.ex3 = self.extract_field(163, 17)
        camf.ex4 = self.extract_field(180, 17)
        camf.ex5 = self.extract_field(197, 5)
        camf.ex6 = self.extract_field(202, 5)
        camf.ex7 = self.extract_field(207, 7)
        camf.ex8 = self.extract_field(146, 1)
        camf.ex9 = self.extract_field(147, 64)
        camf.ex10 = self.extract_field(211, 3)
        camf.vn = self.extract_field(214, 6)

        if camf.sdmt == 0:
            self.satellite_designation_mask_type = 'MT44 is for Japan or for use outside Japan'
            sd_list = ['For Japan', 'For use outside Japan']
        else:  # sdmt should be 1.
            self.satellite_designation_mask_type = 'MT44 transmission status'
            sd_list = ['Transmission stopped', 'Transmission in progress']

        self.satellite_designation_mask = []
        for i in range(9):
            self.satellite_designation_mask.append(sd_list[(camf.sdm & 1 << i) >> i])

        if camf.a1 == camf.a3 == camf.a4 == camf.a5 == camf.a6 == camf.a7 == camf.a8 == camf.a9 == camf.a10 == \
                camf.a11 == camf.a12 == camf.a13 == camf.a14 == camf.a15 == camf.a16 == camf.a17 == camf.a18 == \
                camf.ex1 == camf.ex2 == camf.ex3 == camf.ex4 == camf.ex5 == camf.ex6 == camf.ex7 == camf.vn == 0:
            dcx_message_type = DcxMessageType.NULL_MSG
        elif camf.a2 == 111:  # japan
            if camf.a3 == 1:  # fmmc
                dcx_message_type = DcxMessageType.L_ALERT
            elif camf.a3 == 2 or camf.a3 == 3:  # fdma or related ministries
                dcx_message_type = DcxMessageType.J_ALERT
            elif camf.a3 == 4:  # municipality
                dcx_message_type = DcxMessageType.MT_INFO
            else:
                dcx_message_type = DcxMessageType.UNKNOWN
        else:  # outside japan
            dcx_message_type = DcxMessageType.OUTSIDE_JAPAN

        # detecting the message type
        self.dcx_message_type = qzss_dcx_message_type[dcx_message_type]
        # setting flags to ignore fields
        self.ignore_a12_to_a16 = False
        self.ignore_a17_to_a18 = False
        self.ignore_ex1 = False
        self.ignore_ex2_to_ex7 = False
        self.ignore_ex8_to_ex9 = False
        if dcx_message_type == DcxMessageType.OUTSIDE_JAPAN:
            self.ignore_ex1 = True
            self.ignore_ex2_to_ex7 = True
            self.ignore_ex8_to_ex9 = True
        elif dcx_message_type == DcxMessageType.L_ALERT:
            a12_to_a16 = self.extract_field(80, 49)
            if a12_to_a16 == 0:
                self.ignore_a12_to_a16 = True
            else:
                self.ignore_ex1 = True
            self.ignore_ex2_to_ex7 = True
            self.ignore_ex8_to_ex9 = True
        elif dcx_message_type == DcxMessageType.J_ALERT:
            self.ignore_a12_to_a16 = True
            self.ignore_a17_to_a18 = True
            self.ignore_ex1 = True
            self.ignore_ex2_to_ex7 = True
        elif dcx_message_type == DcxMessageType.MT_INFO:
            ex3_to_ex7 = self.extract_field(163, 51)
            if ex3_to_ex7 == 0:
                self.ignore_ex2_to_ex7 = True
            self.ignore_ex8_to_ex9 = True
        elif dcx_message_type == DcxMessageType.NULL_MSG:
            self.ignore_a12_to_a16 = True
            self.ignore_a17_to_a18 = True
            self.ignore_ex1 = True
            self.ignore_ex2_to_ex7 = True
            self.ignore_ex8_to_ex9 = True
            return QzssDcxNullMsg(**self.get_params())
        else:  # has to be an unknown message
            self.ignore_ex1 = True
            self.ignore_ex2_to_ex7 = True
            self.ignore_ex8_to_ex9 = True

        self.a1_message_type = qzss_dcx_camf_a1_message_type[camf.a1]
        self.a2_country_region_name = qzss_dcx_camf_a2_country_region_name[camf.a2]
        self.a3_provider_identifier = (
            qzss_dcx_camf_a3_provider_identifier_map.get(
                camf.a2,
                qzss_dcx_camf_a3_provider_identifier_undefined))[camf.a3]
        self.a4_hazard_category = qzss_dcx_camf_a4_hazard_category[camf.a4]
        self.a4_hazard_type = qzss_dcx_camf_a4_hazard_type[camf.a4]
        self.a4_hazard_definition = qzss_dcx_camf_a4_hazard_definition[camf.a4]
        self.a5_severity = qzss_dcx_camf_a5_severity[camf.a5]
        self.a6_hazard_onset_week = qzss_dcx_camf_a6_hazard_onset_week[camf.a6]
        today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        hazard_onset = today + datetime.timedelta(weeks=camf.a6, days=-today.weekday(), minutes=camf.a7 - 1)
        if 1 <= camf.a7 <= 10080:
            self.a7_hazard_onset_time_of_week = hazard_onset.strftime('%A - %I:%M %p').upper()
            self.a6a7_hazard_onset_datetime = hazard_onset
        else:  # a7 is unexpectedly out of range...
            self.a7_hazard_onset_time_of_week = 'The Time of the Week Value is Unexpectedly Out of Range (Code: %d)' % camf.a7
            self.a6a7_hazard_onset_datetime = None
        self.a8_hazard_duration = qzss_dcx_camf_a8_hazard_duration[camf.a8]
        self.a9_selection_of_library = qzss_dcx_camf_a9_selection_of_library[camf.a9]
        self.a10_library_version = qzss_dcx_camf_a10_library_version[camf.a10]
        if camf.a10 == 0:  # library version #1 is only supported for now.
            if camf.a9 == 0:  # international library
                self.a11_international_library_code = qzss_dcx_camf_a11_international_library_code[camf.a11]
                self.a11_international_library = qzss_dcx_camf_a11_international_library[camf.a11]
            elif camf.a9 == 1:  # country/region guidance library
                if camf.a2 == 111:  # japanese library
                    self.a11_japanese_library = qzss_dcx_camf_a11_japanese_library_en[camf.a11]
                    self.a11_japanese_library_ja = qzss_dcx_camf_a11_japanese_library_ja[camf.a11]

        def __get_axis(factor):
            return pow(10, math.log10(216.2) + factor * (math.log10(2500000) - math.log10(216.2)) / 31) / 1000

        if self.ignore_a12_to_a16 is False:
            self.a12_ellipse_centre_latitude = -90 + 180 / 0xFFFF * camf.a12
            self.a13_ellipse_centre_longitude = -180 + 360 / 0x1FFFF * camf.a13
            self.a14_ellipse_semi_major_axis = __get_axis(camf.a14)
            self.a15_ellipse_semi_minor_axis = __get_axis(camf.a15)
            self.a16_ellipse_azimuth = -90 + 180 / 0x40 * camf.a16
        if self.ignore_a17_to_a18 is False:
            if camf.a17 == 0 and self.ignore_a12_to_a16 is False:  # B1 – improved resolution of main ellipse
                self.a17_main_subject_for_specific_settings = \
                    qzss_dcx_camf_a17_main_subject_for_specific_settings[camf.a17]
                camf.c1 = self.extract_field(131, 3)
                camf.c2 = self.extract_field(134, 3)
                camf.c3 = self.extract_field(137, 3)
                camf.c4 = self.extract_field(140, 3)
                self.c1_refined_latitude_of_centre_of_main_ellipse = (
                        self.a12_ellipse_centre_latitude +
                        (180 / 0xFFFF) / 8 * camf.c1
                )
                self.c2_refined_longitude_of_centre_of_main_ellipse = (
                        self.a13_ellipse_centre_longitude +
                        (180 / 0xFFFF) / 8 * camf.c2
                )
                if camf.a14 == 0:
                    delta = self.a14_ellipse_semi_major_axis
                else:
                    delta = self.a14_ellipse_semi_major_axis - __get_axis(camf.a14 - 1)
                self.c3_refined_length_of_semi_major_axis = (
                        self.a14_ellipse_semi_major_axis -
                        delta * camf.c3 / 8
                )
                if camf.a15 == 0:
                    delta = self.a15_ellipse_semi_minor_axis
                else:
                    delta = self.a15_ellipse_semi_minor_axis - __get_axis(camf.a15 - 1)
                self.c4_refined_length_of_semi_minor_axis = (
                        self.a15_ellipse_semi_minor_axis -
                        delta * camf.c4 / 8
                )
            elif camf.a17 == 1 and self.ignore_a12_to_a16 is False:  # B2 – position of centre of hazard
                self.a17_main_subject_for_specific_settings = \
                    qzss_dcx_camf_a17_main_subject_for_specific_settings[camf.a17]
                camf.c5 = self.extract_field(131, 7)
                camf.c6 = self.extract_field(138, 7)
                if camf.c5 <= 63:
                    delta = -10 + 20 / 0x80 * camf.c5
                else:
                    delta = -10 + 20 / 0x80 * (camf.c5 + 1)
                self.c5_latitude_of_centre_of_hazard = self.a12_ellipse_centre_latitude + delta
                if camf.c6 <= 63:
                    delta = -10 + 20 / 0x80 * camf.c6
                else:
                    delta = -10 + 20 / 0x80 * (camf.c6 + 1)
                self.c6_longitude_of_centre_of_hazard = self.a13_ellipse_centre_longitude + delta
            elif camf.a17 == 2:  # B3 – second ellipse definition
                self.a17_main_subject_for_specific_settings = \
                    qzss_dcx_camf_a17_main_subject_for_specific_settings[camf.a17]
                camf.c7 = self.extract_field(131, 2)
                camf.c8 = self.extract_field(133, 3)
                camf.c9 = self.extract_field(136, 5)
                camf.c10 = self.extract_field(141, 5)
                self.c7_shift_of_second_ellipse_centre = camf.c7
                self.c8_homothetic_factor_of_second_ellipse = 0.25 * (camf.c8 + 1)
                self.c9_bearing_angle_of_second_ellipse = camf.c9 * 360 / 32
                self.c10_guidance_library_for_second_ellipse_code = \
                    qzss_dcx_camf_c10_guidance_library_for_second_ellipse_code[camf.c10]
                self.c10_guidance_library_for_second_ellipse = \
                    qzss_dcx_camf_c10_guidance_library_for_second_ellipse[camf.c10]
            elif camf.a17 == 3:  # B4 – quantitative and detailed information related to hazard category and type
                self.a17_main_subject_for_specific_settings = \
                    qzss_dcx_camf_a17_main_subject_for_specific_settings[camf.a17]
                if camf.a4 == 36:  # earthquake
                    camf.d1 = self.extract_field(131, 4)
                    camf.d2 = self.extract_field(135, 3)
                    camf.d3 = self.extract_field(138, 4)
                    camf.d4 = self.extract_field(142, 4)
                    self.d1_magnitude_on_richter_scale = qzss_dcx_camf_d1_magnitude_on_richter_scale[camf.d1]
                    self.d2_seismic_coefficient = qzss_dcx_camf_d2_seismic_coefficient[camf.d2]
                    self.d3_azimuth_from_centre_of_main_ellipse_to_epicentre = \
                        qzss_dcx_camf_d3_azimuth_from_centre_of_main_ellipse_to_epicentre[camf.d3]
                    self.d4_vector_length_between_centre_of_main_ellipse_and_epicentre = \
                        qzss_dcx_camf_d4_vector_length_between_centre_of_main_ellipse_and_epicentre[camf.d4]
                elif camf.a4 == 44 or camf.a4 == 43:  # tsunami or tidal wave
                    camf.d5 = self.extract_field(131, 3)
                    self.d5_wave_height = qzss_dcx_camf_d5_wave_height[camf.d5]
                elif camf.a4 == 63 or camf.a4 == 71:  # cold wave or heat wave
                    camf.d6 = self.extract_field(131, 4)
                    self.d6_temperature_range = qzss_dcx_camf_d6_temperature_range[camf.d6]
                elif camf.a4 == 80:  # tropical cyclone (hurricane)
                    camf.d7 = self.extract_field(131, 3)
                    camf.d8 = self.extract_field(134, 4)
                    camf.d9 = self.extract_field(138, 3)
                    self.d7_hurricane_category = qzss_dcx_camf_d7_hurricane_category[camf.d7]
                    self.d8_wind_speed = qzss_dcx_camf_d8_wind_speed[camf.d8]
                    self.d9_rainfall_amounts = qzss_dcx_camf_d9_rainfall_amounts[camf.d9]
                elif camf.a4 == 82:  # tropical cyclone (typhoon)
                    camf.d36 = self.extract_field(131, 3)
                    camf.d8 = self.extract_field(134, 4)
                    camf.d9 = self.extract_field(138, 3)
                    self.d36_typhoon_category = qzss_dcx_camf_d36_typhoon_category[camf.d36]
                    self.d8_wind_speed = qzss_dcx_camf_d8_wind_speed[camf.d8]
                    self.d9_rainfall_amounts = qzss_dcx_camf_d9_rainfall_amounts[camf.d9]
                elif camf.a4 == 79:  # tornado
                    camf.d8 = self.extract_field(131, 4)
                    camf.d9 = self.extract_field(135, 3)
                    camf.d11 = self.extract_field(138, 3)
                    self.d8_wind_speed = qzss_dcx_camf_d8_wind_speed[camf.d8]
                    self.d9_rainfall_amounts = qzss_dcx_camf_d9_rainfall_amounts[camf.d9]
                    self.d11_tornado_probability = qzss_dcx_camf_d11_tornado_probability[camf.d11]
                elif camf.a4 == 77:  # storm or thunderstorm
                    camf.d8 = self.extract_field(131, 4)
                    camf.d9 = self.extract_field(135, 3)
                    camf.d10 = self.extract_field(138, 3)
                    camf.d16 = self.extract_field(141, 3)
                    self.d8_wind_speed = qzss_dcx_camf_d8_wind_speed[camf.d8]
                    self.d9_rainfall_amounts = qzss_dcx_camf_d9_rainfall_amounts[camf.d9]
                    self.d10_damage_category = qzss_dcx_camf_d10_damage_category[camf.d10]
                    self.d16_lightning_intensity = qzss_dcx_camf_d16_lightning_intensity[camf.d16]
                elif camf.a4 == 70:  # hail
                    camf.d12 = self.extract_field(131, 4)
                    self.d12_hail_scale = qzss_dcx_camf_d12_hail_scale[camf.d12]
                elif camf.a4 == 74:  # rainfall
                    camf.d9 = self.extract_field(131, 3)
                    camf.d13 = self.extract_field(134, 4)
                    self.d9_rainfall_amounts = qzss_dcx_camf_d9_rainfall_amounts[camf.d9]
                    self.d13_visibility = qzss_dcx_camf_d13_visibility[camf.d13]
                elif camf.a4 == 76:  # snowfall
                    camf.d14 = self.extract_field(131, 5)
                    camf.d13 = self.extract_field(136, 4)
                    self.d14_snow_depth = qzss_dcx_camf_d14_snow_depth[camf.d14]
                    self.d13_visibility = qzss_dcx_camf_d13_visibility[camf.d13]
                elif camf.a4 == 68:  # flood
                    camf.d15 = self.extract_field(131, 2)
                    self.d15_flood_severity = qzss_dcx_camf_d15_flood_severity[camf.d15]
                elif camf.a4 == 72:  # lightning
                    camf.d16 = self.extract_field(131, 3)
                    self.d16_lightning_intensity = qzss_dcx_camf_d16_lightning_intensity[camf.d16]
                elif camf.a4 == 81:  # wind chill / frost
                    camf.d8 = self.extract_field(131, 4)
                    camf.d6 = self.extract_field(135, 4)
                    self.d8_wind_speed = qzss_dcx_camf_d8_wind_speed[camf.d8]
                    self.d6_temperature_range = qzss_dcx_camf_d6_temperature_range[camf.d6]
                elif camf.a4 == 64:  # derecho
                    camf.d8 = self.extract_field(131, 4)
                    camf.d9 = self.extract_field(135, 3)
                    camf.d16 = self.extract_field(138, 3)
                    camf.d11 = self.extract_field(141, 3)
                    self.d8_wind_speed = qzss_dcx_camf_d8_wind_speed[camf.d8]
                    self.d9_rainfall_amounts = qzss_dcx_camf_d9_rainfall_amounts[camf.d9]
                    self.d16_lightning_intensity = qzss_dcx_camf_d16_lightning_intensity[camf.d16]
                    self.d11_tornado_probability = qzss_dcx_camf_d11_tornado_probability[camf.d11]
                elif camf.a4 == 69:  # fog
                    camf.d17 = self.extract_field(131, 3)
                    camf.d13 = self.extract_field(134, 4)
                    self.d17_fog_level = qzss_dcx_camf_d17_fog_level[camf.d17]
                    self.d13_visibility = qzss_dcx_camf_d13_visibility[camf.d13]
                elif camf.a4 == 75:  # snow storm / blizzard
                    camf.d13 = self.extract_field(131, 4)
                    camf.d8 = self.extract_field(134, 4)
                    self.d13_visibility = qzss_dcx_camf_d13_visibility[camf.d13]
                    self.d8_wind_speed = qzss_dcx_camf_d8_wind_speed[camf.d8]
                elif camf.a4 == 65:  # drought
                    camf.d18 = self.extract_field(131, 2)
                    self.d18_drought_level = qzss_dcx_camf_d18_drought_level[camf.d18]
                elif camf.a4 == 33:  # avalanche risk
                    camf.d19 = self.extract_field(131, 3)
                    self.d19_avalanche_warning_level = qzss_dcx_camf_d19_avalanche_warning_level[camf.d19]
                elif camf.a4 == 32:  # ash fall
                    camf.d20 = self.extract_field(131, 3)
                    self.d20_ash_fall_amount_and_impact = qzss_dcx_camf_d20_ash_fall_amount_and_impact[camf.d20]
                elif camf.a4 == 47:  # wind / wave / storm surge
                    camf.d8 = self.extract_field(131, 4)
                    camf.d5 = self.extract_field(135, 3)
                    self.d8_wind_speed = qzss_dcx_camf_d8_wind_speed[camf.d8]
                    self.d5_wave_height = qzss_dcx_camf_d5_wave_height[camf.d5]
                elif camf.a4 == 37:  # geomagnetic or solar storm
                    camf.d21 = self.extract_field(131, 3)
                    self.d21_geomagnetic_scale = qzss_dcx_camf_d21_geomagnetic_scale[camf.d21]
                elif camf.a4 == 103:  # terrorism
                    camf.d22 = self.extract_field(131, 3)
                    self.d22_terrorism_threat_level = qzss_dcx_camf_d22_terrorism_threat_level[camf.d22]
                elif camf.a4 == 27 or camf.a4 == 30:  # forest fire or risk of fire
                    camf.d23 = self.extract_field(131, 3)
                    self.d23_fire_risk_level = qzss_dcx_camf_d23_fire_risk_level[camf.d23]
                elif camf.a4 == 16 or camf.a4 == 18 or camf.a4 == 21:  # contaminated drinking water or marine pollution or river pollution
                    camf.d24 = self.extract_field(131, 3)
                    self.d24_water_quality = qzss_dcx_camf_d24_water_quality[camf.d24]
                elif camf.a4 == 23:  # uv radiation
                    camf.d25 = self.extract_field(131, 3)
                    self.d25_uv_index = qzss_dcx_camf_d25_uv_index[camf.d25]
                elif camf.a4 == 53 or camf.a4 == 51:  # risk of infection or pandemic
                    camf.d26 = self.extract_field(131, 5)
                    camf.d35 = self.extract_field(136, 6)
                    self.d26_number_of_cases_per_100000_inhabitants = \
                        qzss_dcx_camf_d26_number_of_cases_per_100000_inhabitants[camf.d26]
                    self.d35_infection_type = qzss_dcx_camf_d35_infection_type[camf.d35]
                elif camf.a4 == 19:  # noise pollution
                    camf.d27 = self.extract_field(131, 4)
                    self.d27_noise_range = qzss_dcx_camf_d27_noise_range[camf.d27]
                elif camf.a4 == 15:  # air pollution
                    camf.d28 = self.extract_field(131, 3)
                    self.d28_air_quality_index = qzss_dcx_camf_d28_air_quality_index[camf.d28]
                elif camf.a4 == 56 or camf.a4 == 57 or camf.a4 == 58 or camf.a4 == 55 or camf.a4 == 60:  # gas supply outage or outage of it system or power outage or emergency number outage or telephone line outage
                    camf.d29 = self.extract_field(131, 5)
                    self.d29_outage_estimated_duration = qzss_dcx_camf_d29_outage_estimated_duration[camf.d29]
                elif camf.a4 == 5:  # chemical hazard
                    camf.d31 = self.extract_field(131, 4)
                    self.d31_chemical_hazard_type = qzss_dcx_camf_d31_chemical_hazard_type[camf.d31]
                elif camf.a4 == 11 or camf.a4 == 9 or camf.a4 == 10:  # radiological hazard or nuclear hazard or nuclear power station accident
                    camf.d30 = self.extract_field(131, 4)
                    self.d30_nuclear_event_scale = qzss_dcx_camf_d30_nuclear_event_scale[camf.d30]
                elif camf.a4 == 4:  # biological hazard
                    camf.d32 = self.extract_field(131, 2)
                    camf.d33 = self.extract_field(133, 2)
                    self.d32_biohazard_level = qzss_dcx_camf_d32_biohazard_level[camf.d32]
                    self.d33_biohazard_type = qzss_dcx_camf_d33_biohazard_type[camf.d33]
                elif camf.a4 == 6:  # explosive hazard
                    camf.d34 = self.extract_field(131, 2)
                    self.d34_explosive_hazard_type = qzss_dcx_camf_d34_explosive_hazard_type[camf.d34]

        if self.ignore_ex1 is False:
            self.ex1_target_area = qzss_dcx_ex1_target_area_code_en[camf.ex1]
            self.ex1_target_area_ja = qzss_dcx_ex1_target_area_code_ja[camf.ex1]

        if self.ignore_ex2_to_ex7 is False:
            if camf.ex2 == 0:
                self.ex2_evacuate_direction_type = "Leave the additional target area range."
            else:
                self.ex2_evacuate_direction_type = "Head to the additional target area range."
            self.ex3_additional_ellipse_centre_latitude = -90 + 180 / 0x1FFFF * camf.ex3
            self.ex4_additional_ellipse_centre_longitude = 45 + 180 / 0x1FFFF * camf.ex4
            self.ex5_additional_ellipse_semi_major_axis = __get_axis(camf.ex5)
            self.ex6_additional_ellipse_semi_minor_axis = __get_axis(camf.ex6)
            self.ex7_ellipse_azimuth = -90 + 180 / 0x40 * camf.ex7
        if self.ignore_ex8_to_ex9 is False:
            if camf.ex8 == 0:
                self.ex8_target_area_list_type = 'Prefecture code'
            else:
                self.ex8_target_area_list_type = 'Municipality code'
            self.ex9_target_area_list = []
            self.ex9_target_area_list_ja = []
            if camf.ex8 == 0:  # prefecture code
                for key in qzss_dcx_camf_ex9_target_area_code_en.keys():
                    if key & camf.ex9 >> 17:
                        self.ex9_target_area_list.append(qzss_dcx_camf_ex9_target_area_code_en[key])
                        self.ex9_target_area_list_ja.append(qzss_dcx_camf_ex9_target_area_code_ja[key])
            else:  # municipality code
                for i in range(4):
                    key = self.extract_field(147 + i * 16, 16)
                    if key != 0:
                        self.ex9_target_area_list.append(qzss_dcx_ex1_target_area_code_en[key])
                        self.ex9_target_area_list_ja.append(qzss_dcx_ex1_target_area_code_ja[key])

        self.dcx_version = camf.vn

        if dcx_message_type == DcxMessageType.OUTSIDE_JAPAN:
            return QzssDcxOutsideJapan(**self.get_params())
        elif dcx_message_type == DcxMessageType.L_ALERT:
            return QzssDcxJAlert(**self.get_params())
        elif dcx_message_type == DcxMessageType.J_ALERT:
            return QzssDcxLAlert(**self.get_params())
        elif dcx_message_type == DcxMessageType.MT_INFO:
            return QzssDcxMTInfo(**self.get_params())
        else:  # has to be an unknown message
            return QzssDcxUnknown(**self.get_params())
