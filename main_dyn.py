import random

import torch

import main_distribute
from utils.options import args_parser
import blue_client
import blue_server
import os
import time


def pick_client_random(clients, weight):
    return random.choice(clients)


def weighted_rand(weights):
    r = random.random()
    print(r)
    accu = 0
    for i, w in enumerate(weights):
        if accu < r < accu + w:
            return i
        accu += w
    return len(weights) - 1

def pick_client_weighted(clients, weights):
    id = weighted_rand(weights)
    print(id)
    decrease_weight(weights, id, args.reduce_rate)
    return clients[id]


def decrease_weight(weight, id, mul):
    if len(weight) == 1:
        return
    add = weight[id] * mul / (len(weight) - 1)
    weight[id] *= (1 - mul)
    for i in range(len(weight)):
        if i != id:
            weight[i] += add


if __name__ == '__main__':
    args = args_parser()
    args.num_channels = 1
    args.model = 'cnn'
    blue_file = f'./blue_config/{args.topology}.txt'
    pick_method = pick_client_random
    if args.pick == 'weighted':
        pick_method = pick_client_weighted
    if not os.path.exists(blue_file):
        print('Topology file not exist')
        exit()
    with open(blue_file, 'r', encoding=args.encoding) as f:
        blue_address = f.readlines()
    for i in range(len(blue_address)):
        blue_address[i] = blue_address[i].strip()
    blue_weight = [1 / len(blue_address)] * len(blue_address)
    server = blue_server.BluetoothConnection()
    client = blue_client.BluetoothConnection()
    fed = main_distribute.FedClient(args)
    start_time = time.time()
    local_iter = 0
    if args.client_no == 0:
        fed_data = {'w': torch.load('weight.pt'), 'time': start_time, 'path': []}
        peer = {'start': start_time, 'id': args.client_no}
        fed_data['w'], peer['loss'] = fed.iter(local_iter, fed_data['w'])
        peer['end'] = time.time()
        fed_data['path'].append(peer)
        torch.save(fed_data, 'weight.pt')
        local_iter += 1
        print(f'Weight: {blue_weight}')
        send_addr = pick_method(blue_address, blue_weight).strip()
        print(f'Trying to send model to {send_addr}')
        try:
            client.send_message_to_target(send_addr)  # send
        except:
            pass
    else:
        fed_data = {'w': None, 'time': start_time, 'path': []}
        torch.save(fed_data, 'weight.pt')
    while time.time() - start_time < args.time:
        from_addr = server.get_connection(start_time, args.time)  # receive and wait
        if time.time() - start_time > args.time:
            break
        print(type(from_addr))
        print(f'Trying to reduce weight from {from_addr}')
        if args.pick == 'weighted':
            if blue_address.__contains__(from_addr):
                decrease_weight(blue_weight, blue_address.index(from_addr), args.reduce_rate)
            else:
                print('Cannot find address weight to decrease')
        peer = {'start': time.time(), 'id': args.client_no}
        print('reading weights')
        fed_data = torch.load('weight.pt')
        start_time = fed_data['time']
        fed_data['w'], peer['loss'] = fed.iter(local_iter, fed_data['w'])  # train
        peer['end'] = time.time()
        fed_data['path'].append(peer)
        torch.save(fed_data, 'weight.pt')
        local_iter += 1
        print(f'Weight: {blue_weight}')
        send_addr = pick_method(blue_address, blue_weight).strip()
        print(f'Trying to send model to {send_addr}')
        try:
            client.send_message_to_target(send_addr)  # send
        except:
            pass
    train_acc, test_acc = fed.test()
    with open(f'./save/peer_{args.client_no}_time{args.time}_{args.pick}_{args.topology}.txt', 'w') as f:
        f.write(f'Train acc: {train_acc}\n')
        f.write(f'Test acc: {test_acc}\n')
        for peer in torch.load('weight.pt')['path']:
            f.write(str(peer) + '\n')
    if args.plot:
        fed.plot_loss()
