"""
A small,convenient encapsulated TCP communication class.
"""

import socket, threading
from py_utils.util_tcp.commu_proto import read_wukong_data, write_wukong_data, WukongPkg

# const
recv_max_bytes_len = 1024


def new_thread(f, kw={}):
    t = threading.Thread(target=f, kwargs=kw)
    t.setDaemon(True)
    t.start()


class TcpSvr:
    def __init__(self, host='127.0.0.1', port=9999, max_conns=5):
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.skt.bind((host, port))
        self.max_conns = max_conns

    def listen(self):
        self.skt.listen(self.max_conns)

    def accept(self):
        return self.skt.accept()

    def close(self):
        self.skt.close()


# Customize a protocol to parse packages
class WuKongSvr:
    def __init__(self, host='127.0.0.1', port=9999, max_conns=5):
        self._tcp_skt = TcpSvr(host, port, max_conns)
        self._host = host
        self._port = port

    def run(self):
        self._tcp_skt.listen()
        print(f'tcp svr is listening to {self._host}:{self._port}')
        while True:
            conn, addr = self._tcp_skt.accept()
            print('new conn:', addr)
            new_thread(self.process_conn, kw={'conn': conn, 'addr': addr})

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._tcp_skt.close()

    @classmethod
    def process_conn(cls, conn: socket.socket, addr):
        """run as thread"""
        hi_msg = f"[svr] connected to server, your addr is {addr}"
        wukongpkg = WukongPkg(hi_msg)
        if not write_wukong_data(conn, wukongpkg):
            print(f'write_socket_data {addr} err')
            conn.close()
            return

        while True:
            try:
                recv_wukongpkg = read_wukong_data(conn)
            except Exception as e:
                print(f'conntion:{addr} closed, err:{e.__class__, e.args}!')
                conn.close()
                return
            cls.process_received_data_callback(conn, recv_wukongpkg)
            # add your callback here

    @classmethod
    def process_received_data_callback(cls, conn: socket.socket, recv_wukongpkg: WukongPkg):
        """customize your callback"""
        data = recv_wukongpkg.data
        print('recv:', data)
        wukongpkg = WukongPkg(data.decode())
        if not write_wukong_data(conn, wukongpkg):
            print(f'write_socket_data {conn.getpeername()} err')
            conn.close()
            return


if __name__ == '__main__':
    with WuKongSvr()as wk_svr:
        wk_svr.run()
