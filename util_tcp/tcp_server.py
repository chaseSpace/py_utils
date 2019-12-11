"""
A small,convenient encapsulated TCP communication class.
"""

import socket, threading
from queue import Queue, Full, Empty
from py_utils.util_tcp.commu_proto import *

"""
WuKong, Simple across-process queue communication protocol Based TCP.
"""

# const
recv_max_bytes_len = 1024


def new_thread(f, kw={}):
    t = threading.Thread(target=f, kwargs=kw)
    t.setDaemon(True)
    t.start()


# Customize a protocol to parse packages
class WuKongQueue:
    """PUT or GET support bytes only."""

    def __init__(self, host='127.0.0.1', port=9999, max_conns=1, max_size=0):
        self._tcp_svr = TcpSvr(host, port, max_conns)
        self._host = host
        self._port = port
        self.q = Queue(max_size)
        new_thread(self._run, )

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

    def _get(self):
        try:
            item = self.q.get(block=False)
            return item
        except Empty:
            return

    def _put(self, item) -> bool:
        try:
            self.q.put(item, block=False)
            return True
        except Full:
            return False

    def process_conn(self, addr, conn: socket.socket):
        """run as thread"""
        hi_msg = f"[svr] connected to server, your addr is {addr}"
        wukongpkg = WukongPkg(bytes(hi_msg, encoding='utf8'))
        ok, err = write_wukong_data(conn, wukongpkg)
        if not ok:
            print(f'write_socket_data {addr} err:{err}')
            conn.close()
            return

        while True:

            wukongpkg = read_wukong_data(conn)
            if wukongpkg.err:
                print(f'conntion:{addr} closed, err:{wukongpkg.err}!')
                conn.close()
                return

            data = wukongpkg.data
            # GET
            if self._is_get_cmd(data):
                item = self._get()
                if item is None:
                    write_wukong_data(conn, WukongPkg(QUEUE_EMPTY))
                else:
                    write_wukong_data(conn, WukongPkg(QUEUE_HAVA_DATA + item))
                continue
            # PUT
            is_put, _bytes_data = self._is_put_cmd(data)
            if is_put:
                if self._put(_bytes_data):
                    write_wukong_data(conn, WukongPkg(QUEUE_OK))
                else:
                    write_wukong_data(conn, WukongPkg(QUEUE_FAIL))
                print('push:', _bytes_data)
                continue

            if self._is_query_status_cmd(data):
                # FULL | EMPTY
                if self.q.full():
                    write_wukong_data(conn, WukongPkg(QUEUE_FULL))
                elif self.q.empty():
                    write_wukong_data(conn, WukongPkg(QUEUE_EMPTY))
                else:
                    write_wukong_data(conn, WukongPkg(QUEUE_STATUS_NONE))
                continue

            if self._is_ping(data):
                write_wukong_data(conn, WukongPkg(QUEUE_PONG))
                continue
            print('Unsupport cmd:', data)

    @staticmethod
    def _is_put_cmd(data: bytes) -> (bool, bytes):
        if data.startswith(QUEUE_PUT):
            return True, data.lstrip(QUEUE_PUT)
        return False, None

    @staticmethod
    def _is_get_cmd(data: bytes) -> bool:
        return data.startswith(QUEUE_GET)

    @staticmethod
    def _is_query_status_cmd(data: bytes) -> bool:
        return data.startswith(QUEUE_QUERY_STATUS)

    @staticmethod
    def _is_ping(data: bytes) -> bool:
        return data.startswith(QUEUE_PING)


if __name__ == '__main__':
    with WuKongQueue()as wk_queue:
        import time

        time.sleep(111)
