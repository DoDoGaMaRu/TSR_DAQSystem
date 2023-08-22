import io
import pickle
import asyncio


SEP         : bytes = b'\o'
SEP_LEN     : int = len(SEP)


class ProtocolException(Exception):
    pass


def tcp_send_protocol(writer: asyncio.StreamWriter, event, data):
    try:
        with io.BytesIO() as memfile:
            pickle.dump((event, data), memfile)
            serialized = memfile.getvalue()
        writer.write(serialized + SEP)
    except Exception:
        raise ProtocolException()
