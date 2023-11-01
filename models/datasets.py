import numpy as np
from torch.utils.data import Dataset
import torch


class SimpleData(Dataset):
    def __init__(self, path):
        self.data = np.load(path)['data']

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        feat = self.data[idx][0:-1]
        label = self.data[idx][-1]
        feat = feat.astype(np.float32)
        label = label.astype(np.longlong)
        return feat, label

