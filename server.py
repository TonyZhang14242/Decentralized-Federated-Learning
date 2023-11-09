import datetime
import sys
import time
import os
import random

import numpy as np
import numpy.random
import torch
import asyncio
from utils.server_options import args_parser
from connection.tcp_server import listen, inc_eps, get_received_numbers, acc_list_all, set_seq
from models.Fed import FedAvg
from models.Nets import CNNMnist, MLP
from models.test import test_img
from torchvision import datasets, transforms
from models.datasets import SimpleData
import matplotlib.pyplot as plt
from markov_chain import generate_markov_chain
from utils.logger import Logger


async def main(cur_loop):
    global net
    global datasets_test
    global acc_list_all

    start_time = time.time()
    listen_task = cur_loop.create_task(listen(args.clients))
    # ping_task = cur_loop.create_task(ping())
    # await cur_loop.run_in_executor(None, slow_task)
    acc = []
    loss = []
    acc_detail = []
    seq = generate_markov_chain(args.markov_pattern, args.markov_prob, args.markov_states, args.markov_len)
    seq = [_ * 2 for _ in seq]
    with open(f'./save/{folder}/seq.txt', 'w') as f:
        f.write(str(seq[0]))
        seq_str = str(seq[0])
        for i in range(1, len(seq)):
            f.write(f',{seq[i]}')
            seq_str += f',{seq[i]}'
    set_seq(seq_str)
    # with open('seq.txt') as f:
    #     seq_str = f.read()
    #     seq_str = seq_str.split(',')
    #     seq = [int(_) for _ in seq_str]
    print("Sequence: ", seq)
    cid = 0
    concept_ep = 0
    while True:
        logger.flush()
        await asyncio.sleep(0.5)
        # time.sleep(1)
        if get_received_numbers() == args.clients:
            with open('./received.txt', 'w') as f:
                pass
            w = await cur_loop.run_in_executor(None, client_avg)
            net.load_state_dict(w)
            if concept_ep < args.concept_ep - 1:
                if args.detail:
                    print(f'concept epoch {concept_ep}')
                    print(f"testing concept epoch {concept_ep} in concept: {seq[cid]}")
                    acc_test_cur, loss_test_cur = await cur_loop.run_in_executor(None, test_img, net,
                                                                                 datasets_test[seq[cid]], args)
                    acc_detail.append(acc_test_cur)
                concept_ep += 1
            else:
                print(f'concept epoch {concept_ep}')
                print(f"testing in current concept: {seq[cid]}")
                acc_test_cur, loss_test_cur = await cur_loop.run_in_executor(None, test_img, net,
                                                                             datasets_test[seq[cid]], args)
                acc.append(acc_test_cur)
                acc_detail.append(acc_test_cur)
                loss.append(loss_test_cur)
                if cid < len(seq) - 1:
                    print(f"testing in next concept: {seq[cid + 1]}")
                    acc_test_next, loss_test_next = await cur_loop.run_in_executor(None, test_img, net,
                                                                                   datasets_test[seq[cid + 1]], args)
                    acc.append(acc_test_next)
                    acc_detail.append(acc_test_next)
                    loss.append(loss_test_next)
                else:
                    break
                np.savetxt(
                    f'./save/{folder}/server_test_acc.txt',
                    np.array(acc))
                cid += 1
                concept_ep = 0
    plot_acc(acc, now, 'test_acc')
    if args.detail:
        plot_acc(acc_detail, now, 'test_detail_acc')
    plot_acc(loss, now, 'test_loss')
    await asyncio.sleep(1)
    while len(acc_list_all) < args.clients:
        await asyncio.sleep(10)
    avg_acc = np.zeros(len(acc_list_all[0]['acc']))
    for client_acc in acc_list_all:
        avg_acc += np.array(client_acc['acc'])
    avg_acc /= args.clients
    plot_acc(avg_acc, now, 'train_acc_average')
    print(f'Total time: {time.time() - start_time} seconds')
    print(f'Average test acc: {sum(acc) / len(acc)}')
    print(f'Average loss: {sum(loss) / len(loss)}')
    listen_task.cancel()


def plot_acc(acc, now, name):
    plt.figure()
    plt.plot(range(len(acc)), acc)
    plt.ylabel(name)
    plt.title(title)
    plt.savefig(
        f'./save/{folder}/server_{name}.png')
    np.savetxt(
        f'./save/{folder}/server_{name}.txt',
        np.array(acc))


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
    numpy.random.seed(args.seed)
    random.seed(args.seed)
    torch.manual_seed(args.seed)
    if args.dataset == 'mnist':
        net = CNNMnist()
        states = 4
    elif args.dataset == 'circle':
        net = MLP(2, 10, 2)
        states = 10
    elif args.dataset == 'sine':
        net = MLP(2, 5, 2)
        states = 2
    else:
        exit(0)
    now = datetime.datetime.now()
    folder = '{}_{}_{}_{}_{:0>2}{:0>2}_{:0>2}{:0>2}'.format(args.dataset, args.markov_pattern, args.markov_prob,
                                                            args.markov_len, now.month, now.day, now.hour, now.minute)
    title = '{}_{}_{}_{}'.format(args.dataset, args.markov_pattern, args.markov_prob, args.markov_len)
    os.makedirs(f'./save/{folder}')
    logger = Logger(f'./save/{folder}/server.log')
    sys.stdout = logger
    print('Arguments: ')
    print(f'\t local_epoch: {args.local_ep}')
    print(f'\t concept_ep: {args.concept_ep}')
    print(f'\t learning rate: {args.lr}')
    print(f'\t dataset: {args.dataset}')
    print(f'\t markov pattern: {args.markov_pattern}')
    print(f'\t markov probability: {args.markov_prob}')
    print(f'\t markov states: {args.markov_states}')
    print(f'\t time slots: {args.markov_len}')
    print(f'\t seed: {args.seed}')
    print()
    args.device = torch.device('cuda:{}'.format(args.gpu) if torch.cuda.is_available() and args.gpu != -1 else 'cpu')
    datasets_test = [SimpleData(f'./data/circle/test_{i}.npz') for i in range(states)]
    if not os.path.exists('./clients'):
        os.makedirs('./clients')
    if not os.path.exists('./save'):
        os.makedirs('./save')
    torch.save(net.state_dict(), './clients/avg.pt')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
