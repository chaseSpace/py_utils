import socket, traceback
from py_utils.util_tcp.commu_proto import read_wukong_data, write_wukong_data, WukongPkg


class TcpClient:
    def __init__(self, host, port):
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.skt.connect((host, port))
            wkpkg = read_wukong_data(self.skt)
            print('[client] hello msg:', wkpkg.data)
        except:
            traceback.print_exc()
            return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.skt.close()


if __name__ == '__main__':
    import string
    with TcpClient('127.0.0.1', 9999)as client:
        while True:
            # send_str = input('client input:')
            send_str = ''
            send_wkpkg = WukongPkg(send_str)
            if not write_wukong_data(client.skt, send_wkpkg):
                print(f'write_socket_data {client.skt.getpeername()} err')
                break
            recv_wkpkg = read_wukong_data(client.skt)
            print(f'[client] recv:', recv_wkpkg, '\n')
