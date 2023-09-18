import torch

import main_distribute
from utils.options import args_parser

import tcp_client
import tcp_server
import os
import time

if __name__ == '__main__':
    args = args_parser()
    args.num_channels = 1
    args.model = 'cnn'
    if not os.path.exists('blue_address.txt'):
        print('Bluetooth address file not exist')
        exit()
    with open('blue_address.txt', 'r') as f:
        blue_address = f.readlines()
    server = tcp_server.TCPServer()
    client = tcp_client.TCPClient()
    fed = main_distribute.FedClient(args)
    for iters in range(args.epochs):
        if not (iters == 0 and args.client_no == 0):
            server.get_connection()  # receive and wait
        start_time = time.time()
        w = torch.load('weight.pt')
        w = fed.iter(iters, w)  # train
        torch.save(w, 'weight.pt')
        try:
            client.send_message_to_target(blue_address[iters].strip())  # send
        except:
            pass
        end_time = time.time()
        print("start: "+str(start_time))
        print("end: "+str(end_time))
    fed.test()
    if args.plot:
        fed.plot_loss()
