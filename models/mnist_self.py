import torchvision.datasets.mnist as mnist
import os
from typing import Callable, Optional


class MnistPart(mnist.MNIST):

    def __init__(
            self,
            root: str,
            train: bool = True,
            transform: Optional[Callable] = None,
            target_transform: Optional[Callable] = None,
    ) -> None:
        super().__init__(root, train=train, transform=transform, target_transform=target_transform, download=False)

    resources = [
        ("images-idx3-ubyte", ""),
        ("labels-idx1-ubyte", ""),
    ]

    def _load_data(self):
        image_file = "images-idx3-ubyte"
        data = mnist.read_image_file(os.path.join(self.raw_folder, image_file))

        label_file = "labels-idx1-ubyte"
        targets = mnist.read_label_file(os.path.join(self.raw_folder, label_file))

        return data, targets

    @property
    def raw_folder(self) -> str:
        return os.path.join(self.root, self.__class__.__name__)
