import time
import os
import torch
import asyncio
from utils.server_options import args_parser
from connection.tcp_server import listen, inc_eps, get_received_numbers
from models.Fed import FedAvg


async def main(cur_loop):
    listen_task = cur_loop.create_task(listen(args.client_num))
    # ping_task = cur_loop.create_task(ping())
    # await cur_loop.run_in_executor(None, slow_task)
    while True:
        await asyncio.sleep(1)
        print(f'received: {get_received_numbers()}, clients: {args.client_num}')
        if get_received_numbers() == args.client_num:
            await cur_loop.run_in_executor(None, client_avg)


def client_avg():
    weights = []
    for i in range(args.client_num):
        w = torch.load(f'./clients/client_{i}.pt')
        weights.append(w)
    w_avg = FedAvg(weights)
    torch.save(w_avg, './clients/avg.pt')
    inc_eps()


async def ping():
    while True:
        await asyncio.sleep(1)
        print('ping')


def slow_task():
    time.sleep(5)
    print('im slow')


if __name__ == '__main__':
    args = args_parser()
    # args.client_num = 8
    if not os.path.exists('./clients'):
        os.makedirs('./clients')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
