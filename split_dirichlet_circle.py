import os.path
import random
import sys

import numpy as np
from torchvision import datasets
from torch.utils.data import ConcatDataset
import matplotlib.pyplot as plt
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
sample_num = 2000

if __name__ == "__main__":
    client_id = int(sys.argv[3])
    dataset_name = sys.argv[1]
    concepts = int(sys.argv[2])
    # client_id = 1
    np.random.seed(seed)
    random.seed(seed)
    # train_data = datasets.MNIST(
    #     root="./data", download=True, train=True)
    # test_data = datasets.MNIST(
    #     root="./data", download=True, train=False)
    train_data_all = [np.load(f'./data/{dataset_name}/train_{i}.npz')['data'] for i in range(concepts)]

    train_data = train_data_all[0]
    n_classes = 2

    labels = train_data[:, 2].astype(np.int32)
    dataset = train_data

    # 我们让每个client不同label的样本数量不同，以此做到Non-IID划分
    client_idcs = dirichlet_split_noniid(
        labels, alpha=dirichlet_alpha, n_clients=n_clients)
    self_idcs = client_idcs[client_id]
    print('client noniid: ', len(self_idcs))

    sample_idcs = np.random.choice(self_idcs, sample_num)

    base_dir = f'./data/{dataset_name}-noniid/'
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    for concept in range(concepts):
        data = train_data_all[concept]
        print(f'train_{concept}')
        data_self = data[sample_idcs, :]
        new_file = f'train_{concept}_self.npz'
        np.savez_compressed(os.path.join(base_dir, new_file), data=data_self)

    # 展示不同label划分到不同client的情况
    # plt.figure(figsize=(12, 8))
    # plt.hist([labels[idc] for idc in client_idcs], stacked=True,
    #          bins=np.arange(min(labels) - 0.5, max(labels) + 1.5, 1),
    #          label=["Client {}".format(i) for i in range(n_clients)],
    #          rwidth=0.5)
    # plt.xticks(np.arange(n_classes), ['positive', 'negative'])
    # plt.xlabel("Label type")
    # plt.ylabel("Number of samples")
    # plt.legend(loc="upper right")
    # plt.title("Display Label Distribution on Different Clients")
    # plt.show()

    # 展示不同client上的label分布
    # plt.figure(figsize=(12, 8))
    # label_distribution = [[] for _ in range(n_classes)]
    # for c_id, idc in enumerate(client_idcs):
    #     for idx in idc:
    #         label_distribution[labels[idx]].append(c_id)
    #
    # plt.hist(label_distribution, stacked=True,
    #          bins=np.arange(-0.5, n_clients + 1.5, 1),
    #          label=['positive', 'negative'], rwidth=0.5)
    # plt.xticks(np.arange(n_clients), ["Client %d" %
    #                                   c_id for c_id in range(n_clients)])
    # plt.xlabel("Client ID")
    # plt.ylabel("Number of samples")
    # plt.legend()
    # plt.title("Display Label Distribution on Different Clients")
    # plt.show()
