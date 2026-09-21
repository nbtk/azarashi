"""Typed values passed between decoding stages; never public report instances."""
from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict


class FrameParams(TypedDict):
    sentence: str | bytes
    message: bytes
    nmea: str
    timestamp: datetime
    message_header: str | bytes | None
    satellite_id: int | None
    satellite_prn: int | None
    satellite_svid: int | None


@dataclass(frozen=True, kw_only=True)
class Frame:
    """An input format has supplied the payload and reception metadata."""

    sentence: str | bytes
    message: bytes
    nmea: str
    timestamp: datetime
    message_header: str | bytes | None = None
    satellite_id: int | None = None
    satellite_prn: int | None = None
    satellite_svid: int | None = None

    def params(self) -> FrameParams:
        return {
            'sentence': self.sentence,
            'message': self.message,
            'nmea': self.nmea,
            'timestamp': self.timestamp,
            'message_header': self.message_header,
            'satellite_id': self.satellite_id,
            'satellite_prn': self.satellite_prn,
            'satellite_svid': self.satellite_svid,
        }


class MessageParams(FrameParams):
    preamble: str
    message_type: str


@dataclass(frozen=True, kw_only=True)
class Message(Frame):
    """The shared preamble, CRC and message-type checks have completed."""

    preamble: str
    message_type: str

    def params(self) -> MessageParams:
        return {
            **super().params(),
            'preamble': self.preamble,
            'message_type': self.message_type,
        }


class JmaParams(MessageParams):
    version: int
    report_classification: str
    report_classification_en: str
    report_classification_no: int
    disaster_category: str
    disaster_category_en: str
    disaster_category_no: int
    report_time: datetime
    information_type: str
    information_type_en: str
    information_type_no: int


@dataclass(frozen=True, kw_only=True)
class Jma(Message):
    """Validated JMA common fields, ready for a disaster-category decoder."""

    version: int
    report_classification: str
    report_classification_en: str
    report_classification_no: int
    disaster_category: str
    disaster_category_en: str
    disaster_category_no: int
    report_time: datetime
    information_type: str
    information_type_en: str
    information_type_no: int

    def params(self) -> JmaParams:
        return {
            **super().params(),
            'version': self.version,
            'report_classification': self.report_classification,
            'report_classification_en': self.report_classification_en,
            'report_classification_no': self.report_classification_no,
            'disaster_category': self.disaster_category,
            'disaster_category_en': self.disaster_category_en,
            'disaster_category_no': self.disaster_category_no,
            'report_time': self.report_time,
            'information_type': self.information_type,
            'information_type_en': self.information_type_en,
            'information_type_no': self.information_type_no,
        }
