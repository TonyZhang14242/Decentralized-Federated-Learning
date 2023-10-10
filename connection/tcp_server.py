import socket
import time
import asyncio
from asyncio import StreamReader, StreamWriter
import numpy as np

eps = 0
received_clients = np.zeros(1)
bk = '\r\n'.encode()


def inc_eps():
    global eps, received_clients
    print(f'Epoch {eps} finish')
    eps += 1
    received_clients = np.zeros(received_clients.size)


def get_received_numbers():
    global received_clients
    return np.sum(received_clients)


async def handle(reader: StreamReader, writer: StreamWriter):
    print('connection accepted')
    message = bytes()
    time_start = time.time()
    recv_file = False
    client_id = -1
    while True:
        data = await reader.read(1024)
        message += data
        if recv_file:
            if message.__contains__('FILE_END\r\n'.encode()):
                print(f'Received weight of client {client_id}')
                file = message[:message.find("FILE_END\r\n".encode())]
                with open(f'./clients/client_{client_id}.pt', 'wb') as f:  # file directory here
                    f.write(file)
                    f.flush()
                received_clients[client_id] = 1
                break
            else:
                continue
        if message.startswith('CLIENT_ID_'.encode()):
            message = message[len('CLIENT_ID_'.encode()):]
            client_id = int(message[:message.find(bk)])
            message = message[message.find(bk) + len(bk):]
        if message.startswith('FILE_START\r\n'.encode()):
            message = message[len('FILE_START\r\n'.encode()):]
            recv_file = True
        if message.startswith('REQUEST_WEIGHT_'.encode()):
            message = message[len('REQUEST_WEIGHT_'.encode()):]
            requesting = int(message[:message.find('\r\n'.encode())])
            if requesting <= eps:
                print('sending weights')
                writer.write("FILE_START\r\n".encode())
                with open('./clients/avg.pt', 'rb') as f:  # file directory here
                    print('file open')
                    while True:
                        b = f.read(1024)
                        if len(b) == 0:
                            break
                        writer.write(b)
                writer.write("FILE_END\r\n".encode())
            else:
                writer.write('WAIT\r\n'.encode())
            await writer.drain()
            writer.close()
            break
        if len(data) == 0:
            break
    time_end = time.time()
    print(f'connection closed within time {time_end - time_start}!')


async def listen(client_num):
    global received_clients
    server = await asyncio.start_server(
        handle, '0.0.0.0', 10000)
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    received_clients = np.zeros(client_num)
    print(f'Serving on {addrs}')
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(listen(1))
