import time
import os
import torch
import asyncio
from utils.server_options import args_parser
from connection.tcp_server import listen, inc_eps, get_received_numbers
from models.Fed import FedAvg


async def main(cur_loop):
    listen_task = cur_loop.create_task(listen(args.clients))
    # ping_task = cur_loop.create_task(ping())
    # await cur_loop.run_in_executor(None, slow_task)
    epoch = 0
    while True:
        await asyncio.sleep(1)
        print(f'received: {get_received_numbers()}, clients: {args.clients}')
        if get_received_numbers() == args.clients:
            await cur_loop.run_in_executor(None, client_avg)
            epoch += 1
            if epoch >= args.epochs:
                break
    await listen_task.cancel()


def client_avg():
    weights = []
    for i in range(args.clients):
        w = torch.load(f'./clients/client_{i}.pt')
        weights.append(w)
    w_avg = FedAvg(weights)
    torch.save(w_avg, './clients/avg.pt')
    inc_eps()


if __name__ == '__main__':
    args = args_parser()
    if not os.path.exists('./clients'):
        os.makedirs('./clients')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
