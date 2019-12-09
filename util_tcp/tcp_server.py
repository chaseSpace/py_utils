"""
A small,convenient encapsulated TCP communication class.
"""

import socket, threading
from py_utils.util_tcp.commu_proto import read_socket_data, write_socket_data

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

    @classmethod
    def process_conn(cls, conn: socket.socket, addr):
        """run as thread"""
        hi_msg = f"[svr] connected to server, your addr is {addr}"
        if not write_socket_data(conn, hi_msg):
            print(f'write_socket_data {addr} err')
            conn.close()
            return

        while True:
            try:
                data = read_socket_data(conn)
            except Exception as e:
                print(f'conntion:{addr} closed, err:{e.__class__, e.args}!')
                conn.close()
                return
            cls.process_data(conn, data)

    @classmethod
    def process_data(cls, conn: socket.socket, data):
        if data:
            if isinstance(data, bytes):
                data = data.decode()
            if not write_socket_data(conn, data):
                print(f'write_socket_data {conn.getpeername()} err')
                conn.close()
                return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.skt.close()


if __name__ == '__main__':
    with TcpSvr()as tcp_svr:
        tcp_svr.listen()
        print('tcp svr is listening to localhost:9999')
        while True:
            conn, addr = tcp_svr.accept()
            print('new conn:', addr)
            new_thread(tcp_svr.process_conn, kw={'conn': conn, 'addr': addr})
