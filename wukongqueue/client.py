import sys
from typing import Union, AnyStr

sys.path.append('../../')
from py_utils.wukongqueue.commu_proto import *

__all__ = ['WukongPkg', 'Empty', 'Full', 'WuKongQueueClient']


class Empty(Exception):
    pass


class Full(Exception):
    pass


class _helper:
    def __init__(self, inst):
        self.inst: WuKongQueueClient = inst

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.inst.__exit__(exc_type, exc_val, exc_tb)


class WuKongQueueClient:
    def __init__(self, host, port, *, auto_reconnect=False, pre_connect=False):
        """
        :param host: ...
        :param port: ...
        :param auto_reconnect: do reconnect when conn is disconnected, instead of `raise` an exception.
        :param pre_connect: By default, the class raises an exception when it fails to initialize connection,
                if `pre_conn` is true, you can success to initialize client although server is
                not ready yet.
        """
        self.addr = (host, port)
        self._tcp_client = TcpClient(*self.addr, pre_connect=pre_connect)
        self._try_recover = auto_reconnect

    def put(self, data: Union[str, bytes], encoding='utf8') -> bool:
        self._check_if_need_reconnect()
        if isinstance(data, str):
            data = data.encode(encoding=encoding)

        self._tcp_client.write(QUEUE_PUT + data)
        wukong_pkg = self._tcp_client.read()
        if not wukong_pkg.is_valid():
            return False
        if wukong_pkg.raw_data == QUEUE_OK:
            return True
        elif wukong_pkg.raw_data == QUEUE_FULL:
            raise Full(f'WuKongQueue Svr-addr:{self.addr} is full')
        return False

    def get(self, convert_method=None) -> Union[bytes, AnyStr, None]:
        """
        :param convert_method: function
        NOTE: the method will return None immediately when socket
        conn was normally closed.
        """
        self._check_if_need_reconnect()

        send_data = QUEUE_GET
        self._tcp_client.write(send_data)
        wukong_pkg = self._tcp_client.read()
        if not wukong_pkg.is_valid():
            return
        if wukong_pkg.raw_data == QUEUE_EMPTY:
            raise Empty(f'WuKongQueue Svr-addr:{self.addr} is empty')

        _bytes = wukong_pkg.raw_data.lstrip(QUEUE_DATA)
        if convert_method:
            return convert_method(_bytes)
        return _bytes

    def is_full(self) -> bool:
        self._tcp_client.write(QUEUE_QUERY_STATUS)
        wukong_pkg = self._tcp_client.read()
        if not wukong_pkg.is_valid():
            return False
        return wukong_pkg.raw_data == QUEUE_FULL

    def is_empty(self) -> bool:
        self._tcp_client.write(QUEUE_QUERY_STATUS)
        wukong_pkg = self._tcp_client.read()
        if not wukong_pkg.is_valid():
            return True
        return wukong_pkg.raw_data == QUEUE_EMPTY

    def connected(self) -> bool:
        self._tcp_client.write(QUEUE_PING)
        wukong_pkg = self._tcp_client.read()
        if not wukong_pkg.is_valid():
            return False
        return wukong_pkg.raw_data == QUEUE_PONG

    def realtime_qsize(self) -> int:
        self._tcp_client.write(QUEUE_SIZE)
        wukong_pkg = self._tcp_client.read()
        if not wukong_pkg.is_valid():
            return 0
        return int(wukong_pkg.raw_data.lstrip(QUEUE_SIZE).decode())

    def realtime_maxsize(self) -> int:
        self._tcp_client.write(QUEUE_MAXSIZE)
        wukong_pkg = self._tcp_client.read()
        if not wukong_pkg.is_valid():
            return 0
        return int(wukong_pkg.raw_data.lstrip(QUEUE_MAXSIZE).decode())

    def reset(self, max_size=0) -> bool:
        self._tcp_client.write(QUEUE_RESET + str(max_size).encode())
        wukong_pkg = self._tcp_client.read()
        if not wukong_pkg.is_valid():
            return False
        return wukong_pkg.raw_data == QUEUE_OK

    def connected_clients(self) -> int:
        self._tcp_client.write(QUEUE_CLIENTS)
        wukong_pkg = self._tcp_client.read()
        if not wukong_pkg.is_valid():
            return 0
        return int(wukong_pkg.raw_data.lstrip(QUEUE_CLIENTS).decode())

    def close(self):
        self._tcp_client.close()

    def _check_if_need_reconnect(self):
        if self._try_recover:
            if not self.connected():
                try:
                    self._tcp_client = TcpClient(*self.addr)
                    print(f'reconnect succ!')
                except Exception as e:
                    print(f'_check_if_need_recover fail: {e.__class__, e.args}')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def helper(self):
        return _helper(self)


if __name__ == '__main__':
    import time

    with WuKongQueueClient('127.0.0.1', 918, auto_reconnect=True)as client:
        # send_str = input('client input:')

        for i in range(11):
            time.sleep(2)
            print(client.connected())
            print(client.connected_clients())
            client.put('1')
        # print('empty', client.is_empty())
        # print('full', client.is_full())
        # 
        # print(client.realtime_maxsize())
        # print('reset', client.reset(6))
        # print(client.realtime_maxsize())
