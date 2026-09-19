"""The report objects that decode() and decode_stream() return."""
from typing import TypeAlias

from . import base
from . import dcx
from . import jma

Report: TypeAlias = jma.Base | dcx.Base  # what decode() and decode_stream() return

__all__ = ['Report', 'base', 'dcx', 'jma']
