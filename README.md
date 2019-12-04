# pytorch-randaugment

Unofficial PyTorch Reimplementation of RandAugment. Most of codes are from [Fast AutoAugment](https://github.com/kakaobrain/fast-autoaugment).

## Introduction

TODO

## Install

```bash
$ pip install git+https://github.com/ildoonet/pytorch-randaugment
```

## Usage

```python
from torchvision.transforms import transforms
from RandAugment import RandAugment

transform_train = transforms.Compose([
    transforms.RandomCrop(32, padding=4),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(_CIFAR_MEAN, _CIFAR_STD),
])

# Add RandAugment with N, M(hyperparameter)
transform_train.transforms.insert(0, RandAugment(N, M))
```

## Experiment

We use same hyperparameters as the paper mentioned. 

### CIFAR-10

| Model             | Paper's Result | Ours         |
|-------------------|---------------:|-------------:|
| Wide-ResNet 28x10 | 97.3           | 97.4         |
| Shake26 2x96d     | 
| Pyramid272        | TODO           |

### CIFAR-100

| Model             | Paper's Result | Ours         |
|-------------------|---------------:|-------------:|
| Wide-ResNet 28x10 | 83.3           | 83.3         |

### ImageNet

TODO

## References

- RandAugment : [Paper](https://arxiv.org/abs/1909.13719)
- Fast AutoAugment : [Code](https://github.com/kakaobrain/fast-autoaugment) [Paper](https://arxiv.org/abs/1905.00397)
