import os.path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams


def save_npz(name, train, test):
    for i in range(len(train)):
        np.savez_compressed(f'./data/{name}/train_{i}.npz', data=train[i])
        np.savez_compressed(f'./data/{name}/test_{i}.npz', data=test[i])


def plot(data, row, col, idx):
    axes = plt.subplot(row, col, idx)
    g = data[idx - 1]
    # print(g[1] == 0)
    plt.scatter(g[np.where(g[:, 2] == 0)[0]][:, 0], g[np.where(g[:, 2] == 0)[0]][:, 1], marker='o',
                color='red', s=1)
    plt.scatter(g[np.where(g[:, 2] == 1)[0]][:, 0], g[np.where(g[:, 2] == 1)[0]][:, 1], marker='o',
                color='blue', s=1)
    axes.set_aspect('equal', adjustable='box')


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
    test = gen_circle(centers, 0.1, 3000)
    if not os.path.exists('./data/circle'):
        os.makedirs('./data/circle')
    # save_npz('circle', train, test)
    if fig:
        plt.figure(figsize=(50, 20))
        rcParams['font.size'] = 26
        for i in range(1, 11):
            plot(train, 2, 5, i)
        plt.savefig('circle.pdf')
        plt.show()


def gen_circle2(series, radius, count):
    result = []
    cnt_in = int(count * 0.407)
    cnt_out = count - cnt_in
    for center in series:
        angle = np.random.random(cnt_in) * 2 * np.pi
        length = np.sqrt(np.random.random(cnt_in) * (radius ** 2))
        inside = np.c_[length * np.cos(angle), length * np.sin(angle)] + np.tile(center, (cnt_in, 1))
        inside = np.c_[inside, np.ones(cnt_in)]
        points = np.random.random((cnt_out, 2))
        points[:, 0] *= 0.2
        points[:, 0] += center[0] - 0.1
        distance = points - np.tile(center, (cnt_out, 1))
        label = (distance[:, 0] ** 2 + distance[:, 1] ** 2 < radius ** 2).astype(np.int32)
        result.append(np.r_[inside, np.c_[points, label]])
    return result


def circle2(fig=False):
    centers = np.linspace((0.1, 0.5), (1, 0.5), 10)
    train = gen_circle2(centers, 0.1, 10000)
    test = gen_circle2(centers, 0.1, 3000)
    if not os.path.exists('./data/circle2'):
        os.makedirs('./data/circle2')
    save_npz('circle2', train, test)
    if fig:
        plt.figure(figsize=(50, 20))
        for i in range(1, 11):
            plot(train, 2, 5, i)
        plt.savefig('circle2.jpg')
        plt.show()


def gen_sine1(count):
    result = []
    points = np.random.random((count, 2))
    label = points[:, 1] < np.sin(points[:, 0])
    result.append(np.c_[points, label])
    points = np.random.random((count, 2))
    label = points[:, 1] > np.sin(points[:, 0])
    result.append(np.c_[points, label])
    return result


def sine1(fig=False):
    train = gen_sine1(10000)
    test = gen_sine1(3000)
    if not os.path.exists('./data/sine1'):
        os.makedirs('./data/sine1')
    save_npz('sine1', train, test)
    if fig:
        plt.figure(figsize=(20, 10))
        for i in range(1, 3):
            plot(train, 1, 2, i)
        plt.savefig('sine1')
        plt.show()


def gen_sine2(count):
    result = []
    points = np.random.random((count, 2))
    points_x = points[:, 0] * (3 * np.pi)
    label = points[:, 1] < (0.5 + 0.3 * np.sin(points_x))
    result.append(np.c_[points, label])
    points = np.random.random((count, 2))
    points_x = points[:, 0] * (3 * np.pi)
    label = points[:, 1] > (0.5 + 0.3 * np.sin(points_x))
    result.append(np.c_[points, label])
    return result


def sine2(fig=False):
    train = gen_sine2(10000)
    test = gen_sine2(3000)
    if not os.path.exists('./data/sine2'):
        os.makedirs('./data/sine2')
    save_npz('sine2', train, test)
    if fig:
        plt.figure(figsize=(20, 10))
        for i in range(1, 3):
            plot(train, 1, 2, i)
        plt.savefig('sine2')
        plt.show()


def gen_sinirrel(sine):
    irrel = []
    for data in sine:
        rd = np.random.random((data.shape[0], 2))
        data = np.c_[data[:, 0:2], rd, data[:, 2]]
        irrel.append(data)
    return irrel


def sinirrel1(fig=False):
    train = gen_sinirrel(gen_sine1(10000))
    test = gen_sinirrel(gen_sine1(3000))
    if not os.path.exists('./data/sinirrel1'):
        os.makedirs('./data/sinirrel1')
    save_npz('sinirrel1', train, test)


def sinirrel2(fig=False):
    train = gen_sinirrel(gen_sine2(10000))
    test = gen_sinirrel(gen_sine2(3000))
    if not os.path.exists('./data/sinirrel2'):
        os.makedirs('./data/sinirrel2')
    save_npz('sinirrel2', train, test)


def gauss_2d(count, c1, c2, div):
    dim1 = np.random.normal(c1, div, count)
    dim2 = np.random.normal(c2, div, count)
    return np.c_[dim1, dim2]


def gen_gauss(count):
    half_cnt = int(count / 2)
    cov = np.array([[1, 0], [0, 1]])
    cent1 = gauss_2d(half_cnt, 0, 0, 1)
    cent2 = gauss_2d(half_cnt, 2, 0, 4)
    # cent1 = np.random.multivariate_normal((0, 0), cov / 2, half_cnt)
    # cent2 = np.random.multivariate_normal((2, 0), cov, half_cnt)
    fig = plt.figure()
    ax = plt.gca()
    ax.set_aspect('equal', adjustable='box')
    plt.scatter(cent2[:, 0], cent2[:, 1], marker='o', color='blue', s=1)
    plt.scatter(cent1[:, 0], cent1[:, 1], marker='o', color='red', s=1)
    plt.show()


def gen_stagger(count):
    np.random.randint()


if __name__ == '__main__':
    if not os.path.exists('./data'):
        os.makedirs('./data')
    # gen_gauss(10000)
    circle(fig=True)
