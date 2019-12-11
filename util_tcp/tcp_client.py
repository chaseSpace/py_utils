import socket, traceback
from py_utils.util_tcp.commu_proto import *


class Empty(Exception):
    pass


class WuKongQueueClient:
    def __init__(self, host, port):
        self.addr = [host, port]
        self._tcp_client = TcpClient(host, port)
        data = self._tcp_client.read()
        print('[client] hello msg:', data)

    def put(self, data: bytes) -> bool:
        send_data = QUEUE_PUT + data
        self._tcp_client.write(send_data)
        return self._tcp_client.read() == QUEUE_OK

    def get(self) -> bytes:
        send_data = QUEUE_GET
        self._tcp_client.write(send_data)
        recv_data = self._tcp_client.read()
        if recv_data == QUEUE_EMPTY:
            raise Empty(f'WuKongQueue svr-addr:{self.addr} is empty')
        return recv_data.lstrip(QUEUE_HAVA_DATA)

    def is_full(self) -> bool:
        self._tcp_client.write(QUEUE_QUERY_STATUS)
        return self._tcp_client.read() == QUEUE_FULL

    def is_empty(self) -> bool:
        self._tcp_client.write(QUEUE_QUERY_STATUS)
        return self._tcp_client.read() == QUEUE_EMPTY

    def connected(self) -> bool:
        self._tcp_client.write(QUEUE_PING)
        return self._tcp_client.read() == QUEUE_PONG

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._tcp_client.close()

    close = __exit__


if __name__ == '__main__':
    import string
    import time

    with WuKongQueueClient('127.0.0.1', 9999)as client:
        # send_str = input('client input:')
        print(client.connected())
        for i in range(11):
            print(client.put(i.to_bytes(length=2, byteorder='big')), i)
        time.sleep(1)
        print(client.get())
        print(client.get())
        i = client.get()
        print(int.from_bytes(i, byteorder='big'))
        for i in range(10):
            i = client.get()
            if i is not None:
                print(int.from_bytes(i, byteorder='big'))
