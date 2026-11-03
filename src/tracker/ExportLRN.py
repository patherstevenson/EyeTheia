#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
:mod:`ExportLRN` module
=======================

ONNX friendly replacement for CrossMapLRN2d.

torch.nn.LocalResponseNorm gives the same results but is exported as a 3D
AveragePool with dynamic shape operations, which WebGPU (ONNX Runtime Web)
can only run in NCHW layout. ConvLRN computes the same normalization with
standard operations (Mul, Conv, Add, Pow, Div).

:author: Pather Stevenson
:date: October 2026
"""

import copy

import torch
import torch.nn as nn
import torch.nn.functional as F


class ConvLRN(nn.Module):
    """
    Local response normalization across channels, the sum of squares over
    neighbor channels is done with a fixed 1x1 convolution.
    """

    def __init__(self, channels: int, size: int = 5, alpha: float = 1e-4, beta: float = 0.75, k: float = 1.0) -> None:
        """
        :param channels: Number of input channels.
        :param size: Number of neighbor channels used for normalization.
        :param alpha: Multiplicative factor.
        :param beta: Exponent.
        :param k: Additive factor.
        """
        super(ConvLRN, self).__init__()

        self.size = size
        self.alpha = alpha
        self.beta = beta
        self.k = k

        # Same window as LocalResponseNorm: from c - size // 2 to c + (size - 1) // 2
        idx = torch.arange(channels)
        offset = idx[None, :] - idx[:, None]
        band = ((offset >= -(size // 2)) & (offset <= (size - 1) // 2)).float()

        self.register_buffer("weight", band[:, :, None, None])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        sq_sum = F.conv2d(x * x, self.weight)
        return x / (self.k + self.alpha / self.size * sq_sum).pow(self.beta)


def replace_crossmaplrn_for_onnx(module: nn.Module) -> nn.Module:
    """
    Return a deepcopy of the module where each CrossMapLRN2d is replaced by
    ConvLRN, the number of channels comes from the previous Conv2d.

    :param module: Model to export.
    :return: Model copy ready for ONNX export.
    """
    model_copy = copy.deepcopy(module)

    def recurse(parent: nn.Module) -> None:
        channels = None

        for name, child in parent.named_children():
            if isinstance(child, nn.Conv2d):
                channels = child.out_channels

            if child.__class__.__name__ == "CrossMapLRN2d":
                if channels is None:
                    raise ValueError(f"Cannot find the number of channels for '{name}'")

                lrn = ConvLRN(
                    channels,
                    size = getattr(child, "size", 5),
                    alpha = getattr(child, "alpha", 1e-4),
                    beta = getattr(child, "beta", 0.75),
                    k = getattr(child, "k", 1.0)
                )
                lrn.to(next(model_copy.parameters()).device)

                setattr(parent, name, lrn)
            else:
                recurse(child)

    recurse(model_copy)

    return model_copy
