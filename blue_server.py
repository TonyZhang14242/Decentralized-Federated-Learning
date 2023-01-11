import bluetooth
import time
import base64


class BluetoothConnection:

    def __init__(self):
        self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.server_sock.bind(('', 1))
        self.server_sock.listen(1)

    def get_connection(self, start=2673120403.0, timeout=50000):
        print('Start listening to connection query.......')
        self.server_sock.settimeout(start + timeout - time.time())
        try:
            client_sock, address = self.server_sock.accept()
        except:
            print('Bluetooth receive timeout')
            return None
        print("Accepted connection from ", address)
        message = b''
        try:
            while True:
                time.sleep(0.1)
                data = client_sock.recv(1024)
                # print(data)
                message += data
                # print(data)

                # time.sleep(1)
                # img_data = message
        except:
            pass
        if time.time() - start < timeout:
            with open('weight.pt', 'wb') as f:
                f.write(message)
                f.flush()
            f.close()
        client_sock.close()
        return address[0]

    def createService(self, way=bluetooth.RFCOMM):
        server_sock = bluetooth.BluetoothSocket(way)
        server_sock.bind(('', 1))
        server_sock.listen(1)
        while True:
            print('Start listening to connection query.......')
            client_sock, address = server_sock.accept()
            print("Accepted connection from ", address)
            message = ''.encode()
            try:
                while True:
                    time.sleep(0.1)
                    data = client_sock.recv(1024)
                    # print(data)
                    message += data
                    # print(data)

                    # time.sleep(1)
                    # img_data = message
                    with open('001.png', 'wb') as f:
                        f.write(message)
                        f.flush()
                    f.close()
            except:
                pass
            client_sock.close()


if __name__ == '__main__':
    BluetoothConnection().createService()
