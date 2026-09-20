class AzarashiException(Exception):
    """Everything azarashi raises. Catch this to report any of them in one place.

    It says nothing about what to do next, only that azarashi is what stopped, and it holds
    what they all carry: the message, and the object it came from.

    The three classes under it are what a reading loop has to tell apart. Two of them are named
    after the way on, because there is one: AzarashiReadOn and AzarashiReopenStream. The third,
    AzarashiNoMoreData, is named after the fact, because there is no way on. Under the three sit
    the classes named after what happened, which is what a log line wants.
    """

    def __init__(self, message: str, instance: object = None) -> None:
        self.message = message
        self.instance = instance
        super().__init__(self.message)

    def __str__(self) -> str:
        sentence = getattr(self.instance, 'nmea', None) or getattr(self.instance, 'sentence', None)
        if not sentence:  # nothing to show: an empty one would leave a dangling arrow
            return self.message
        elif type(sentence) is bytes:
            sentence = "b'" + ''.join(r'\x%02X' % c for c in sentence) + "'"
        elif type(sentence) is not str:
            sentence = str(sentence)
        return f'{self.message} -> {sentence}'


class AzarashiReadOn(AzarashiException):
    """Reading again is the way on: the stream is well, and only this read brought no report.

    Every failure of a message sits under here. A message that cannot be read is behind you and
    the next one follows it; a message that is not complete yet is resumed by the next read.
    """


class AzarashiDecodeError(AzarashiReadOn, ValueError):
    """A message did not become a report. Catch this one to log it and keep reading the stream.

    It is a ValueError, which is what Python raises for data it cannot make sense of, and what
    the decoders of the standard library raise: json.JSONDecodeError and UnicodeDecodeError are
    both ValueErrors. A layer that knows nothing of azarashi then reads it as bad input rather
    than as a fault of its own.
    """


class AzarashiInvalidMessageError(AzarashiDecodeError):
    """The message cannot be read: a length, a checksum or a CRC is wrong, or no decoder fits it.

    A code value the spec does not define is not one of these; it is kept and named in the report.
    """


class AzarashiNotImplementedError(AzarashiDecodeError):
    """azarashi has no decoder for the message, e.g. an experimental broadcast.

    It is deliberately not a NotImplementedError. That one, and the RuntimeError it inherits,
    mean a piece of code was left unwritten, so a layer that caught it would take a message the
    satellite really sent for a fault of its own. A message azarashi cannot decode yet is
    ordinary traffic, not a fault.
    """


class AzarashiTimeoutError(AzarashiReadOn):
    """A stream with a read timeout (e.g. pySerial) had no complete message before the timeout expired.

    Partially read data is kept, so calling decode_stream() again continues from it.

    It carries no exception of the standard library. It is not an EOFError, because the data has
    not ended and a layer reading it as the end would stop a stream that is still live. Nor is
    it a TimeoutError, which is an OSError and would land it among the failures of the stream
    itself, where a caller that reopens on OSError would reopen a device that is perfectly well.

    It stays outside AzarashiDecodeError because nothing failed to decode.
    """


class AzarashiReopenStream(AzarashiException, OSError):
    """The stream is unusable, and a new one is the way on: close it and open it again.

    Reading it again returns the error at once, so a caller that reads on spins. Reopening the
    same object keeps the duplicate memory of unique=, which is per stream.

    It is an OSError, which is what the streams themselves raise (serial.SerialException among
    them), so existing OSError handling keeps working. It is deliberately neither an
    AzarashiReadOn nor an EOFError: reading on is wrong, and the data did not end. Being
    outside both means no clause order can turn it into either.
    """


class AzarashiDisconnectedError(AzarashiReopenStream):
    """The device or the far side went away while it was being read.

    A USB serial adapter was pulled out, a socket was reset, or the read failed some other way
    that the stream reported as an OSError.
    """


class AzarashiStreamClosedError(AzarashiReopenStream):
    """The stream was closed while it was being read.

    An io object raises ValueError rather than OSError once it is closed. Reopening is the way
    on if a reconnect closed it, but a program that closed the stream and kept reading it will
    see this too, and reopening in a loop would hide that.
    """


class AzarashiStopReading(AzarashiException, EOFError):
    """There is nothing more to take and no way on: stop reading.

    It is an EOFError so that existing EOF handling keeps working. The classes under it say why
    there is nothing more.
    """


class AzarashiNoMoreData(AzarashiStopReading):
    """The data ran out: a file reached its end, or the far side of a socket closed it.

    Nothing broke, so there is nothing to put right; there is simply nothing left to take. A
    device that was pulled out is AzarashiDisconnectedError instead, because that stream can be
    opened again and this one has run out. Whether running out is the end of a recorded file or
    the loss of a live feed is for the caller to say, so this says only the fact.
    """
