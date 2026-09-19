from . import reports
from . import reports as qzss_dc_report  # the earlier name of the module
from .exceptions import AzarashiDecodeError
from .exceptions import AzarashiError
from .exceptions import AzarashiInvalidMessageError
from .exceptions import AzarashiNotImplementedError
from .exceptions import AzarashiTimeoutError
from .exceptions import QzssDcrDecoderException
from .exceptions import QzssDcrDecoderNotImplementedError
from .exceptions import QzssDcrDecoderTimeoutError
from .interfaces import decode
from .interfaces import decode_stream
from .reports import QzssDcReport

__all__ = [
    # the two entry points
    'decode',
    'decode_stream',

    # the report classes, and the type of what the entry points return
    'reports',
    'QzssDcReport',

    # every exception azarashi defines
    'AzarashiError',
    'AzarashiDecodeError',
    'AzarashiInvalidMessageError',
    'AzarashiNotImplementedError',
    'AzarashiTimeoutError',

    # the earlier names: of the module above, and of three of the exceptions
    'qzss_dc_report',
    'QzssDcrDecoderException',
    'QzssDcrDecoderNotImplementedError',
    'QzssDcrDecoderTimeoutError',
]
