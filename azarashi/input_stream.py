import os
import stat
import sys
from collections.abc import Callable
from typing import Any, BinaryIO

import serial


def open_input(path: str, baudrate: int = 9600) -> BinaryIO | serial.SerialBase:
    """Open the input of the command line tools as a binary stream.

    'stdin', regular files and named pipes are read as they are. Anything else, such as a
    serial device, a port name like COM3 or a pySerial URL, is opened with pySerial.
    """
    if path == 'stdin':
        return sys.stdin.buffer
    try:
        is_file = not stat.S_ISCHR(os.stat(path).st_mode)
    except OSError:  # COM3, socket://... and other names that are not paths
        is_file = False
    if is_file:
        return open(path, mode='rb')
    return serial.serial_for_url(path, baudrate=baudrate, timeout=None)  # block until data arrives


class RecordingStream:
    """Passes a binary stream through while appending every byte read from it to a file."""

    def __init__(self, stream: BinaryIO | serial.SerialBase, record: BinaryIO) -> None:
        self._stream = stream
        self._record = record

    def __getattr__(self, name: str) -> Any:
        return getattr(self._stream, name)

    def _copy(self, data: bytes) -> bytes:
        if data:
            self._record.write(data)
            self._record.flush()
        return data

    def read(self, *args: Any) -> bytes:
        return self._copy(self._stream.read(*args))

    def read1(self, *args: Any) -> bytes:
        read1: Callable[..., bytes] | None = getattr(self._stream, 'read1', None)
        if callable(read1):
            return self._copy(read1(*args))
        return self._copy(self._stream.read(1))  # one byte at a time, as decode_stream() reads such streams

    def readline(self, *args: Any) -> bytes:
        return self._copy(self._stream.readline(*args))

    def close(self) -> None:
        try:
            self._stream.close()
        finally:
            self._record.close()
