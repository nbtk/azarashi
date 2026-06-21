def hex_qzss_dcr_message_extractor(reader, reader_args=None, reader_kwargs=None):
    if reader_args is None:
        reader_args = ()
    if reader_kwargs is None:
        reader_kwargs = {}
    msg = reader(*reader_args, **reader_kwargs)
    if not msg:
        raise EOFError('Encountered EOF')
    elif isinstance(msg, (bytes, bytearray)):
        msg = msg.decode()
    return msg
