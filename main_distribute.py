#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Python version: 3.6
import datetime

import matplotlib
import matplotlib.pyplot as plt
import copy
import numpy as np
from torchvision import datasets, transforms
import torch
import time

from models.Update import LocalUpdate
from models.Nets import MLP, CNNMnist, CNNCifar
from models.datasets import SimpleData
from models.test import test_img
from models.mnist_self import MnistSelf
from utils.sampling import random_split

matplotlib.use('Agg')


class FedClient:

    def __init__(self, args, seq):
        trans_mnist = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
        # self.dataset_train = MnistPart('./data/', train=True, transform=trans_mnist)
        if args.dataset == 'circle':
            self.net_glob = MLP(2, 10, 2)
            states = 10
            self.datasets_train = [SimpleData(f'./data/circle/train_{i}_self.npz') for i in range(states)]
            print(len(self.datasets_train[0]))
            self.datasets_test = [SimpleData(f'./data/circle/test_{i}.npz') for i in range(states)]
        elif args.dataset == 'circle2':
            self.net_glob = MLP(2, 10, 2)
            states = 25
            self.datasets_train = [SimpleData(f'./data/circle2/train_{i}_self.npz') for i in range(states)]
            print(len(self.datasets_train[0]))
            self.datasets_test = [SimpleData(f'./data/circle2/test_{i}.npz') for i in range(states)]
        elif args.dataset == 'mnist':
            self.net_glob = CNNMnist()
            states = 4
            self.datasets_test = [MnistSelf('./data/MNIST-Rotate', i, train=False, transform=trans_mnist) for i in
                                  range(states)]
            self.datasets_train = [MnistSelf('./data/MNIST-Rotate', i, train=True, transform=trans_mnist) for i in
                                   range(states)]
        elif args.dataset == 'mnist-noniid':
            self.net_glob = CNNMnist()
            states = 4
            self.datasets_test = [MnistSelf('./data/MNIST-Rotate', i, train=False, transform=trans_mnist) for i in
                                  range(states)]
            self.datasets_train = [MnistSelf('./data/MNIST-Rotate-Noniid', i, train=True, transform=trans_mnist) for i in
                                   range(states)]
        else:
            print('Unknown dataset')
            exit(0)

        args.device = torch.device(
            'cuda:{}'.format(args.gpu) if torch.cuda.is_available() and args.gpu != -1 else 'cpu')
        self.args = args
        self.net_glob.train()
        self.loss_train = []
        self.acc_train = []
        # self.sample = random_split(self.datasets_train[0], args.sample_num)
        self.now = datetime.datetime.now()
        self.seq = seq

    def iter(self, iter_num, weight):
        self.net_glob.load_state_dict(weight)
        print('training')
        local = LocalUpdate(args=self.args, dataset=self.datasets_train[self.seq[iter_num]])
        w, loss, acc = local.train(self.net_glob.to(self.args.device))
        for eps in range(self.args.local_ep - 1):
            w, loss, acc = local.train(self.net_glob.to(self.args.device))
        # print('saving weights')
        # torch.save(w, 'weight.pt')
        print('Concept {:3d}, Average loss {:.3f}'.format(iter_num, loss))
        self.loss_train.append(loss)
        self.acc_train.append(acc)
        return w, loss

    def plot_loss(self):
        args = self.args
        now = self.now
        plt.figure()
        plt.plot(range(len(self.loss_train)), self.loss_train)
        plt.ylabel('train_loss')
        plt.savefig(
            './save/client_{}_{:0>2}{:0>2}_{:0>2}{:0>2}_loss.png'.format(args.client_no, now.month, now.day,
                                                                         now.hour, now.minute))

    def plot_acc(self):
        args = self.args
        now = self.now
        plt.figure()
        plt.plot(range(len(self.acc_train)), self.acc_train)
        plt.ylabel('train_acc')
        plt.savefig(
            './save/client_{}_{:0>2}{:0>2}_{:0>2}{:0>2}_acc.png'.format(args.client_no, now.month, now.day,
                                                                        now.hour, now.minute))

    def test(self):
        self.net_glob.eval()
        acc_train, loss_train = test_img(self.net_glob, self.datasets_train[0], self.args)
        acc_test, loss_test = test_img(self.net_glob, self.datasets_test[0], self.args)
        print("Training accuracy: {:.2f}".format(acc_train))
        print("Testing accuracy: {:.2f}".format(acc_test))
        return acc_train, acc_test
