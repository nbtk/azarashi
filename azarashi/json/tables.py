"""The code tables a JSON record names in `table`, in one catalogue.

A record takes the labels and the status of a code from here, and code_tables() writes the same
catalogue out, so that the two cannot disagree. A table is named `<specification>.<table>`, and a
table whose codes change with a country or a library version goes on with `.<qualifier>`.
"""
import importlib
import re
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from typing import Any, Literal

from ..definitions.camf import d_fields
from ..definitions.camf.a11_library import a11_library
from ..definitions.camf.a3_provider_identifier import a3_provider_identifier_map
from ..definitions.qzss.dcx.ex1_target_area_code import ex1_target_area_code_en, ex1_target_area_code_ja
from ..definitions.qzss.dcx.ex2_evacuate_direction_type import ex2_evacuate_direction_type
from ..definitions.qzss.dcx.ex9_target_area_code import EX9_PREFECTURE_BITS
from ..definitions.qzss.dcx.ex9_target_area_code import ex9_target_area_code_en, ex9_target_area_code_ja

Status = Literal["valid", "special", "undefined"]

DCR = "IS-QZSS-DCR-017"
DCX = "IS-QZSS-DCX-004"
CAMF = "CAMF Issue 1.2"


@dataclass(frozen=True)
class Table:
    """One code table: its names for each code, and where a specification defines it."""

    name: str
    ja: Mapping[int, Any] | None
    en: Mapping[int, Any] | None
    source: str | None  # None where azarashi does not know which specification lists the codes
    special: frozenset[int] = frozenset()  # codes that say a value is unknown, not given, not set or not used
    reserved: frozenset[int] = frozenset()  # codes the specification has not assigned, left out as undefined
    codes: tuple[int, ...] = field(init=False)

    def __post_init__(self) -> None:
        keys = (set(self.ja or {}) | set(self.en or {})) - self.reserved
        object.__setattr__(self, "codes", tuple(sorted(keys)))

    def status(self, code: int) -> Status:
        if code not in self.codes:
            return "undefined"
        return "special" if code in self.special else "valid"

    def labels(self, code: int) -> dict[str, str]:
        """The names of a code, leaving out a language that has none or an empty one."""
        if code in self.reserved:
            return {}
        found = {language: table.get(code) for language, table in (("ja", self.ja), ("en", self.en)) if table}
        return {language: text for language, text in found.items() if isinstance(text, str) and text}

    def code(self, code: int) -> dict[str, Any]:
        """A code object: the code, its status, this table and the code's labels."""
        return {"status": self.status(code), "code": str(code), "table": self.name, "labels": self.labels(code)}


def _others(names: Mapping[int, Any] | None) -> set[int]:
    """The codes a DCR table names その他, other: JMA sends one for a value its table has no code for.

    IS-QZSS-DCR-017 notes it under the information serial code: "There is a case to transmit
    undefined codes due to revise the JMA system. "15" is indicated in this case." A regional one,
    as 北海道のその他の市町村, still says which prefecture or region.
    """
    return {code for code, text in (names or {}).items()
            if isinstance(text, str) and (text.startswith("その他") or "のその他の" in text)}


def _dcr(name: str, source: str, special: tuple[int, ...] = ()) -> Table:
    tables = importlib.import_module(f"..definitions.qzss.dcr.{name}", __package__)
    ja = getattr(tables, name, None)
    return Table(
        "qzss.dcr." + name,
        ja,
        getattr(tables, name + "_en", None),
        f"{DCR} {source}",
        frozenset(special) | _others(ja),
    )


