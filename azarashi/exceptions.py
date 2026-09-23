class AzarashiException(Exception):
    """Everything azarashi raises. Catch this to report any of them in one place.

    It says nothing about what to do next. AzarashiReadOn, AzarashiReopenStream,
    AzarashiStopReading and AzarashiFixTheCall say that. A reading loop catches the first three
    and lets the fourth through, since no read can put a wrong call right. Neither they nor this
    class are ever raised: what is raised is one of the classes under them, which say what
    happened. The message is in .message and the object it came from in .instance.
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

    It is a ValueError, so a layer that knows nothing of azarashi reads it as bad input.
    """


class AzarashiInvalidMessageError(AzarashiDecodeError):
    """The message cannot be read: a length, a checksum or a CRC is wrong, or no decoder fits it.

    A code value the spec does not define is not one of these; it is kept and named in the report.
    """


class AzarashiNotImplementedError(AzarashiDecodeError):
    """azarashi has no decoder for the message, e.g. an experimental broadcast.

    It is not a NotImplementedError, and so not a RuntimeError either: a message azarashi
    cannot decode yet is ordinary traffic, not code left unwritten.
    """


class AzarashiTimeoutError(AzarashiReadOn):
    """A read on a stream with a timeout (e.g. pySerial) returned no data or an incomplete line.

    Partially read data is kept, so calling decode_stream() again continues from it.

    It inherits Exception, but not EOFError, TimeoutError or OSError. The data has not ended,
    so it is not an EOFError. TimeoutError is an OSError and would put it among the failures
    of the stream itself.

    It stays outside AzarashiDecodeError because nothing failed to decode.
    """


class AzarashiReopenStream(AzarashiException, OSError):
    """The stream is unusable, and a new one is the way on: close it and open it again.

    Reading it again returns the error at once, so a caller that reads on spins. Reopening the
    same weakly referenceable object (e.g. pySerial) keeps the duplicate memory of unique=,
    which is per stream. For other objects, the state is discarded when a later lookup sees
    them closed, so reopening does not guarantee that their duplicate memory remains.

    It is an OSError, which is what the streams themselves raise, serial.SerialException among
    them. It is neither an AzarashiReadOn nor an EOFError, so no clause order can take it for
    either of them.
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
    the loss of a live feed is for the caller to tell.
    """


class AzarashiFixTheCall(AzarashiException):
    """The call itself is wrong, and no read will put it right: fix the code that makes it.

    The arguments alone decide it, so calling again the same way fails the same way. It is found
    before anything is read, except that whether a stream gives text or bytes shows at its first
    read. What a message holds is never a mistake in the call: a message that cannot be read is
    AzarashiInvalidMessageError, and reading on is the way past it.

    It is outside AzarashiReadOn, AzarashiReopenStream and AzarashiStopReading, so a reading loop
    that catches those three lets it through and the program stops with the reason, instead of
    retrying a call that cannot succeed or ending as if the data had run out.
    """


class AzarashiUnsupportedFormatError(AzarashiFixTheCall, ValueError):
    """The format asked for is not one azarashi reads, or not one this call reads.

    A msg_type outside nmea, spresense, hex, ublox and net, or net given to a call that reads a
    stream. It is a ValueError: the argument is a string, and one azarashi does not take.
    """


class AzarashiArgumentTypeError(AzarashiFixTheCall, TypeError):
    """An argument is not the kind of object the call needs.

    A message that is neither text nor bytes, a timestamp that is not a datetime, a stream without
    the method its format reads with or one that gives text where bytes are read, a callback that
    cannot be called, callback arguments that are not a sequence or a mapping of names, a unique=
    that is neither a truth value nor a number, or something given to the JSON conversion that is
    not a report. It is a TypeError, as Python's own calls report an argument of the wrong kind.
    """
