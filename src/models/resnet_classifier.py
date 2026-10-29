"""ResNet-50 classifier implementation for brain MRI classification.

Complies with Part 6.1:
- ImageNet-pretrained torchvision ResNet-50.
- Replaces final classification head for target class counts.
- Supports both full fine-tuning and feature extraction.
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torchvision.models as models


class ResNet50Classifier(nn.Module):
    """ResNet-50 architecture adapted for multi-class brain MRI classification."""
    def __init__(
        self,
        num_classes: int = 3,
        pretrained: bool = True,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.num_classes = num_classes
        self.architecture_name = "resnet50"
        self.pretrained_weights = "IMAGENET1K_V2" if pretrained else None

        weights = models.ResNet50_Weights.DEFAULT if pretrained else None
        self.backbone = models.resnet50(weights=weights)

        in_features = self.backbone.fc.in_features  # 2048
        if dropout > 0.0:
            self.backbone.fc = nn.Sequential(
                nn.Dropout(p=dropout),
                nn.Linear(in_features, num_classes),
            )
        else:
            self.backbone.fc = nn.Linear(in_features, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass returning unnormalized class logits (B, num_classes)."""
        return self.backbone(x)

    def forward_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extract post-pooling feature vectors (B, 2048)."""
        x = self.backbone.conv1(x)
        x = self.backbone.bn1(x)
        x = self.backbone.relu(x)
        x = self.backbone.maxpool(x)

        x = self.backbone.layer1(x)
        x = self.backbone.layer2(x)
        x = self.backbone.layer3(x)
        x = self.backbone.layer4(x)

        x = self.backbone.avgpool(x)
        return torch.flatten(x, 1)

    def get_parameter_counts(self) -> dict[str, int]:
        total = sum(p.numel() for p in self.parameters())
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        return {"total_parameters": total, "trainable_parameters": trainable}

