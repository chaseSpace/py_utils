"""
A small and convenient cross process Queue service based on TCP protocol.
"""

import socket
import sys
import threading
from queue import Queue, Full
from types import FunctionType
from typing import Union

sys.path.append('../../')
from py_utils.wukongqueue.commu_proto import *


def new_thread(f, kw={}):
    t = threading.Thread(target=f, kwargs=kw)
    t.setDaemon(True)
    t.start()


class _helper:
    def __init__(self, inst):
        self.inst: WuKongQueue = inst

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.inst.__exit__(exc_type, exc_val, exc_tb)


class _wk_svr_helper:
    def __init__(self, wk_inst):
        self.wk_inst = wk_inst

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self.wk_inst.lock:
            self.wk_inst.clients -= 1


class WuKongQueue:
    """PUT or GET support bytes only."""

    def __init__(self, host='127.0.0.1', port=918, *, name='', max_conns=1, max_size=0):
        self.name = name
        self._tcp_svr = TcpSvr(host, port, max_conns)
        self._host = host
        self._port = port
        self.clients = 0
        self.lock = threading.Lock()
        self.q = Queue(max_size)
        new_thread(self._run)

    def _run(self):
        print(
            f'WuKongQueue [{self.name if self.name else "unknown"}] service is listening to {self._host}:{self._port}')
        while True:
            conn, addr = self._tcp_svr.accept()
            print('new conn:', addr)
            new_thread(self.process_conn, kw={'addr': addr, 'conn': conn})
            with self.lock:
                self.clients += 1

    def close(self):
        self._tcp_svr.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def helper(self):
        return _helper(self)

    def get(self, block=True, timeout=None, convert_method: FunctionType = None) -> Union[bytes, None]:
        """
        :param block: see also stdlib `queue.Queue.get` usage.
        :param timeout: see also stdlib `queue.Queue.get` usage.
        :param convert_method: function
        :return:
        """
        item = self.q.get(block=block, timeout=timeout)
        return convert_method(item) if convert_method else item

    def put(self, item: bytes) -> bool:
        try:
            self.q.put_nowait(item)
            return True
        except Full:
            return False

    def reset(self, max_size=0):
        del self.q
        self.q = Queue(max_size)

    def process_conn(self, addr, conn: socket.socket):
        """run as thread"""
        with _wk_svr_helper(self):
            while True:
                wukongpkg = read_wukong_data(conn)
                if not wukongpkg.is_valid():
                    print(f'connection:{addr} closed, err:{wukongpkg.err}!')
                    conn.close()
                    return

                data = wukongpkg.raw_data
                # GET
                if self._expected_cmd(data, QUEUE_GET):
                    item = self.get()  # TODO: support params transmit

                    if item is None:
                        write_wukong_data(conn, WukongPkg(QUEUE_EMPTY))
                    else:
                        write_wukong_data(conn, WukongPkg(QUEUE_DATA + item))
                    continue

                # PUT
                if self._expected_cmd(data, QUEUE_PUT):
                    _bytes_data = data.lstrip(QUEUE_PUT)
                    if self.put(_bytes_data):
                        write_wukong_data(conn, WukongPkg(QUEUE_OK))
                        # print('push:', _bytes_data)
                    else:
                        write_wukong_data(conn, WukongPkg(QUEUE_FULL))
                        # print('push:', _bytes_data, 'FULL')
                    continue

                # STATUS QUERY
                if self._expected_cmd(data, QUEUE_QUERY_STATUS):
                    # FULL | EMPTY | NORMAL
                    if self.q.full():
                        write_wukong_data(conn, WukongPkg(QUEUE_FULL))
                    elif self.q.empty():
                        write_wukong_data(conn, WukongPkg(QUEUE_EMPTY))
                    else:
                        write_wukong_data(conn, WukongPkg(QUEUE_NORMAL))
                    continue

                # PING -> PONG
                if self._expected_cmd(data, QUEUE_PING):
                    write_wukong_data(conn, WukongPkg(QUEUE_PONG))
                    continue

                # QSIZE
                if self._expected_cmd(data, QUEUE_SIZE):
                    write_wukong_data(conn, WukongPkg(str(self.q.qsize()).encode()))
                    continue

                # MAXSIZE
                if self._expected_cmd(data, QUEUE_MAXSIZE):
                    write_wukong_data(conn, WukongPkg(str(self.q.maxsize).encode()))
                    continue

                # RESET
                if self._expected_cmd(data, QUEUE_RESET):
                    max_size = int(data.lstrip(QUEUE_RESET).decode())
                    self.reset(max_size)
                    write_wukong_data(conn, WukongPkg(QUEUE_OK))
                    continue

                # CLIENTS NUMBER
                if self._expected_cmd(data, QUEUE_CLIENTS):
                    write_wukong_data(conn, WukongPkg(QUEUE_CLIENTS + str(self.clients).encode()))
                    continue
                print('Unsupport cmd:', data)

    @staticmethod
    def _expected_cmd(data: bytes, qcmd) -> bool:
        return data.startswith(qcmd)


if __name__ == '__main__':
    with WuKongQueue(max_size=3)as wk_queue:
        import time

        time.sleep(111)
