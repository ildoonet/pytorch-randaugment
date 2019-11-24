# pytorch-randaugment
Unofficial PyTorch Reimplementation of RandAugment.

Code taken from https://github.com/DeepVoltaire/AutoAugment and https://github.com/jizongFox/uda

## How to use:
```python
from autoaugment import RandAugment
data = ImageFolder(rootdir, transform=transforms.Compose(
                        [
                            transforms.RandomCrop(32, padding=4, fill=128), # fill parameter needs torchvision installed from source
                            transforms.RandomHorizontalFlip(), 
                            RandAugment(),
                            transforms.ToTensor(), 
                            Cutout(n_holes=1, length=16), # (https://github.com/uoguelph-mlrg/Cutout/blob/master/util/cutout.py)
                            transforms.Normalize(...)
                        ])
)
loader = DataLoader(data, ...)
```


