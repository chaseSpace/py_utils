# Protocol of communication

import socket
from copy import deepcopy


class SupportBytesOnly(Exception):
    pass


__all__ = ['read_wukong_data', 'write_wukong_data', 'WukongPkg', 'TcpSvr', 'TcpClient',
           'QUEUE_FULL',
           'QUEUE_GET',
           'QUEUE_PUT',
           'QUEUE_EMPTY',
           'QUEUE_NORMAL',
           'QUEUE_QUERY_STATUS',
           'QUEUE_OK',
           'QUEUE_FAIL',
           'QUEUE_PING',
           'QUEUE_PONG',
           'QUEUE_DATA',
           'QUEUE_SIZE',
           'QUEUE_MAXSIZE',
           'QUEUE_RESET',
           'QUEUE_PARAMS',
           'QUEUE_CLIENTS']

# stream delimiter
delimiter = b'bye:)'
delimiter_escape = b'bye:]'
delimiter_len = len(delimiter)

params_gap = ':'
params_gap_escape = '-'
params_split = '\n'
params_split_escape = '/n'

params_escape_map = {
    # delimiter: delimiter_escape,
    params_gap: params_gap_escape,
    params_split: params_split_escape
}


def msg_escape(msg: str) -> str:
    for k, v in params_escape_map.items():
        msg = msg.replace(k, v)
    return msg


def msg_unescape(msg: str) -> str:
    for k, v in params_escape_map.items():
        msg = msg.replace(v, k)
    return msg


def parse_params(msg: str) -> dict:
    """do parse after convert to str"""
    params_lst = msg.split(params_split)
    params_d = {}
    _params_gap = params_gap
    for i in params_lst:
        s = i.split(_params_gap)
        if len(s) == 1:
            print('parse_params fail', i)
            return {}
        params_d[s[0]] = s[1]
    return params_d


def package_params(params: dict) -> str:
    """do package before convert to bytes, support str only."""
    kv_lst = []
    for k, v in params.items():
        kv_lst.append(params_gap.join([k, v]))
    return params_split.join(kv_lst)


class WukongPkg:
    """customized communication msg package"""

    def __init__(self, msg: bytes = b'', err=None, closed=False):
        """
        :param msg: raw bytes
        :param err: error encountered reading socket
        :param closed: whether the socket is closed.
        """
        if not isinstance(msg, bytes):
            raise SupportBytesOnly('Support bytes only')
        self.raw_data = msg
        self.err = err
        self._is_skt_closed = closed

    def __repr__(self):
        return self.raw_data.decode()

    def __bool__(self):
        return len(self.raw_data) > 0

    def get_params(self) -> dict:
        """TODO: complete the feature"""
        return parse_params(self.raw_data.decode())

    def is_valid(self) -> bool:
        if self._is_skt_closed or self.err:
            return False
        return True


# max read/write to 4KB
MAX_BYTES = 1 << 12

# buffer
STREAM_BUFFER = []


def read_wukong_data(conn: socket.socket) -> WukongPkg:
    """Block read from tcp socket connection"""
    global STREAM_BUFFER

    buffer = deepcopy(STREAM_BUFFER)
    STREAM_BUFFER.clear()

    while True:
        try:
            data: bytes = conn.recv(MAX_BYTES)
        except Exception as e:
            return WukongPkg(err=f'{e.__class__, e.args}')
        if data == b'':
            return WukongPkg(closed=True)

        bye_index = data.find(delimiter)
        if bye_index == -1:
            buffer.append(data)
            continue

        buffer.append(data[:bye_index])
        if len(data) < bye_index + delimiter_len:
            STREAM_BUFFER.append(data[bye_index + delimiter_len:])
        break
    msg = b''.join(buffer).replace(delimiter_escape, delimiter)
    ret = WukongPkg(msg)
    return ret


def write_wukong_data(conn: socket.socket, msg: WukongPkg) -> (bool, str):
    """NOTE: Sending an empty string is allowed"""
    _bytes_msg = msg.raw_data.replace(delimiter, delimiter_escape) + delimiter
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
        will_send_data = _bytes_msg[sent_index:sent_index + MAX_BYTES]
        if not _send_msg(will_send_data):
            return False, err
        sent_index += MAX_BYTES

    return True, err


class TcpConn:
    def __init__(self):
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.err = None

    def write(self, data) -> bool:
        ok, self.err = write_wukong_data(self.skt, WukongPkg(data))
        return ok

    def read(self):
        return read_wukong_data(self.skt)

    def close(self):
        self.skt.close()


class TcpSvr(TcpConn):
    def __init__(self, host='127.0.0.1', port=9999, max_conns=1):
        super().__init__()
        self.skt.bind((host, port))
        self.max_conns = max_conns

    def accept(self):
        self.skt.listen(self.max_conns)
        return self.skt.accept()


class TcpClient(TcpConn):
    def __init__(self, host='127.0.0.1', port=9999, pre_connect=False):
        super().__init__()
        if not pre_connect:
            self.skt.connect((host, port))


QUEUE_PUT = b'PUT'
QUEUE_GET = b'GET'
QUEUE_DATA = b'DATA'
QUEUE_FULL = b'FULL'
QUEUE_EMPTY = b'EMPTY'
QUEUE_NORMAL = b'NORMAL'
QUEUE_QUERY_STATUS = b'STATUS'
QUEUE_OK = b'OK'
QUEUE_FAIL = b'FAIL'
QUEUE_PING = b'PING'
QUEUE_PONG = b'PONG'
QUEUE_SIZE = b'SIZE'
QUEUE_MAXSIZE = b'MAXSIZE'
QUEUE_RESET = b'RESET'
QUEUE_PARAMS = b'PARAMS'
QUEUE_CLIENTS = b'CLIENTS'
