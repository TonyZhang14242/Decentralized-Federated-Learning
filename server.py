import datetime
import time
import os

import numpy as np
import torch
import asyncio
from utils.server_options import args_parser
from connection.tcp_server import listen, inc_eps, get_received_numbers, acc_list_all
from models.Fed import FedAvg
from models.Nets import CNNMnist, MLP
from models.test import test_img
from torchvision import datasets, transforms
from models.datasets import SimpleData
import matplotlib.pyplot as plt


async def main(cur_loop):
    global net
    global datasets_test
    global acc_list_all
    now = datetime.datetime.now()
    start_time = time.time()
    listen_task = cur_loop.create_task(listen(args.clients))
    # ping_task = cur_loop.create_task(ping())
    # await cur_loop.run_in_executor(None, slow_task)
    acc = []
    with open('seq.txt') as f:
        seq_str = f.read()
        seq_str = seq_str.split(',')
        seq = [int(_) for _ in seq_str]
        print("Sequence: ", seq)
    cid = 0
    while True:
        await asyncio.sleep(1)
        # time.sleep(1)
        if get_received_numbers() == args.clients:
            w = await cur_loop.run_in_executor(None, client_avg)
            net.load_state_dict(w)
            print(f"testing in current concept: {seq[cid]}")
            acc_test_cur, loss_test_cur = await cur_loop.run_in_executor(None, test_img, net,
                                                                         datasets_test[seq[cid]], args)
            # acc_test_cur, loss_test_cur = test_img(net, datasets_test[seq[cid]], args)
            acc.append(acc_test_cur)
            if cid < len(seq) - 1:
                print(f"testing in next concept: {seq[cid + 1]}")
                acc_test_next, loss_test_next = await cur_loop.run_in_executor(None, test_img, net,
                                                                               datasets_test[seq[cid + 1]], args)
                acc.append(acc_test_next)
            else:
                break
            cid += 1
    plot_acc(acc, now, 'test')
    await asyncio.sleep(1)
    while len(acc_list_all) < args.clients:
        await asyncio.sleep(10)
    avg_acc = np.zeros(len(acc_list_all[0]['acc']))
    for client_acc in acc_list_all:
        avg_acc += np.array(client_acc['acc'])
    avg_acc /= args.clients
    plot_acc(avg_acc, now, 'train_average')
    print(f'Total time: {time.time() - start_time} seconds')
    listen_task.cancel()


def plot_acc(acc, now, name):
    plt.figure()
    plt.plot(range(len(acc)), acc)
    plt.ylabel(f'{name}_acc')
    plt.savefig(
        './save/server_{}_{:0>2}{:0>2}_{:0>2}{:0>2}_acc.png'.format(name, now.month, now.day, now.hour, now.minute))
    with open('./save/server_{}_{:0>2}{:0>2}_{:0>2}{:0>2}_acc.txt') as f:
        f.write(str(acc))


def client_avg():
    weights = []
    for i in range(args.clients):
        w = torch.load(f'./clients/client_{i}.pt')
        weights.append(w)
    w_avg = FedAvg(weights)
    torch.save(w_avg, './clients/avg.pt')
    inc_eps()
    return w_avg


if __name__ == '__main__':
    args = args_parser()
    if args.dataset == 'mnist':
        net = CNNMnist()
    elif args.dataset == 'circle':
        net = MLP(2, 10, 2)
    elif args.dataset == 'sine':
        net = MLP(2, 10, 2)
    elif args.dataset == 'sea':
        net = MLP(3, 10, 2)
    else:
        exit(0)
    args.device = torch.device('cuda:{}'.format(args.gpu) if torch.cuda.is_available() and args.gpu != -1 else 'cpu')
    datasets_test = [SimpleData(f'./data/circle/test_{i}.txt') for i in range(args.concepts)]
    if not os.path.exists('./clients'):
        os.makedirs('./clients')
    if not os.path.exists('./save'):
        os.makedirs('./save')
    torch.save(net.state_dict(), './clients/avg.pt')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
