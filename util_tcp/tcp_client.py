import socket, traceback

# const
recv_max_bytes_len = 1024


class TcpClient:
    def __init__(self, host, port):
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.skt.connect((host, port))
            data = self.skt.recv(recv_max_bytes_len)
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
            # convert to bytes
            sent_bytes = client.skt.send(send_str.encode())
            data = client.skt.recv(recv_max_bytes_len)
            print(f'[client] recv:', data, '\n')
