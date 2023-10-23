from torch.utils.data import Dataset
import torch


class SineData(Dataset):
    def __init__(self):
        pass

    def __len__(self):
        return 2147483647

    def __getitem__(self, idx):
        feat = torch.rand(2)
        label = float(feat[1] < torch.sin(feat[0]))
        return feat, label


class CircleData(Dataset):
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def __len__(self):
        return 2147483647

    def __getitem__(self, idx):
        feat = torch.rand(2) * 2
        label = float((feat[0] - self.center[0]) ** 2 + (feat[1] - self.center[1]) ** 2 < self.radius ** 2)
        return feat, label

