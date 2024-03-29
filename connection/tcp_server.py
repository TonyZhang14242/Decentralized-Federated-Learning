import random
import socket
import time
import asyncio
from asyncio import StreamReader, StreamWriter
import numpy as np

eps = 0
received_clients = np.zeros(1)
bk = '\r\n'.encode()
seq = ''
acc_list_all = []


def inc_eps():
    global eps, received_clients
    print(f'Epoch {eps} finish')
    eps += 1
    received_clients = np.zeros(received_clients.size)


def get_received_numbers():
    global received_clients
    return np.sum(received_clients)


def set_seq(seq_str):
    global seq
    seq = seq_str


async def handle(reader: StreamReader, writer: StreamWriter):
    rng = random.randint(10, 99)
    # print(f'{rng}: connection accepted')
    # loop = asyncio.get_running_loop()
    time_start = time.time()
    global acc_list_all
    message = bytes()
    recv_file = False
    recv_acc = False
    client_id = -1
    while True:
        data = await reader.read(1024)
        message += data
        if recv_file:
            if message.__contains__('FILE_END\r\n'.encode()):
                with open('./received.txt', "a") as f:
                    f.write(f'Received weight of client {client_id}\n')
                file = message[:message.find("FILE_END\r\n".encode())]
                with open(f'./clients/client_{client_id}.pt', 'wb') as f:  # file directory here
                    f.write(file)
                    f.flush()
                received_clients[client_id] = 1
                # print(received_clients)
                break
            else:
                continue
        if recv_acc:
            if message.__contains__('ACC_END\r\n'.encode()):
                print(f'Received accuracy of client {client_id}')
                acc_list = message[:message.find("ACC_END\r\n".encode())]
                acc_list = acc_list.decode().split(',')
                acc_list = [float(_) for _ in acc_list]
                acc_list_all.append({'client': client_id, 'acc': acc_list})
                break
            else:
                continue
        if message.startswith('CLIENT_ID_'.encode()):
            # print(rng, message)
            message = message[len('CLIENT_ID_'.encode()):]
            client_id = int(message[:message.find(bk)])
            message = message[message.find(bk) + len(bk):]
        if message.startswith('FILE_START\r\n'.encode()):
            # print(rng, message)
            message = message[len('FILE_START\r\n'.encode()):]
            recv_file = True
        if message.startswith('ACC_START\r\n'.encode()):
            # print(rng, message)
            message = message[len('ACC_START\r\n'.encode()):]
            # print(rng, message)
            recv_acc = True
        if message.startswith('REQUEST_SEQ'.encode()):
            # print(rng, message)
            message = message[len('REQUEST_SEQ'.encode()):]
            writer.write("SEQ_START\r\n".encode())
            writer.write(seq.encode())
            writer.write("SEQ_END\r\n".encode())
            await writer.drain()
            writer.close()
            break
        if message.startswith('REQUEST_WEIGHT_'.encode()):
            # print(rng, message)
            message = message[len('REQUEST_WEIGHT_'.encode()):]
            requesting = int(message[:message.find('\r\n'.encode())])
            if requesting <= eps:
                # print('sending weights')
                writer.write("FILE_START\r\n".encode())
                with open('./clients/avg.pt', 'rb') as f:  # file directory here
                    while True:
                        b = f.read(1024)
                        if len(b) == 0:
                            break
                        writer.write(b)
                writer.write("FILE_END\r\n".encode())
            else:
                writer.write('WAIT\r\n'.encode())
                # print(f'Requesting {requesting} but eps is {eps}, send WAIT')
            await writer.drain()
            writer.close()
            break
        if len(data) == 0:
            break
    # time_end = time.time()
    # print(f'{rng}: connection closed')


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
