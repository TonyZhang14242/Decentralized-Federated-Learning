import os.path
import random
import sys

import numpy as np
from torchvision import datasets
from torch.utils.data import ConcatDataset
import matplotlib.pyplot as plt
from split_mnist import load_mnist_labels, load_mnist_images, save_imgset, save_labelset
from models.mnist_self import MnistSelf


def dirichlet_split_noniid(train_labels, alpha, n_clients):
    '''
    按照参数为alpha的Dirichlet分布将样本索引集合划分为n_clients个子集
    '''
    n_classes = train_labels.max() + 1
    # (K, N) 类别标签分布矩阵X，记录每个类别划分到每个client去的比例
    label_distribution = np.random.dirichlet([alpha] * n_clients, n_classes)
    # (K, ...) 记录K个类别对应的样本索引集合
    class_idcs = [np.argwhere(train_labels == y).flatten()
                  for y in range(n_classes)]

    # 记录N个client分别对应的样本索引集合
    client_idcs = [[] for _ in range(n_clients)]
    for k_idcs, fracs in zip(class_idcs, label_distribution):
        # np.split按照比例fracs将类别为k的样本索引k_idcs划分为了N个子集
        # i表示第i个client，idcs表示其对应的样本索引集合idcs
        for i, idcs in enumerate(np.split(k_idcs,
                                          (np.cumsum(fracs)[:-1] * len(k_idcs)).
                                                  astype(int))):
            client_idcs[i] += [idcs]

    client_idcs = [np.concatenate(idcs) for idcs in client_idcs]

    return client_idcs


n_clients = 10
dirichlet_alpha = 1.0
seed = 1
sample_num = 5000

if __name__ == "__main__":
    client_id = int(sys.argv[1])
    np.random.seed(seed)
    random.seed(seed)
    # train_data = datasets.MNIST(
    #     root="./data", download=True, train=True)
    # test_data = datasets.MNIST(
    #     root="./data", download=True, train=False)
    train_data_all = [MnistSelf('./data/MNIST-Rotate', i, train=True, complete=True) for i in range(4)]

    train_data = train_data_all[0]
    classes = train_data.classes
    n_classes = len(classes)

    labels = np.array(train_data.targets)
    dataset = train_data

    # 我们让每个client不同label的样本数量不同，以此做到Non-IID划分
    client_idcs = dirichlet_split_noniid(
        labels, alpha=dirichlet_alpha, n_clients=n_clients)
    self_idcs = client_idcs[client_id]
    print('client noniid: ', len(self_idcs))
    while len(self_idcs) < sample_num:
        self_idcs = np.r_[self_idcs, self_idcs]

    sample_idcs = np.random.choice(self_idcs, sample_num, replace=False)

    base_dir = './data/MNIST-Rotate-Noniid/'
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    print('train-labels-idx1-ubyte-self')
    save_labelset(os.path.join(base_dir, 'train-labels-idx1-ubyte-self'), labels[sample_idcs],
                  0, sample_num)
    for concept in range(4):
        imgs = train_data_all[concept].data.numpy()[sample_idcs]
        print(f'train-images-idx3-ubyte-self-{concept}')
        save_imgset(os.path.join(base_dir, f'train-images-idx3-ubyte-self-{concept}'), imgs, 0, len(imgs))

    # 展示不同label划分到不同client的情况
    # plt.figure(figsize=(12, 8))
    # plt.hist([labels[idc] for idc in client_idcs], stacked=True,
    #          bins=np.arange(min(labels) - 0.5, max(labels) + 1.5, 1),
    #          label=["Client {}".format(i) for i in range(n_clients)],
    #          rwidth=0.5)
    # plt.xticks(np.arange(n_classes), train_data.classes)
    # plt.xlabel("Label type")
    # plt.ylabel("Number of samples")
    # plt.legend(loc="upper right")
    # plt.title("Display Label Distribution on Different Clients")
    # plt.show()
