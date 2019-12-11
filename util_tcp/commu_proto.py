# Protocol of communication

import socket
from copy import deepcopy
from typing import Union

__all__ = ['read_wukong_data', 'write_wukong_data', 'WukongPkg', 'TcpSvr', 'TcpClient', 'QUEUE_FULL', 'QUEUE_GET',
           'QUEUE_PUT',
           'QUEUE_EMPTY',
           'QUEUE_HAVA_DATA',
           'QUEUE_STATUS_NONE',
           'QUEUE_QUERY_STATUS',
           'QUEUE_OK',
           'QUEUE_FAIL',
           'QUEUE_PING',
           'QUEUE_PONG']

# stream delimeter
delimeter = b'bye:)'
delimeter_escape = b'bye:]'
delimeter_len = len(delimeter)


def msg_escape(msg: bytes) -> bytes:
    return msg.replace(delimeter, delimeter_escape)


def msg_recover(msg: bytes) -> bytes:
    return msg.replace(delimeter_escape, delimeter)


class WukongPkg:
    def __init__(self, msg: bytes = b'', err=None):
        if not isinstance(msg, bytes):
            raise Exception('Support byte only.')
        self.data = msg
        self.err = err

    def __repr__(self):
        return self.data.decode()

    def __bool__(self):
        return len(self.data) > 0


# const
max_bytes = 1024

# buffer
STREAM_BUFFER = []


def read_wukong_data(conn: socket.socket) -> WukongPkg:
    """block read"""
    global STREAM_BUFFER

    buffer = deepcopy(STREAM_BUFFER)
    STREAM_BUFFER.clear()

    while True:
        try:
            data: bytes = conn.recv(max_bytes)
        except Exception as e:
            return WukongPkg(err=f'{e.__class__,e.args}')

        bye_index = data.find(delimeter)
        if bye_index == -1:
            buffer.append(data)
            continue

        buffer.append(data[:bye_index])
        if len(data) < bye_index + delimeter_len:
            STREAM_BUFFER.append(data[bye_index + delimeter_len:])
        break

    ret = WukongPkg(msg_recover(b''.join(buffer)))
    return ret


def write_wukong_data(conn: socket.socket, msg: WukongPkg) -> (bool, str):
    """NOTE: Sending an empty string is allowed"""
    _bytes_msg = msg_escape(msg.data) + delimeter
    _bytes_msg_len = len(_bytes_msg)
    sent_index = -1
    err = ''

    def _send_msg(msg: bytes):
        try:
            conn.send(msg)
            return True
        except Exception as e:
            nonlocal err
            err = f'{e.__class__, e.args}'
            return False

    while sent_index < _bytes_msg_len:
        sent_index = 0 if sent_index == -1 else sent_index
        will_send_data = _bytes_msg[sent_index:sent_index + max_bytes]
        if not _send_msg(will_send_data):
            return False, err
        sent_index += max_bytes

    return True, err


class TcpConn:
    def __init__(self):
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.err = None

    def write(self, data) -> bool:
        ok, self.err = write_wukong_data(self.skt, WukongPkg(data))
        return ok

    def read(self):
        wukongpkg = read_wukong_data(self.skt)
        self.err = wukongpkg.err
        return wukongpkg.data

    def close(self):
        self.skt.close()


class TcpSvr(TcpConn):
    def __init__(self, host='127.0.0.1', port=9999, max_conns=5):
        super().__init__()
        self.skt.bind((host, port))
        self.max_conns = max_conns

    def listen(self):
        self.skt.listen(self.max_conns)

    def accept(self):
        return self.skt.accept()

    def close(self):
        self.skt.close()


class TcpClient(TcpConn):
    def __init__(self, host='127.0.0.1', port=9999):
        super().__init__()
        self.skt.connect((host, port))

    def close(self):
        self.skt.close()


QUEUE_PUT = b'PUT:'
QUEUE_GET = b'GET:'
QUEUE_HAVA_DATA = b'DATA:'
QUEUE_FULL = b'FULL'
QUEUE_EMPTY = b'EMPTY'
QUEUE_STATUS_NONE = b'NONE'
QUEUE_QUERY_STATUS = b'STATUS'
QUEUE_OK = b'OK'
QUEUE_FAIL = b'FAIL'
QUEUE_PING = B'PING'
QUEUE_PONG = b'PONG'
