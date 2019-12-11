# Protocol of communication

import socket
from copy import deepcopy
from typing import Union

# stream flag
delimeter = b'bye:)'
delimeter_len = len(delimeter)


def msg_escape(msg: bytes) -> bytes:
    return msg.replace(delimeter, b'bye:]')


def msg_recover(msg: bytes) -> bytes:
    return msg.replace(b'bye:]', delimeter)


class WukongPkg:
    def __init__(self, msg: Union[str, bytes]):
        if isinstance(msg, bytes):
            self.data = msg
        elif isinstance(msg, str):
            self.data = bytes(msg, encoding='utf8')
        else:
            raise Exception('Support byte or str only.')

    def __repr__(self):
        return self.data.decode()

    def __bool__(self):
        return len(self.data) > 0


# const
max_bytes = 1024

STREAM_BUFFER = []


def read_wukong_data(conn: socket.socket) -> WukongPkg:
    """"""

    global STREAM_BUFFER

    buffer = deepcopy(STREAM_BUFFER)
    print('STREAM_BUFFER', len(STREAM_BUFFER), STREAM_BUFFER)
    STREAM_BUFFER.clear()

    while True:
        data: bytes = conn.recv(max_bytes)
        bye_index = data.find(delimeter)
        if bye_index == -1:
            buffer.append(data)
            continue

        buffer.append(data[:bye_index])
        if len(data) < bye_index + delimeter_len:
            STREAM_BUFFER.append(data[bye_index + delimeter_len:])
        break

    ret = WukongPkg(msg_recover(b''.join(buffer)).decode())
    return ret


def write_wukong_data(conn: socket.socket, msg: WukongPkg) -> bool:
    """NOTE: Sending an empty string is allowed"""
    _bytes_msg = msg_escape(msg.data) + delimeter
    _bytes_msg_len = len(_bytes_msg)
    sent_index = -1

    def _send_msg(msg: bytes):
        try:
            conn.send(msg)
            return True
        except Exception as e:
            print(f'conntion:{conn.getpeername()} closed, err:{e.__class__, e.args}!')
            return False

    while sent_index < _bytes_msg_len:
        sent_index = 0 if sent_index == -1 else sent_index
        will_send_data = _bytes_msg[sent_index:sent_index + max_bytes]
        if not _send_msg(will_send_data):
            return False
        sent_index += max_bytes

    return True
