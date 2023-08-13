import io
import pickle


def tcp_send_protocol(event, data):
    with io.BytesIO() as memfile:
        pickle.dump((event, data), memfile)
        serialized = memfile.getvalue()
    return serialized + b'\o'
