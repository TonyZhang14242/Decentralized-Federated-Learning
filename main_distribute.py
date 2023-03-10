#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Python version: 3.6

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

matplotlib.use('Agg')


class FedClient:

    def __init__(self, args):
        trans_mnist = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
        self.dataset_train = MnistPart('./data/', train=True, transform=trans_mnist)
        self.dataset_test = datasets.MNIST('./data/', train=False, download=True, transform=trans_mnist)
        args.device = torch.device(
            'cuda:{}'.format(args.gpu) if torch.cuda.is_available() and args.gpu != -1 else 'cpu')
        self.args = args
        self.net_glob = CNNMnist(args=args).to(args.device)
        self.net_glob.train()
        self.loss_train = []
        if args.client_no == 0:
            torch.save(self.net_glob.state_dict(), 'weight.pt')

    def iter(self, iter_num, weight):
        self.net_glob.load_state_dict(weight)
        print('training')
        local = LocalUpdate(args=self.args, dataset=self.dataset_train, idxs=list(range(len(self.dataset_train))))
        w, loss = local.train(self.net_glob.to(self.args.device))
        # print('saving weights')
        # torch.save(w, 'weight.pt')
        print('Round {:3d}, Average loss {:.3f}'.format(iter_num, loss))
        self.loss_train.append(loss)
        time.sleep(2)
        return w, loss

    def plot_loss(self):
        args = self.args
        plt.figure()
        plt.plot(range(len(self.loss_train)), self.loss_train)
        plt.ylabel('train_loss')
        plt.savefig(
            './save/distribute_{}_{}_{}_C{}_iid{}.png'.format(args.dataset, args.model, args.epochs, args.frac,
                                                              args.iid))

    def test(self):
        self.net_glob.eval()
        acc_train, loss_train = test_img(self.net_glob, self.dataset_train, self.args)
        acc_test, loss_test = test_img(self.net_glob, self.dataset_test, self.args)
        print("Training accuracy: {:.2f}".format(acc_train))
        print("Testing accuracy: {:.2f}".format(acc_test))
        return acc_train, acc_test
