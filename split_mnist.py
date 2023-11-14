import os.path

import numpy as np
import sys


def save_imgset(filename, dataset, start, end):
    with open(filename, 'wb') as f:
        f.write(int.to_bytes(2051, 4, 'big'))
        f.write(int.to_bytes(end - start, 4, 'big'))
        f.write(int.to_bytes(28, 4, 'big'))
        f.write(int.to_bytes(28, 4, 'big'))
        for img in dataset[start:end]:
            f.write(img.tobytes())


def save_labelset(filename, dataset, start, end):
    with open(filename, 'wb') as f:
        f.write(int.to_bytes(2049, 4, 'big'))
        f.write(int.to_bytes(end - start, 4, 'big'))

        f.write(dataset[start:end])


def load_mnist_images(filename, dtype='uint8'):
    """Output: A 3-d array with shape of [N, height, width]."""
    with open(filename, 'rb') as f:
        f.read(4)  # 以二进制形式一次读取4个字节
        n_samples = int.from_bytes(f.read(4), byteorder="big")
        n_rows = int.from_bytes(f.read(4), byteorder="big")
        n_cols = int.from_bytes(f.read(4), byteorder="big")

        images = np.empty((n_samples, n_rows * n_cols), dtype=dtype)
        for i in range(n_samples):
            for value in range(n_rows * n_cols):
                images[i][value] = int.from_bytes(f.read(1), byteorder="big")
        images = np.ascontiguousarray(images.reshape((-1, n_rows, n_cols)))

    return images


def load_mnist_labels(filename, dtype='uint8'):
    """Output An 1-d array with shape of [N,]."""
    with open(filename, 'rb') as f:
        f.read(4)
        n_samples = int.from_bytes(f.read(4), byteorder="big")
        labels = np.empty(n_samples, dtype=dtype)
        for i in range(n_samples):
            labels[i] = int.from_bytes(f.read(1), byteorder="big")

    return labels


if __name__ == '__main__':
    base_dir = sys.argv[1]
    sample_num = int(sys.argv[2])
    choice = np.random.choice(60000, sample_num)
    labels = load_mnist_labels(os.path.join(base_dir, 'train-labels-idx1-ubyte'))
    labels_c = labels[choice]
    print('train-labels-idx1-ubyte-self')
    save_labelset(os.path.join(base_dir, 'train-labels-idx1-ubyte-self'), labels_c, 0, sample_num)
    for i in range(4):
        images = load_mnist_images(os.path.join(base_dir, f'train-images-idx3-ubyte-{i}'))
        images_c = images[choice, :, :]
        print(f'train-images-idx3-ubyte-self-{i}')
        save_imgset(os.path.join(base_dir, f'train-images-idx3-ubyte-self-{i}'), images_c, 0, sample_num)


