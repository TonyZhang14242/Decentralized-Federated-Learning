import socket
import time

class TCPServer:
    def acceptFromServer(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("0.0.0.0",10000))
        server.listen(10000)
        print('start listening...')
        while True:
            soc, addr = server.accept()
            message = ''.encode()
            print('Start transmission...')
            time_start = time.time()
            try:
                while True:
                    data = soc.recv(1024)
                    if len(data) == 0:
                        break
                    message += data
                    with open('./001.png','wb') as f: #file directory here
                        f.write(message)
                        f.flush()
                    f.close()
                time_end = time.time()
                print(f'Transmission finished within time {time_end - time_start}!')   
            except:
                print('error occurred!')
            soc.close()
            print('file received!')
        server.close()

    def get_connection(self):
            soc, addr = server.accept()
            message = ''.encode()
            print('Start transmission...')
            time_start = time.time()
            try:
                while True:
                    data = soc.recv(1024)
                    if len(data) == 0:
                        break
                    message += data
                    with open('./001.png','wb') as f: #file directory here
                        f.write(message)
                        f.flush()
                    f.close()
                time_end = time.time()
                print(f'Transmission finished within time {time_end - time_start}!')   
            except:
                print('error occurred!')
            soc.close()
            print('file received!')

if __name__ == '__main__':
    TCPServer.acceptFromServer()