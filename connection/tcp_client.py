import socket
import time


def send_file(addr, port, client_id):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # try:
    try:
        client.connect((addr, port))
        print('Start transmission...')
        client.send(f'CLIENT_ID_{client_id}\r\n'.encode())
        client.send("FILE_START\r\n".encode())
        with open('./weight.pt', 'rb') as f:  # file directory here
            time_start = time.time()
            while True:
                b = f.read(1024)
                if len(b) == 0:
                    break
                client.send(b)
            time_end = time.time()
        client.send("FILE_END\r\n".encode())
        print(f'Transmission finished within time {time_end - time_start}!')
    except Exception as e:
        print(e)
        print('Send file failed, retry in 10s')
    finally:
        client.close()


def send_acc(addr, port, client_id, acc):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    acc_str = ''
    for _ in acc:
        acc_str += ',{:.2f}'.format(_)
    acc_bytes = acc_str[1:].encode()
    try:
        client.connect((addr, port))
        print('Start transmission...')
        time_start = time.time()
        client.send(f'CLIENT_ID_{client_id}\r\n'.encode())
        client.send("ACC_START\r\n".encode())
        client.send(acc_bytes)
        client.send("ACC_END\r\n".encode())
        time_end = time.time()
        print(f'Transmission finished within time {time_end - time_start}!')
    except Exception as e:
        print(e)
        print('Send file failed, retry in 10s')
    finally:
        client.close()


def request_weight(addr, port, eps):
    received = False
    while not received:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((addr, port))
            client.send(f"REQUEST_WEIGHT_{eps}\r\n".encode())
            print(f"REQUEST_WEIGHT_{eps}")
            time_start = time.time()
            message = bytes()
            while True:
                data = client.recv(1024)
                message += data
                if message.startswith('WAIT\r\n'.encode()):
                    print("waiting...")
                    time.sleep(2)
                    break
                if message.startswith('FILE_START\r\n'.encode()):
                    message = message[len('FILE_START\r\n'.encode()):]
                    print('Start requesting...')
                if message.__contains__('FILE_END\r\n'.encode()):
                    file = message[:message.find("FILE_END\r\n".encode())]
                    message = message[message.find("FILE_END\r\n".encode()):]
                    with open('./weight.pt', 'wb') as f:  # file directory here
                        f.write(file)
                        f.flush()
                    received = True
                    time_end = time.time()
                    print(f'Transmission finished within time {time_end - time_start}!')
                    break
                if len(data) == 0:
                    break

        except Exception as e:
            print(e)
            print('Request failed, retry in 2 sec')
            time.sleep(2)
        finally:
            client.close()


def request_seq(addr, port):
    while True:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((addr, port))
            client.send(f"REQUEST_SEQ\r\n".encode())
            time_start = time.time()
            message = bytes()
            while True:
                data = client.recv(1024)
                message += data
                if message.startswith('SEQ_START\r\n'.encode()):
                    message = message[len('SEQ_START\r\n'.encode()):]
                if message.__contains__('SEQ_END\r\n'.encode()):
                    seq = message[:message.find("SEQ_END\r\n".encode())]
                    seq = seq.decode().split(',')
                    seq = [int(_) for _ in seq]
                    time_end = time.time()
                    print(f'Transmission finished within time {time_end - time_start}!')
                    return seq
                if len(data) == 0:
                    break
        except Exception as e:
            print(e)
            print('Request failed, retry in 10 sec')
            time.sleep(2)
        finally:
            client.close()


if __name__ == '__main__':
    print(request_seq('127.0.0.1', 10000))
    # send_file('127.0.0.1', 10000)
    # request_weight('127.0.0.1')
