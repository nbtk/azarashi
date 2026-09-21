"""Static checks of the internal decoding boundaries; do not execute this file."""
from datetime import UTC, datetime

from azarashi.decoders.common import Decoder
from azarashi.decoders.context import Frame, Message, Jma
from azarashi.decoders import dcr, dcx

stamp = datetime.now(UTC)
Decoder('', nmea='', timestamp=stamp)  # want: call-arg
Decoder('', message='invalid', nmea='', timestamp=stamp)  # want: arg-type
Decoder('', message=b'', nmea='', timestamp=stamp, satelite_id=55)  # want: call-arg

frame = Frame(sentence='', message=b'', nmea='', timestamp=stamp)
message = Message(**frame.params(), preamble='A', message_type='DCR')
Message(**frame.params(), preamble='A')  # want: call-arg
Message(**frame.params(), preamble=1, message_type='DCR')  # want: arg-type
dcr.Decoder(frame)  # want: arg-type
dcx.Decoder(frame)  # want: arg-type
dcr.EarthquakeEarlyWarning(message)  # want: arg-type
Jma(**message.params(), version=1, report_classification='', report_classification_en='', report_classification_no=1, disaster_category='', disaster_category_en='', disaster_category_no=1, information_type='', information_type_en='', information_type_no=0)  # want: call-arg
Jma(**message.params(), version=1, report_classification='', report_classification_en='', report_classification_no=1, disaster_category='', disaster_category_en='', disaster_category_no=1, information_type='', information_type_en='', information_type_no=0, report_time='invalid')  # want: arg-type
