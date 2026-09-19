"""The report objects that decode() and decode_stream() return."""
from typing import TypeAlias

from .base import *
from .dcx import *
from .jma import *
from .dcx import QzssDcXtendedMessageBase
from .jma import QzssDcReportJmaBase

QzssDcReport: TypeAlias = QzssDcReportJmaBase | QzssDcXtendedMessageBase  # what decode() and decode_stream() return
