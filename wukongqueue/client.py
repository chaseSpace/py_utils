from py_utils.wukongqueue.commu_proto import *


class Empty(Exception):
    pass


class Full(Exception):
    pass


class WuKongQueueClient:
    def __init__(self, host, port):
        self.addr = [host, port]
        self._tcp_client = TcpClient(host, port)

    def put(self, data: bytes) -> bool:
        send_data = QUEUE_PUT + data
        self._tcp_client.write(send_data)
        recv_data = self._tcp_client.read()
        if recv_data == QUEUE_OK:
            return True
        elif recv_data == QUEUE_FULL:
            raise Full(f'WuKongQueue Svr-addr:{self.addr} is full')
        return False

    def get(self) -> bytes:
        send_data = QUEUE_GET
        self._tcp_client.write(send_data)
        recv_data = self._tcp_client.read()
        if recv_data == QUEUE_EMPTY:
            raise Empty(f'WuKongQueue Svr-addr:{self.addr} is empty')
        return recv_data.lstrip(QUEUE_DATA)

    def is_full(self) -> bool:
        self._tcp_client.write(QUEUE_QUERY_STATUS)
        return self._tcp_client.read() == QUEUE_FULL

    def is_empty(self) -> bool:
        self._tcp_client.write(QUEUE_QUERY_STATUS)
        return self._tcp_client.read() == QUEUE_EMPTY

    def connected(self) -> bool:
        self._tcp_client.write(QUEUE_PING)
        return self._tcp_client.read() == QUEUE_PONG

    def realtime_qsize(self) -> int:
        self._tcp_client.write(QUEUE_SIZE)
        recv_data = self._tcp_client.read()
        return int(recv_data.lstrip(QUEUE_SIZE).decode())

    def realtime_maxsize(self):
        self._tcp_client.write(QUEUE_MAXSIZE)
        recv_data = self._tcp_client.read()
        return int(recv_data.lstrip(QUEUE_MAXSIZE).decode())

    def reset(self, max_size=0) -> bool:
        self._tcp_client.write(QUEUE_RESET + str(max_size).encode())
        recv_data = self._tcp_client.read()
        return recv_data == QUEUE_OK

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
        print('empty', client.is_empty())
        print('full', client.is_full())

        print(client.realtime_maxsize())
        print('reset', client.reset(6))
        print(client.realtime_maxsize())
