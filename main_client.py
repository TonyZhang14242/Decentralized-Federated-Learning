import random
import sys

import torch

import main_distribute
from utils.options import args_parser
import connection.tcp_client as client_net
import os
import configparser
import time
import numpy as np

if __name__ == '__main__':
    args = args_parser()
    np.random.seed(args.seed)
    random.seed(args.seed)
    torch.manual_seed(args.seed)
    config = configparser.ConfigParser()
    config.read('client_config.ini')
    server = config['server']['addr']
    port = int(config['server']['port'])
    seq = client_net.request_seq(server, port)
    print(f'seq: {seq}')
    fed = main_distribute.FedClient(args, seq)
    if not os.path.exists('./save'):
        os.makedirs('./save')
    accu = 0
    for cid in range(len(seq)):
        for concept_ep in range(args.concept_ep):
            client_net.request_weight(server, port, accu)  # receive and wait
            time.sleep(0.5)
            w = torch.load('weight.pt')
            start_time = time.time()
            w, loss = fed.iter(cid, w)  # train
            torch.save(w, 'weight.pt')
            print(f'Train complete in {time.time() - start_time} seconds')
            client_net.send_file(server, port, args.client_no)
            sys.stdout.flush()
            accu += 1
        # train_acc, test_acc = fed.test()
        # print(f'Epoch: {local_epoch}, loss: {local_epoch}')
        # with open(f'./save/peer_{args.client_no}_time{args.time}_{args.pick}_{args.topology}.txt', 'w') as f:
        #     f.write(f'Train acc: {train_acc}\n')
        #     f.write(f'Test acc: {test_acc}\n')
        #     for peer in torch.load('weight.pt')['path']:
        #         f.write(str(peer) + '\n')
    client_net.send_acc(server, port, args.client_no, fed.acc_train)
    fed.plot_loss()
    fed.plot_acc()
