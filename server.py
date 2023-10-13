import time
import os
import torch
import asyncio
from utils.server_options import args_parser
from connection.tcp_server import listen, inc_eps, get_received_numbers
from models.Fed import FedAvg
from models.Nets import CNNMnist
from models.test import test_img
from torchvision import datasets, transforms
import matplotlib.pyplot as plt


async def main(cur_loop):
    global net
    global dataset_test
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
    listen_task.cancel()


def plot_acc(acc):
    plt.figure()
    plt.plot(range(len(acc)), acc)
    plt.ylabel('train_loss')
    plt.savefig('./save/server_loss.png')


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
    trans_mnist = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
    dataset_test = datasets.MNIST('./data/', train=False, download=True, transform=trans_mnist)
    if not os.path.exists('./clients'):
        os.makedirs('./clients')
    if not os.path.exists('./save'):
        os.makedirs('./save')
    torch.save(net.state_dict(), './clients/avg.pt')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
