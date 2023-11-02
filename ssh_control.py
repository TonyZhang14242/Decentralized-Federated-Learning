import asyncio
import asyncssh
import sys
import datetime

now = datetime.datetime.now()


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
    sys.argv = [sys.argv[0], *command.split(' ')]
    await asyncio.get_event_loop().run_in_executor(None, exec_server)
    print('Task server complete')


def exec_server():
    exec(open('./server.py').read())


async def run_multiple_clients(clients, client_cmd, server_cmd) -> None:
    # Put your lists of hosts here
    hosts = clients
    tasks = [run_client(host[0], host[1], client_cmd) for host in enumerate(hosts)]
    tasks.append(run_server(server_cmd))
    results = await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == '__main__':
    ls = []
    with open('clients.txt', 'r') as f:
        line = f.readline()
        while len(line) > 0:
            ls.append(line[:-1])
            line = f.readline()
    client_command = 'cd ~/Decentralized-Federated-Learning/; python ./main_client.py --client_no {} --dataset circle --local_ep 3 --concept_ep 4 --sample_num 2000'
    # server_command = 'cd ~/Decentralized-Federated-Learning/; /opt/conda/bin/python ./server.py --clients 10 --verbose --dataset circle --markov_pattern periodic --markov_prob 0.{} --markov_len 100 --concept_ep 4 --detail'
    server_args = '--clients 10 --verbose --dataset circle --markov_pattern periodic --markov_prob 0.{} --markov_len 100 --concept_ep 4 --detail'
    try:
        for i in range(3, 10):
            # print(server_command.format(i))
            asyncio.get_event_loop().run_until_complete(run_multiple_clients(ls, client_command, server_args.format(i)))
            print(f'prob 0.{i} complete')
    except (OSError, asyncssh.Error) as exc:
        sys.exit('SSH connection failed: ' + str(exc))
