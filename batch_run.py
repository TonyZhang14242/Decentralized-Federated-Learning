import asyncio
import asyncssh
import sys
from typing import Optional


async def run_client(device_id, host, command):
    async with asyncssh.connect(host, username='ming', password='123', known_hosts=None) as conn:
        result = await conn.run(command)
        return result


async def run_server(command):
    command = command.replace('python', '/home/sustech/miniconda3/envs/torch/bin/python')
    async with asyncssh.connect('192.168.1.111', username='sustech', password='tangming123', known_hosts=None) as conn:
        result = await conn.run(command)
        return result


async def run_multiple_clients(clients, command) -> None:
    # Put your lists of hosts here
    hosts = clients
    tasks = [run_client(host[0], host[1], command) for host in enumerate(hosts)]
    tasks.append(run_server(command))
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for i, result in enumerate(results, 1):
        if isinstance(result, Exception):
            print('Task %d failed: %s' % (i, str(result)))
        elif result.exit_status != 0:
            print('Task %d exited with status %s:' % (i, result.exit_status))
            print(result.stderr, end='')
        else:
            print('Task %d succeeded:' % i)
            print(result.stdout, end='')

        print(75 * '-')


if __name__ == '__main__':
    ls = []
    with open('clients.txt', 'r') as f:
        line = f.readline()
        while len(line) > 0:
            ls.append(line[:-1])
            line = f.readline()
    print('Input command to run:')
    command = input()
    command = 'cd ~/Decentralized-Federated-Learning/; ' + command
    try:
        asyncio.get_event_loop().run_until_complete(run_multiple_clients(ls, command))
    except (OSError, asyncssh.Error) as exc:
        sys.exit('SSH connection failed: ' + str(exc))
