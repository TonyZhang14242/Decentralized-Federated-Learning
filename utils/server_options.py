import argparse


def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=10, help="rounds of training")
    parser.add_argument('--client_num', type=int, default=1, help="number of clients")
    args = parser.parse_args()
    return args
