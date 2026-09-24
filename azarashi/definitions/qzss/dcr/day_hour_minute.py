from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....reports.base import DayHourMinute

days = range(1, 32)
hours = range(0, 24)
minutes = range(0, 60)

# names a whole time field (day, hour and minute) as one number when it is not a time
occurrence_time_of_earthquake_undefined = "地震発生時刻(コード番号：%d)"
occurrence_time_of_earthquake_undefined_en = "Undefined Occurrence Time of Earthquake (Code: %d)"
activity_time_undefined = "日時(コード番号：%d)"
activity_time_undefined_en = "Undefined Activity Time (Code: %d)"
typhoon_reference_time_undefined = "基点時刻(コード番号：%d)"
typhoon_reference_time_undefined_en = "Undefined Reference Time (Code: %d)"
expected_tsunami_arrival_time_undefined = "津波到達予想時刻(コード番号：%d)"
expected_tsunami_arrival_time_undefined_en = "Undefined Expected Tsunami Arrival Time (Code: %d)"


def expected_tsunami_arrival_time_kind(raw: 'DayHourMinute', is_time: bool) -> tuple[str, str]:
    """What an expected tsunami arrival time is, in Japanese and English, given whether it is a time."""
    if (raw['hour'], raw['minute']) == (31, 63):  # has arrived (estimated or observed)
        return '津波到達中と推測', 'Tsunami arrival expected'
    if (raw['day'], raw['hour'], raw['minute']) == (0, 30, 62):  # no data
        return '該当情報なし', 'No data'
    if not is_time:
        code = raw['day'] << 11 | raw['hour'] << 6 | raw['minute']  # the whole field (12 bits)
        return expected_tsunami_arrival_time_undefined % code, expected_tsunami_arrival_time_undefined_en % code
    return '津波の到達予想時刻', 'Estimated initial tsunami arrival time'
