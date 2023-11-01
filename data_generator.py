import os.path

import numpy as np
import matplotlib.pyplot as plt


def save_npz(name, train, test):
    for i in range(len(train)):
        np.savez_compressed(f'./data/{name}/train_{i}.npz', data=train[i])
        np.savez_compressed(f'./data/{name}/test_{i}.npz', data=test[i])


def gen_circle(series, radius, count):
    result = []
    half_count_plus = int(count / 2 + count / 20)
    half_count_minus = int(count / 2 - count / 20)
    for center in series:
        angle = np.random.random(half_count_minus) * 2 * np.pi
        length = np.sqrt(np.random.random(half_count_minus) * (radius ** 2))
        inside = np.c_[length * np.cos(angle), length * np.sin(angle)] + np.tile(center, (half_count_minus, 1))
        inside = np.c_[inside, np.ones(half_count_minus)]
        points = np.random.random((half_count_plus, 2))
        points[:, 0] *= 1.1
        distance = points - np.tile(center, (half_count_plus, 1))
        label = (distance[:, 0] ** 2 + distance[:, 1] ** 2 < radius ** 2).astype(np.int32)
        result.append(np.r_[inside, np.c_[points, label]])
    return result


def circle(fig=False):
    centers = np.linspace((0.1, 0.5), (1, 0.5), 10)
    train = gen_circle(centers, 0.1, 10000)
    test = gen_circle(centers, 0.1, 1000)
    if not os.path.exists('./data/circle'):
        os.makedirs('./data/circle')
    save_npz('circle', train, test)
    if fig:
        plt.figure(figsize=(50, 20))
        for i in range(1, 11):
            axes = plt.subplot(2, 5, i)
            g = train[i - 1]
            # print(g[1] == 0)
            plt.scatter(g[np.where(g[:, 2] == 0)[0]][:, 0], g[np.where(g[:, 2] == 0)[0]][:, 1], marker='o',
                        color='red', s=1)
            plt.scatter(g[np.where(g[:, 2] == 1)[0]][:, 0], g[np.where(g[:, 2] == 1)[0]][:, 1], marker='o',
                        color='blue', s=1)
            axes.set_aspect('equal', adjustable='box')
            # axes.add_artist(plt.Circle((centers[i-1][0], centers[i-1][1]), 0.1, fill=False))
        plt.savefig('circle.jpg')
        # plt.show()


def gen_sine(count):
    result = []
    points = np.random.random((count, 2))
    points[:, 1] *= 2
    points[:, 1] -= 1
    points[:, 0] *= np.pi * 2
    label = points[:, 1] < np.sin(points[:, 0])
    result.append(np.c_[points, label])
    points = np.random.random((count, 2))
    points[:, 1] *= 2
    points[:, 1] -= 1
    points[:, 0] *= np.pi * 2
    label = points[:, 1] > np.sin(points[:, 0])
    result.append(np.c_[points, label])
    return result


def sine(fig=False):
    train = gen_sine(10000)
    test = gen_sine(1000)
    if not os.path.exists('./data/sine'):
        os.makedirs('./data/sine')
    save_npz('sine', train, test)
    if fig:
        plt.figure(figsize=(20, 10))
        for i in range(1, 3):
            axes = plt.subplot(1, 2, i)
            g = train[i - 1]
            plt.scatter(g[np.where(g[:, 2] == 0)[0]][:, 0], g[np.where(g[:, 2] == 0)[0]][:, 1], marker='o',
                        color='red', s=2)
            plt.scatter(g[np.where(g[:, 2] == 1)[0]][:, 0], g[np.where(g[:, 2] == 1)[0]][:, 1], marker='o',
                        color='blue', s=2)
            axes.set_aspect('equal', adjustable='box')
        plt.show()


def gen_sea(series, count):
    result = []
    for plane in series:
        points = np.random.random((count, 3))
        label = (points[:, 0] + points[:, 1] < plane).astype(np.int32)
        result.append(np.c_[points, label])
    return result


def sea(fig=False):
    planes = np.linspace(0.2, 1.8, 10)
    train = gen_sea(planes, 10000)
    test = gen_sea(planes, 1000)
    if not os.path.exists('./data/sea'):
        os.makedirs('./data/sea')
    for i in range(len(train)):
        np.savetxt(f'./data/sea/train_{i}.txt', train[i])
        np.savetxt(f'./data/sea/test_{i}.txt', test[i])
    if fig:
        plt.figure(figsize=(30, 3))
        for i in range(1, 11):
            plt.subplot(1, 10, i)
            g = test[i - 1]
            # print(g[1] == 0)
            plt.scatter(g[np.where(g[:, 3] == 0)[0]][:, 0], g[np.where(g[:, 3] == 0)[0]][:, 1], marker='o',
                        color='red', s=2)
            plt.scatter(g[np.where(g[:, 3] == 1)[0]][:, 0], g[np.where(g[:, 3] == 1)[0]][:, 1], marker='o',
                        color='blue', s=2)
        plt.show()


if __name__ == '__main__':
    if not os.path.exists('./data'):
        os.makedirs('./data')
    circle(fig=False)
