import random

import torch

import main_distribute
from utils.options import args_parser
import connection.tcp_client as client_net
import os
import time

if __name__ == '__main__':
    args = args_parser()
    args.num_channels = 1
    args.model = 'cnn'
    # server = '172.18.36.132'
    server = '127.0.0.1'
    fed = main_distribute.FedClient(args)
    for local_epoch in range(args.epochs):
        time.sleep(1)
        client_net.request_weight(server, local_epoch)  # receive and wait
        w = torch.load('weight.pt')
        print('train')
        w, loss = fed.iter(args.local_ep, w)  # train
        torch.save(w, 'weight.pt')
        client_net.send_file(server, args.client_no)
        # train_acc, test_acc = fed.test()
        # print(f'Epoch: {local_epoch}, loss: {local_epoch}')
        # with open(f'./save/peer_{args.client_no}_time{args.time}_{args.pick}_{args.topology}.txt', 'w') as f:
        #     f.write(f'Train acc: {train_acc}\n')
        #     f.write(f'Test acc: {test_acc}\n')
        #     for peer in torch.load('weight.pt')['path']:
        #         f.write(str(peer) + '\n')
    if args.plot:
        fed.plot_loss()
