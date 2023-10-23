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
from models.Fed import FedAvg
from models.test import test_img
from models.mnist_self import MnistPart
from utils.sampling import random_split

matplotlib.use('Agg')


class FedClient:

    def __init__(self, args):
        trans_mnist = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
        # self.dataset_train = MnistPart('./data/', train=True, transform=trans_mnist)
        self.dataset_train = datasets.MNIST('./data/', train=True, download=True, transform=trans_mnist)
        self.dataset_test = datasets.MNIST('./data/', train=False, download=True, transform=trans_mnist)
        args.device = torch.device(
            'cuda:{}'.format(args.gpu) if torch.cuda.is_available() and args.gpu != -1 else 'cpu')
        self.args = args
        self.net_glob = CNNMnist().to(args.device)
        self.net_glob.train()
        self.loss_train = []
        self.acc_train = []
        self.sample = random_split(self.dataset_train, 10000)
        self.now = datetime.datetime.now()

    def iter(self, iter_num, weight):
        self.net_glob.load_state_dict(weight)
        print('training')
        local = LocalUpdate(args=self.args, dataset=self.dataset_train, idxs=self.sample)
        w, loss, acc = local.train(self.net_glob.to(self.args.device))
        # print('saving weights')
        # torch.save(w, 'weight.pt')
        print('Round {:3d}, Average loss {:.3f}'.format(iter_num, loss))
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
        acc_train, loss_train = test_img(self.net_glob, self.dataset_train, self.args)
        acc_test, loss_test = test_img(self.net_glob, self.dataset_test, self.args)
        print("Training accuracy: {:.2f}".format(acc_train))
        print("Testing accuracy: {:.2f}".format(acc_test))
        return acc_train, acc_test
