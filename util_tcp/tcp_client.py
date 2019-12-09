import socket, traceback
from py_utils.util_tcp.commu_proto import read_socket_data, write_socket_data


class TcpClient:
    def __init__(self, host, port):
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.skt.connect((host, port))
            data = read_socket_data(self.skt)
            print('[client] hello msg:', data)
        except:
            traceback.print_exc()
            return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.skt.close()


if __name__ == '__main__':

    with TcpClient('127.0.0.1', 9999)as client:
        while True:
            send_str = input('client input:')

            if not write_socket_data(client.skt, send_str):
                print(f'write_socket_data {client.skt.getpeername()} err')
                break
            data = read_socket_data(client.skt)
            print(f'[client] recv:', data, '\n')
