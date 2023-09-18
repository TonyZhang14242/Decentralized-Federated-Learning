import socket
import os
import time


class TCPClient:
    def connectToHost(self, addr):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((addr, 8990))
            with open('../CVLab/Assignment3/SIFT_KNN.png', 'rb') as f: #file directory here
                print('Start transmission...')
                time_start = time.time()
                while True:
                    b = f.read(1024)
                    if len(b) == 0:
                        break
                    client.send(b)
                time_end = time.time()
                print(f'Transmission finished within time {time_end - time_start}!')    
            client.close()
        except:
            print(f'Cannot connect to host {addr}')

    def send_message_to_target(self, addr):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((addr, 8990))
            with open('../CVLab/Assignment3/SIFT_KNN.png', 'rb') as f: #file directory here
                print('Start transmission...')
                time_start = time.time()
                while True:
                    b = f.read(1024)
                    if len(b) == 0:
                        break
                    client.send(b)
                time_end = time.time()
                print(f'Transmission finished within time {time_end - time_start}!')    
            client.close()
        except:
            print(f'Cannot connect to host {addr}')



if __name__ == '__main__':
    TCPClient.connectToHost('172.18.36.132')
    