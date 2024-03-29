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
    parser.add_argument('--markov_prob', type=float, default=0.5)
    parser.add_argument('--markov_states', type=int, default=1)
    parser.add_argument('--markov_len', type=int, default=10)
    parser.add_argument('--concept_ep', type=int, default=5)
    parser.add_argument('--local_ep', type=int, default=5, help='client local epoch, only for show')
    parser.add_argument('--lr', type=float, default=0.01, help="only for show")
    parser.add_argument('--detail', action='store_true')
    parser.add_argument('--seed', type=int, default=1, help='random seed (default: 1)')
    parser.add_argument('--seq_mul', type=int, default=1, help='multiply factor for markov chain')
    parser.add_argument('--seq_add', type=int, default=0)
    args = parser.parse_args()
    return args
