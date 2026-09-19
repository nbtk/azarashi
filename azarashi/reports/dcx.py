"""The reports of a DCX message (MT44), whose fields are the CAMF ones."""
from datetime import datetime
from typing import Any

from .base import MessageBase


class Camf:
    """The fields of a DCX message as transmitted.

    The C and D fields are None unless the specific settings (A17) and the hazard (A4) carry them.
    """
    sdmt: int
    sdm: int
    a1: int
    a2: int
    a3: int
    a4: int
    a5: int
    a6: int
    a7: int
    a8: int
    a9: int
    a10: int
    a11: int
    a12: int
    a13: int
    a14: int
    a15: int
    a16: int
    a17: int
    a18: int
    c1: int | None = None
    c2: int | None = None
    c3: int | None = None
    c4: int | None = None
    c5: int | None = None
    c6: int | None = None
    c7: int | None = None
    c8: int | None = None
    c9: int | None = None
    c10: int | None = None
    d1: int | None = None
    d2: int | None = None
    d3: int | None = None
    d4: int | None = None
    d5: int | None = None
    d6: int | None = None
    d7: int | None = None
    d8: int | None = None
    d9: int | None = None
    d10: int | None = None
    d11: int | None = None
    d12: int | None = None
    d13: int | None = None
    d14: int | None = None
    d15: int | None = None
    d16: int | None = None
    d17: int | None = None
    d18: int | None = None
    d19: int | None = None
    d20: int | None = None
    d21: int | None = None
    d22: int | None = None
    d23: int | None = None
    d24: int | None = None
    d25: int | None = None
    d26: int | None = None
    d27: int | None = None
    d28: int | None = None
    d29: int | None = None
    d30: int | None = None
    d31: int | None = None
    d32: int | None = None
    d33: int | None = None
    d34: int | None = None
    d35: int | None = None
    d36: int | None = None
    ex1: int
    ex2: int
    ex3: int
    ex4: int
    ex5: int
    ex6: int
    ex7: int
    ex8: int
    ex9: int
    ex10: int
    vn: int

    def __str__(self) -> str:
        return str(self.__dict__)

    def __repr__(self) -> str:  # a report holds one of these, and an address tells the reader nothing
        return f'{type(self).__name__}({", ".join(f"{k}={v}" for k, v in self.__dict__.items())})'

    def get_params(self) -> dict[str, int]:
        return dict(self.__dict__)  # a copy, as Report.get_params() gives


