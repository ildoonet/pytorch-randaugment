# pytorch-randaugment

Unofficial PyTorch Reimplementation of RandAugment. Most of codes are from [Fast AutoAugment](https://github.com/kakaobrain/fast-autoaugment).

## Introduction

Models can be trained with RandAugment for the dataset of interest with no need for a separate proxy task. By only tuning two hyperparameters(N, M), you can achieve competitive performances as AutoAugments.

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

We use same hyperparameters as the paper mentioned. We observed similar results as reported. 

You can run an experiment with, 

```bash
$ python RandAugment/train.py -c confs/wresnet28x10_cifar10_b256.yaml --save cifar10_wres28x10.pth
```

### CIFAR-10 Classification

| Model             | Paper's Result | Ours         |
|-------------------|---------------:|-------------:|
| Wide-ResNet 28x10 | 97.3           | 97.4         |
| Shake26 2x96d     | 98.0           | 98.1         |
| Pyramid272        | 98.5           |

### CIFAR-100 Classification

| Model             | Paper's Result | Ours         |
|-------------------|---------------:|-------------:|
| Wide-ResNet 28x10 | 83.3           | 83.3         |

### SVHN Classification

| Model             | Paper's Result | Ours         |
|-------------------|---------------:|-------------:|
| Wide-ResNet 28x10 | 98.9           | 98.8         |

### ImageNet Classification

I have experienced some difficulties while reproducing paper's result.

**Issue : https://github.com/ildoonet/pytorch-randaugment/issues/9**

| Model             | Paper's Result | Ours         |
|-------------------|---------------:|-------------:|
| ResNet-50         | 77.6 / 92.8    | TODO 
| EfficientNet-B5   | 83.2 / 96.7    | TODO
| EfficientNet-B7   | 84.4 / 97.1    | TODO

## References

- RandAugment : [Paper](https://arxiv.org/abs/1909.13719)
- Fast AutoAugment : [Code](https://github.com/kakaobrain/fast-autoaugment) [Paper](https://arxiv.org/abs/1905.00397)
