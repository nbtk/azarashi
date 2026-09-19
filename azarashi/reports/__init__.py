"""The report objects that decode() and decode_stream() return."""
from typing import TypeAlias

from . import base
from . import dcr
from . import dcx

Report: TypeAlias = dcr.Base | dcx.Base  # what decode() and decode_stream() return

__all__ = ['Report', 'base', 'dcr', 'dcx']