DCR_TABLES = [
    _dcr("report_classification", "Parameter Definitions (Rc)"),
    _dcr("information_type", "Parameter Definitions (It)"),
    _dcr("depth_of_hypocenter", "Tables 4.1.2-5 and 4.1.2-12 (De)", special=(511,)),
    _dcr("eew_magnitude", "Table 4.1.2-5 (Ma)", special=(127,)),
    _dcr("hypocenter_magnitude", "Table 4.1.2-12 (Ma)", special=(126, 127)),
    _dcr("epicenter_and_hypocenter", "Table 4.1.2-7", special=(0,)),
    _dcr("seismic_intensity_lower_limit", "Table 4.1.2-8", special=(14, 15)),
    _dcr("seismic_intensity_upper_limit", "Table 4.1.2-9", special=(14, 15)),
    _dcr("long_period_ground_motion_lower_limit", "Table 4.1.2-11-1", special=(0, 7)),
    _dcr("long_period_ground_motion_upper_limit", "Table 4.1.2-11-2", special=(0, 7)),
    _dcr("notification_on_disaster_prevention", "Table 4.1.2-6"),
    _dcr("eew_forecast_region", "Table 4.1.2-10"),
    _dcr("seismic_intensity", "Table 4.1.2-15"),
    _dcr("prefecture", "Table 4.1.2-16"),
    _dcr("information_serial_code", "Table 4.1.2-19"),
    _dcr("tsunami_warning_code", "Table 4.1.2-22"),
    _dcr("tsunami_height", "Table 4.1.2-23", special=(13, 14)),
    _dcr("tsunami_forecast_region", "Table 4.1.2-24"),
    _dcr("tsunamigenic_potential", "Table 4.1.2-27", special=(7,)),  # その他の津波発生の可能性有無
    _dcr("northwest_pacific_tsunami_height", "Table 4.1.2-27a", special=(511,)),
    _dcr("coastal_region", "Table 4.1.2-28", special=(99, 100)),  # Unknown, Other region
    _dcr("volcanic_warning_code", "Table 4.1.2-31"),
    _dcr("volcano_name", "Table 4.1.2-32"),
    _dcr("local_government", "Table 4.1.2-33"),
    _dcr("ambiguity_of_activity_time", "Table 4.1.2-30 (Du)"),
    _dcr("ash_fall_warning_type", "Table 4.1.2-35 (Dw1)"),
    _dcr("expected_ash_fall_time", "Table 4.1.2-35 (Ho)"),
    _dcr("ash_fall_warning_code", "Table 4.1.2-36"),
    _dcr("weather_warning_state", "Table 4.1.2-39"),
    _dcr("weather_related_disaster_sub_category", "Table 4.1.2-40"),
    _dcr("weather_forecast_region", "Table 4.1.2-41"),
    _dcr("flood_warning_level", "Table 4.1.2-44"),
    _dcr("flood_forecast_region", "Table 4.1.2-45"),
    _dcr("typhoon_reference_time_type", "Table 4.1.2-47 (Dt)"),
    _dcr("typhoon_elapsed_time_from_reference_time", "Table 4.1.2-47 (Du)"),
    _dcr("typhoon_number", "Table 4.1.2-47 (Tn)"),
    _dcr("typhoon_scale_category", "Table 4.1.2-48"),
    _dcr("typhoon_intensity_category", "Table 4.1.2-49"),
    _dcr("typhoon_central_pressure", "Table 4.1.2-47 (Pr)"),
    _dcr("typhoon_maximum_wind_speed", "Table 4.1.2-47 (W1)", special=(0,)),
    _dcr("typhoon_maximum_gust_wind_speed", "Table 4.1.2-47 (W2)", special=(0,)),
    _dcr("marine_warning_code", "Table 4.1.2-52"),
    _dcr("marine_forecast_region", "Table 4.1.2-53"),
]


def _camf(name: str, source: str, special: tuple[int, ...] = ()) -> Table:
    module = "a4_hazard_category_and_type" if name.startswith("a4_") else name
    if name.startswith("d") and name[1].isdigit():
        module = "d_fields"
    tables = importlib.import_module(f"..definitions.camf.{module}", __package__)
    return Table("camf." + name, None, getattr(tables, name), f"{CAMF} {source}", frozenset(special))


B4_NAMES = sorted((n for n in vars(d_fields) if re.fullmatch(r"d\d+_[a-z0-9_]+", n) and not n.endswith("_value")),
                  key=lambda n: int(n.split("_")[0][1:]))

CAMF_TABLES = [
    _camf("a1_message_type", "Annex C 1"),
    _camf("a2_country_region_name", "Annex C 2"),
    _camf("a4_hazard_category", "Annex C 4", special=(0,)),
    _camf("a4_hazard_type", "Annex C 4", special=(0,)),
    _camf("a4_hazard_definition", "Annex C 4", special=(0,)),
    _camf("a5_severity", "Annex C 5", special=(0,)),
    _camf("a8_hazard_duration", "Annex C 8", special=(0,)),
    _camf("a9_type_of_library", "Annex C 9"),
    _camf("a10_library_version", "Annex C 10"),
    _camf("a17_type_of_specific_settings", "Annex C 17"),
    _camf("c7_shift_of_second_ellipse_centre", "Annex C 18.3.1"),
    _camf("c8_homothetic_factor_of_second_ellipse", "Annex C 18.3.2"),
    _camf("c9_bearing_angle_of_second_ellipse", "Annex C 18.3.3"),
    _camf("c10_instruction_library_for_second_ellipse", "Annex C 18.3.4", special=(0,)),
    *(_camf(name, f"Annex C 18.4.35.{name.split('_')[0][1:]}", special=(0,) if name == "d30_nuclear_event_scale" else ())
      for name in B4_NAMES),
]


