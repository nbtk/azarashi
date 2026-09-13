import logging
import time


def utc_formatter():
    """Log line formatter with ISO 8601 UTC times, e.g. 2026-09-13T14:50:14.119Z."""
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    formatter.converter = time.gmtime
    formatter.default_time_format = '%Y-%m-%dT%H:%M:%S'
    formatter.default_msec_format = '%s.%03dZ'
    return formatter


def configure_logging(level=logging.INFO):
    handler = logging.StreamHandler()
    handler.setFormatter(utc_formatter())
    logging.basicConfig(level=level, handlers=[handler])
