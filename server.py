import datetime
import time
import os

import numpy as np
import torch
import asyncio
from utils.server_options import args_parser
from connection.tcp_server import listen, inc_eps, get_received_numbers, acc_list_all
from models.Fed import FedAvg
from models.Nets import CNNMnist
from models.test import test_img
from torchvision import datasets, transforms
import matplotlib.pyplot as plt


async def main(cur_loop):
    global net
    global dataset_test
    global acc_list_all
    now = datetime.datetime.now()
    start_time = time.time()
    listen_task = cur_loop.create_task(listen(args.clients))
    # ping_task = cur_loop.create_task(ping())
    # await cur_loop.run_in_executor(None, slow_task)
    epoch = 0
    acc = []
    while True:
        await asyncio.sleep(1)
        # print(f'received: {get_received_numbers()}, clients: {args.clients}')
        if get_received_numbers() == args.clients:
            w = await cur_loop.run_in_executor(None, client_avg)
            epoch += 1
            net.load_state_dict(w)
            acc_test, loss_test = await cur_loop.run_in_executor(None, test_img, net, dataset_test, args)
            acc.append(acc_test)
            if epoch >= args.epochs:
                break
    plot_acc(acc, now, 'test')
    await asyncio.sleep(1)
    while len(acc_list_all) < args.clients:
        await asyncio.sleep(10)
    avg_acc = np.zeros(len(acc_list_all[0]['acc']))
    for client_acc in acc_list_all:
        avg_acc += np.array(client_acc['acc'])
    avg_acc /= args.clients
    plot_acc(avg_acc, now, 'train_avg')
    print(f'Total time: {time.time() - start_time} seconds')
    listen_task.cancel()


def plot_acc(acc, now, name):
    plt.figure()
    plt.plot(range(len(acc)), acc)
    plt.ylabel('test_acc')
    plt.savefig(
        './save/server_{}_{:0>2}{:0>2}_{:0>2}{:0>2}_acc.png'.format(name, now.month, now.day, now.hour, now.minute))


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
    net = CNNMnist()
    args.device = torch.device('cuda:{}'.format(args.gpu) if torch.cuda.is_available() and args.gpu != -1 else 'cpu')
    trans_mnist = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
    dataset_test = datasets.MNIST('./data/', train=False, download=True, transform=trans_mnist)
    if not os.path.exists('./clients'):
        os.makedirs('./clients')
    if not os.path.exists('./save'):
        os.makedirs('./save')
    torch.save(net.state_dict(), './clients/avg.pt')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