class Base(MessageBase):
    """What every DCX message carries, a null message included.

    The alert itself is on AlertBase; a null message has none.
    """
    dcx_message_type: str
    satellite_designation_mask_type: str
    satellite_designation_mask: list[str]

    def __init__(self,
                 camf: Camf,
                 ignore_a12_to_a16: bool,
                 ignore_a17_to_a18: bool,
                 ignore_ex1: bool,
                 ignore_ex2_to_ex7: bool,
                 ignore_ex8_to_ex9: bool,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.camf = camf
        self.ignore_a12_to_a16 = ignore_a12_to_a16
        self.ignore_a17_to_a18 = ignore_a17_to_a18
        self.ignore_ex1 = ignore_ex1
        self.ignore_ex2_to_ex7 = ignore_ex2_to_ex7
        self.ignore_ex8_to_ex9 = ignore_ex8_to_ex9

        for key, value in kwargs.items():
            if key not in self.__dict__:
                self.__dict__[key] = value



class AlertBase(Base):
    """A DCX message that carries an alert: everything but a null message.

    The fields below the blank line are set only when the message and its A17 specific settings
    carry them, so they are None otherwise. The ignore_* flags say which groups were read.
    """
    dcx_version: int
    a1_message_type: str
    a2_country_region_name: str
    a3_provider_identifier: str
    a4_hazard_category: str
    a4_hazard_type: str
    a4_hazard_definition: str
    a5_severity: str
    a6_hazard_onset_week: str
    a7_hazard_onset_time_of_week: str
    a6a7_hazard_onset_datetime: datetime | None
    a8_hazard_duration: str
    a9_type_of_library: str
    a10_library_version: str

    a11_international_library_code: str | None = None
    a11_international_library: str | None = None
    a11_japanese_library: str | None = None
    a11_japanese_library_ja: str | None = None
    a12_ellipse_centre_latitude: float | None = None
    a13_ellipse_centre_longitude: float | None = None
    a14_ellipse_semi_major_axis: float | None = None
    a15_ellipse_semi_minor_axis: float | None = None
    a16_ellipse_azimuth: float | None = None
    a17_type_of_specific_settings: str | None = None
    c1_refined_latitude_of_centre_of_main_ellipse: float | None = None
    c2_refined_longitude_of_centre_of_main_ellipse: float | None = None
    c3_refined_length_of_semi_major_axis: float | None = None
    c4_refined_length_of_semi_minor_axis: float | None = None
    c5_latitude_of_centre_of_hazard: float | None = None
    c6_longitude_of_centre_of_hazard: float | None = None
    c7_shift_of_second_ellipse_centre: int | None = None
    c8_homothetic_factor_of_second_ellipse: float | None = None
    c9_bearing_angle_of_second_ellipse: float | None = None
    c10_instruction_library_for_second_ellipse_code: str | None = None
    c10_instruction_library_for_second_ellipse: str | None = None
    d1_magnitude_on_richter_scale: str | None = None
    d2_seismic_coefficient: str | None = None
    d3_azimuth_from_centre_of_main_ellipse_to_epicentre: float | None = None  # degrees
    d4_vector_length_between_centre_of_main_ellipse_and_epicentre: float | None = None  # a factor of the semi-major axis
    d5_wave_height: str | None = None
    d6_temperature_range: str | None = None
    d7_hurricane_category: str | None = None
    d8_wind_speed: str | None = None
    d9_rainfall_amounts: str | None = None
    d10_damage_category: str | None = None
    d11_tornado_probability: str | None = None
    d12_hail_scale: str | None = None
    d13_visibility: str | None = None
    d14_snow_depth: str | None = None
    d15_flood_severity: str | None = None
    d16_lightning_intensity: str | None = None
    d17_fog_level: str | None = None
    d18_drought_level: str | None = None
    d19_avalanche_warning_level: str | None = None
    d20_ash_fall_amount_and_impact: str | None = None
    d21_geomagnetic_scale: str | None = None
    d22_terrorism_threat_level: str | None = None
    d23_fire_risk_level: str | None = None
    d24_water_quality: str | None = None
    d25_uv_index: str | None = None
    d26_number_of_cases_per_100000_inhabitants: str | None = None
    d27_noise_range: str | None = None
    d28_air_quality_index: str | None = None
    d29_outage_estimated_duration: str | None = None
    d30_nuclear_event_scale: str | None = None
    d31_chemical_hazard_type: str | None = None
    d32_biohazard_level: str | None = None
    d33_biohazard_type: str | None = None
    d34_explosive_hazard_type: str | None = None
    d35_infection_type: str | None = None
    d36_typhoon_category: str | None = None
    ex1_target_area: str | None = None
    ex1_target_area_ja: str | None = None
    ex2_evacuate_direction_type: str | None = None
    ex3_additional_ellipse_centre_latitude: float | None = None
    ex4_additional_ellipse_centre_longitude: float | None = None
    ex5_additional_ellipse_semi_major_axis: float | None = None
    ex6_additional_ellipse_semi_minor_axis: float | None = None
    ex7_additional_ellipse_azimuth: float | None = None
    ex8_target_area_list_type: str | None = None
    ex9_target_area_list: list[str] | None = None
    ex9_target_area_list_ja: list[str] | None = None

    def get_hazard_onset_str(self) -> str | None:
        onset = self.a6a7_hazard_onset_datetime
        return None if onset is None else onset.isoformat().replace('+00:00', 'Z')

    def __str__(self) -> str:
        header = f"### DCX Message - {self.dcx_message_type} ###\n"
        if self.camf.a1 == 0:
                header += "*** This is a test message ***\n"

        report = header + \
                 f"A1 - Message type: {self.a1_message_type}\n" + \
                 f"A2 - Country/region name: {self.a2_country_region_name}\n" + \
                 f"A3 - Provider identifier: {self.a3_provider_identifier}\n" + \
                 f"A4 - Hazard category and type: {self.a4_hazard_category} - " + \
                 f"{self.a4_hazard_type}\n" + \
                 f"A4 - Hazard definition: {self.a4_hazard_definition}\n" + \
                 f"A5 - Severity: {self.a5_severity}\n" + \
                 f"A6A7 - Hazard onset: {self.get_hazard_onset_str()}\n" + \
                 f"A8 - Hazard duration: {self.a8_hazard_duration}\n"
        if self.camf.a9 == 0: # international
            report += f"A11 - Instruction code: {self.a11_international_library_code}\n"
            if self.camf.a11 != 0:
                report += f"A11 - Instruction: {self.a11_international_library}\n"
        elif self.camf.a9 == 1: # japanese
            if self.camf.a11 != 0:
                report += f"A11 - Instruction: {self.a11_japanese_library}\n" + \
                          f"A11 - Instruction (ja): {self.a11_japanese_library_ja}\n"

        if self.ignore_a12_to_a16 is False:
            report += f"A12 - Ellipse centre latitude: {self.a12_ellipse_centre_latitude}\n" + \
                      f"A13 - Ellipse centre longitude: {self.a13_ellipse_centre_longitude}\n" + \
                      f"A14 - Ellipse semi - major axis: {self.a14_ellipse_semi_major_axis}\n" + \
                      f"A15 - Ellipse semi - minor axis: {self.a15_ellipse_semi_minor_axis}\n" + \
                      f"A16 - Ellipse azimuth: {self.a16_ellipse_azimuth}\n"

        if self.ignore_a17_to_a18 is False:
            a17 =  self.a17_type_of_specific_settings
            if a17 is not None:
                report += f"A17 - Type of specific settings: {a17}\n"
                keys = self.__dict__.keys()
                prefix = ['c%d_' % (i + 1) for i in range(10)] + ['d%d_' % (i + 1) for i in range(36)]
                for k in keys:
                    for p in prefix:
                        if k.startswith(p):
                            ident, title = k.split('_', 1)
                            headline = ident.upper() + ' - ' + title.replace('_', ' ').capitalize()
                            content = self.__dict__.get(k)
                            report += f"{headline}: {content}\n"

        if self.ignore_ex1 is False:
            report += f"EX1 - Target area: {self.ex1_target_area}\n" + \
                      f"EX1 - Target area (ja): {self.ex1_target_area_ja}\n"

        if self.ignore_ex2_to_ex7 is False:
            report += f"EX2 - Evacuate direction type: {self.ex2_evacuate_direction_type}\n" + \
                      f"EX3 - Additional ellipse centre latitude: {self.ex3_additional_ellipse_centre_latitude}\n" + \
                      f"EX4 - Additional ellipse centre longitude: {self.ex4_additional_ellipse_centre_longitude}\n" + \
                      f"EX5 - Additional ellipse semi major axis: {self.ex5_additional_ellipse_semi_major_axis}\n" + \
                      f"EX6 - Additional ellipse semi minor axis: {self.ex6_additional_ellipse_semi_minor_axis}\n" + \
                      f"EX7 - Additional ellipse azimuth: {self.ex7_additional_ellipse_azimuth}\n"

        if self.ignore_ex8_to_ex9 is False:
            report += f"EX8 - Target area list type: {self.ex8_target_area_list_type}\n" + \
                      f"EX9 - Target area list: {self.ex9_target_area_list}\n" + \
                      f"EX9 - Target area list (ja): {self.ex9_target_area_list_ja}\n"

        if report.endswith('\n'):
            report = report[:-1]

        return report


class NullMsg(Base):
    def __init__(self,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def __str__(self) -> str:
        return f"### DCX Message - {self.dcx_message_type} ###"


class OutsideJapan(AlertBase):
    def __init__(self,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)


class LAlert(AlertBase):
    def __init__(self,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)


class JAlert(AlertBase):
    def __init__(self,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)


class MTInfo(AlertBase):
    def __init__(self,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)


class Unknown(AlertBase):
    def __init__(self,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
