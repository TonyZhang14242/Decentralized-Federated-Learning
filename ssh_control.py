import asyncio
import os.path

import asyncssh
import sys
import datetime


async def run_client(device_id, host, command):
    async with asyncssh.connect(host, username='ming', password='123', known_hosts=None) as conn:
        savedir = './out/{}/{:0>2}{:0>2}_{:0>2}{:0>2}.log'.format(device_id, now.month, now.day, now.hour, now.minute)
        print(f'client_{device_id} started')
        result = await conn.run(command.format(device_id), stdout=savedir)
        if isinstance(result, Exception):
            print('Task %d failed: %s' % (device_id, str(result)))
        elif result.exit_status != 0:
            print('Task %d exited with status %s:' % (device_id, result.exit_status))
            print(result.stderr, end='')
        else:
            print('Task %d succeeded:' % device_id)
            print(result.stdout, end='')
        return result


async def run_server(command):
    async with asyncssh.connect('127.0.0.1', username='sustech', password='tangming123', known_hosts=None) as conn:
        savedir = './out/server/{:0>2}{:0>2}_{:0>2}{:0>2}.log'.format(now.month, now.day, now.hour, now.minute)
        print('server started')
        result = await conn.run(command, stdout=savedir)
        if isinstance(result, Exception):
            print('Task server failed: %s' % str(result))
        elif result.exit_status != 0:
            print('Task server exited with status %s:' % result.exit_status)
            print(result.stderr, end='')
        else:
            print('Task server succeeded:')
            print(result.stdout, end='')
        return result


async def run_multiple_clients(clients, client_cmd, server_cmd) -> None:
    # Put your lists of hosts here
    hosts = clients
    tasks = [run_client(host[0], host[1], client_cmd) for host in enumerate(hosts)]
    tasks.append(run_server(server_cmd))
    results = await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == '__main__':
    ls = []
    if not os.path.exists('./out'):
        os.makedirs('./out')
    for i in range(10):
        if not os.path.exists(f'./out/{i}'):
            os.makedirs(f'./out/{i}')
    if not os.path.exists('./out/server'):
        os.makedirs('./out/server')
    with open('clients.txt', 'r') as f:
        line = f.readline()
        while len(line) > 0:
            ls.append(line[:-1])
            line = f.readline()
    client_command = 'cd ~/Decentralized-Federated-Learning/; python ./main_client.py --client_no {} --dataset circle --local_ep 3 --concept_ep 8 --lr 0.001'
    server_command = 'cd ~/Decentralized-Federated-Learning/; /home/sustech/miniconda3/envs/torch/bin/python ./server.py --clients 10 --verbose --dataset circle --markov_pattern periodic --markov_prob 0.{} --markov_len 50 --local_ep 3 --lr 0.001 --concept_ep 8 --detail'
    try:
        for i in range(1, 10):
            # print(server_command.format(i))
            now = datetime.datetime.now()
            asyncio.get_event_loop().run_until_complete(run_multiple_clients(ls, client_command, server_command.format(i)))
            print(f'prob 0.{i} complete')
    except (OSError, asyncssh.Error) as exc:
        sys.exit('SSH connection failed: ' + str(exc))
