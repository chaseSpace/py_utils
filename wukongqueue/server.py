"""
A small and convenient cross process Queue service based on TCP protocol.
"""

import socket, threading
from typing import Union
from queue import Queue, Full, Empty
from py_utils.wukongqueue.commu_proto import *


def new_thread(f, kw={}):
    t = threading.Thread(target=f, kwargs=kw)
    t.setDaemon(True)
    t.start()


class WuKongQueue:
    """PUT or GET support bytes only."""

    def __init__(self, host='127.0.0.1', port=9999, max_conns=1, max_size=0):
        self._tcp_svr = TcpSvr(host, port, max_conns)
        self._host = host
        self._port = port
        self.q = Queue(max_size)
        new_thread(self._run)

    def _run(self):
        self._tcp_svr.listen()
        print(f'tcp svr is listening to {self._host}:{self._port}')
        while True:
            conn, addr = self._tcp_svr.accept()
            print('new conn:', addr)
            new_thread(self.process_conn, kw={'addr': addr, 'conn': conn})

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._tcp_svr.close()

    close = __exit__

    def get(self, block=True, timeout=None) -> Union[bytes, None]:
        """<get> will get item from queue, Block is unsupport so far.
            None returned means queue is empty.
        """
        return self.q.get(block=False, timeout=timeout)

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
        # hi_msg = f"[svr] connected to server, your addr is {addr}"
        # wukongpkg = WukongPkg(bytes(hi_msg, encoding='utf8'))
        # ok, err = write_wukong_data(conn, wukongpkg)
        # if not ok:
        #     print(f'write_socket_data {addr} err:{err}')
        #     conn.close()
        #     return

        while True:

            wukongpkg = read_wukong_data(conn)
            if wukongpkg.err:
                print(f'conntion:{addr} closed, err:{wukongpkg.err}!')
                conn.close()
                return

            data = wukongpkg.data
            # GET
            if self._expected_cmd(data, QUEUE_GET):
                item = self.get()
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
                    print('push:', _bytes_data)
                else:
                    write_wukong_data(conn, WukongPkg(QUEUE_FULL))
                    print('push:', _bytes_data, 'FULL')
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

            print('Unsupport cmd:', data)

    @staticmethod
    def _expected_cmd(data: bytes, qcmd) -> bool:
        return data.startswith(qcmd)


if __name__ == '__main__':
    with WuKongQueue(max_size=3)as wk_queue:
        import time

        time.sleep(111)
