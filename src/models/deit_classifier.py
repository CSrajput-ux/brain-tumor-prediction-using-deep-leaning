"""DeiT-Small/16 Vision Transformer classifier for brain MRI classification.

Complies with Part 6.2:
- ImageNet-pretrained timm deit_small_patch16_224.
- Patch size: 16x16, Input resolution: 224x224, Embedding dim: 384, Depth: 12, Heads: 6.
- Custom classification head adapted to required class count.
"""
from __future__ import annotations

import timm
import torch
import torch.nn as nn


class DeiTSmallClassifier(nn.Module):
    """DeiT-Small/16 Vision Transformer adapted for multi-class brain MRI classification."""
    def __init__(
        self,
        num_classes: int = 3,
        pretrained: bool = True,
        drop_rate: float = 0.1,
    ):
        super().__init__()
        self.num_classes = num_classes
        self.architecture_name = "deit_small_patch16_224"
        self.pretrained_checkpoint = "deit_small_patch16_224.fb_in1k" if pretrained else None

        self.model = timm.create_model(
            "deit_small_patch16_224",
            pretrained=pretrained,
            num_classes=num_classes,
            drop_rate=drop_rate,
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass returning unnormalized class logits (B, num_classes)."""
        return self.model(x)

    def forward_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extract post-transformer representation before head (B, 384)."""
        return self.model.forward_features(x)

    def get_parameter_counts(self) -> dict[str, int]:
        total = sum(p.numel() for p in self.parameters())
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        return {"total_parameters": total, "trainable_parameters": trainable}

