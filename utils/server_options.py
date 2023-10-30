import argparse


def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=10, help="rounds of training")
    parser.add_argument('--clients', type=int, default=1, help="number of clients")
    parser.add_argument('--gpu', type=int, default=-1, help="GPU ID, -1 for CPU")
    parser.add_argument('--bs', type=int, default=128, help="test batch size")
    parser.add_argument('--verbose', action='store_true', help='verbose print')
    parser.add_argument('--dataset', type=str, default='mnist', help="name of dataset")
    parser.add_argument('--markov_pattern', type=str, default='periodic', help='pattern of drift chain')
    parser.add_argument('--concepts', type=int, default=1, help='concept numbers')
    args = parser.parse_args()
    return args