def prefecture_code(bit: int) -> int:
    """The code a record gives the EX9 prefecture of a bit, counted from the lowest bit as 0.

    It is the prefecture's place in IS-QZSS-DCX-004 Table 4.2-25, counted from the top: Hokkaido,
    the lowest bit, is 1 and Okinawa 47. These are the codes of IS-QZSS-DCR-017 Table 4.1.2-16.
    """
    return bit + 1


def _prefecture_names(table: Mapping[int, str]) -> dict[int, str]:
    """The prefectures of EX9 by the code a record gives them, rather than by mask."""
    return {prefecture_code(bit): table[1 << bit] for bit in range(EX9_PREFECTURE_BITS) if 1 << bit in table}


DCX_TABLES = [
    Table("qzss.dcx.ex1_target_area_code", ex1_target_area_code_ja, ex1_target_area_code_en, f"{DCX} Table 4.2-21"),
    Table("qzss.dcx.ex2_evacuate_direction_type", None, ex2_evacuate_direction_type, f"{DCX} Table 4.2-22"),
    Table("qzss.dcx.ex9_target_area_code_list", _prefecture_names(ex9_target_area_code_ja),
          _prefecture_names(ex9_target_area_code_en), f"{DCX} Table 4.2-25"),
]

JAPAN = 111

def provider(country: int) -> Table:
    """The A3 providers a country assigns, empty for a country azarashi has none of."""
    providers = a3_provider_identifier_map.get(country)
    if providers is None:
        return Table(f"camf.a3_provider_identifier.country_{country}", None, None, None)
    return Table(f"camf.a3_provider_identifier.country_{country}", None, providers, f"{DCX} Table 4.2-6",
                 frozenset([0]))  # not used


def instruction(library: int, country: int, version: int, *, part: Literal['list_a', 'list_b'] = 'list_a') -> Table:
    """The A11 instructions of the library A9 chooses, in the version A10 gives."""
    tables = a11_library(library, country, version)
    if library == 0:  # CAMF's own library, the same for every country
        names = tables.en if part == 'list_a' else tables.en_b
        if names is None:
            return Table(f"camf.a11_instruction_library.international.version_{version}.{part}", None, None, None)
        return Table(f"camf.a11_instruction_library.international.version_{version}.{part}", None,
                     {**names, 0: "No instruction"},  # CAMF Issue 1.2, 3.5.3: 00000 is the empty value of a list
                     f"{CAMF} Annex C 11", frozenset([0]),
                     reserved=frozenset() if part == 'list_a' else frozenset([29, 30]))
    source = f"{DCX} Tables 4.2-14 and 4.2-15" if tables.en is not None else None
    special = (0,) if tables.en is not None else ()  # all bits 0: no instruction
    return Table(f"camf.a11_instruction_library.country_{country}.version_{version}", tables.ja, tables.en, source,
                 frozenset(special))


TABLES: dict[str, Table] = {t.name: t for t in DCR_TABLES + CAMF_TABLES + DCX_TABLES}


def every_table() -> Iterator[Table]:
    """Every table a record can name with codes azarashi knows, the providers and libraries it has among them."""
    yield from TABLES.values()
    for country in sorted(a3_provider_identifier_map):
        yield provider(country)
    yield instruction(0, 0, 0)
    yield instruction(0, 0, 0, part='list_b')
    yield instruction(1, JAPAN, 0)


def code_tables() -> dict[str, Any]:
    """The catalogue as the code tables file gives it."""
    tables: dict[str, Any] = {}
    for table in every_table():
        codes = {str(code): {"status": table.status(code), "labels": table.labels(code)} for code in table.codes}
        tables[table.name] = {"source": table.source, "codes": codes}
    return {"schema_version": 2, "tables": tables}
