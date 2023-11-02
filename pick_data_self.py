import os
import sys

import numpy as np

if __name__ == '__main__':
    base_dir = sys.argv[1]
    sample_num = int(sys.argv[2])
    files = os.listdir(base_dir)
    for file in files:
        if file.startswith('train'):
            new_file = file.split('.')[0] + '_self'
            print(new_file)
            data = np.load(os.path.join(base_dir, file))['data']
            choice = np.random.choice(len(data), sample_num)
            data_self = data[choice, :]
            np.savez_compressed(os.path.join(base_dir, new_file), data=data_self)
