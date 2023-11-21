import torchvision.datasets.mnist as mnist
import os
from typing import Callable, Optional


class MnistSelf(mnist.MNIST):

    def __init__(
            self,
            root: str,
            concept: int,
            train: bool = True,
            transform: Optional[Callable] = None,
            target_transform: Optional[Callable] = None,
            complete=False
    ) -> None:
        self.concept = concept
        self.complete = complete
        super().__init__(root, train=train, transform=transform, target_transform=target_transform, download=False)

    resources = [
    ]

    def _load_data(self):
        image_file = (f"{'train' if self.train else 't10k'}-images-idx3-ubyte"
                      f"{'-self' if self.train and not self.complete else ''}-{self.concept}")
        # print(image_file)
        data = mnist.read_image_file(os.path.join(self.raw_folder, image_file))

        label_file = (f"{'train' if self.train else 't10k'}-labels-idx1-ubyte"
                      f"{'-self' if self.train and not self.complete else ''}")
        # print(os.path.join(self.raw_folder, label_file))
        targets = mnist.read_label_file(os.path.join(self.raw_folder, label_file))

        return data, targets

    @property
    def raw_folder(self) -> str:
        return self.root
