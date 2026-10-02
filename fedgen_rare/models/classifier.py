"""
Diagnostic Classifier backbones supporting latent feature extraction and forward classification head.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models

class ConvNet(nn.Module):
    """
    4-layer Convolutional Neural Network for pulmonary CT slice feature extraction.
    Includes feature projector for contrastive learning and forward_head for generative replay.
    """
    def __init__(self, in_channels=1, num_classes=3, feature_dim=128):
        super(ConvNet, self).__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(in_channels, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),  # 64 -> 32
            
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),  # 32 -> 16
            
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),  # 16 -> 8
            
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((1, 1))
        )
        self.feature_projection = nn.Sequential(
            nn.Linear(128, feature_dim),
            nn.LayerNorm(feature_dim),
            nn.ReLU(inplace=True)
        )
        self.fc = nn.Linear(feature_dim, num_classes)
        self.projector = nn.Sequential(
            nn.Linear(feature_dim, feature_dim),
            nn.ReLU(inplace=True),
            nn.Linear(feature_dim, feature_dim)
        )

    def extract_features(self, x):
        h = self.encoder(x)
        h = torch.flatten(h, 1)
        feat = self.feature_projection(h)
        return feat

    def forward_head(self, feat):
        return self.fc(feat)

    def forward(self, x, project=False):
        feat = self.extract_features(x)
        logits = self.forward_head(feat)
        if project:
            proj = self.projector(feat)
            return proj, logits
        return feat, logits


class ResNetClassifier(nn.Module):
    """
    ResNet-18 diagnostic backbone adapted for single-channel medical CT scans.
    """
    def __init__(self, in_channels=1, num_classes=3, feature_dim=128):
        super(ResNetClassifier, self).__init__()
        base_resnet = models.resnet18(weights=None)
        
        if in_channels != 3:
            self.conv1 = nn.Conv2d(in_channels, 64, kernel_size=7, stride=2, padding=3, bias=False)
        else:
            self.conv1 = base_resnet.conv1
            
        self.bn1 = base_resnet.bn1
        self.relu = base_resnet.relu
        self.maxpool = base_resnet.maxpool
        self.layer1 = base_resnet.layer1
        self.layer2 = base_resnet.layer2
        self.layer3 = base_resnet.layer3
        self.layer4 = base_resnet.layer4
        self.avgpool = base_resnet.avgpool
        
        in_features = base_resnet.fc.in_features
        self.feature_projection = nn.Sequential(
            nn.Linear(in_features, feature_dim),
            nn.LayerNorm(feature_dim),
            nn.ReLU(inplace=True)
        )
        self.fc = nn.Linear(feature_dim, num_classes)
        
        self.projector = nn.Sequential(
            nn.Linear(feature_dim, feature_dim),
            nn.ReLU(inplace=True),
            nn.Linear(feature_dim, feature_dim)
        )

    def extract_features(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.avgpool(x)
        h = torch.flatten(x, 1)
        feat = self.feature_projection(h)
        return feat

    def forward_head(self, feat):
        return self.fc(feat)

    def forward(self, x, project=False):
        feat = self.extract_features(x)
        logits = self.forward_head(feat)
        if project:
            proj = self.projector(feat)
            return proj, logits
        return feat, logits


def build_classifier(backbone='convnet', in_channels=1, num_classes=3, feature_dim=128):
    if backbone == 'resnet18':
        return ResNetClassifier(in_channels=in_channels, num_classes=num_classes, feature_dim=feature_dim)
    elif backbone == 'convnet':
        return ConvNet(in_channels=in_channels, num_classes=num_classes, feature_dim=feature_dim)
    else:
        raise ValueError(f"Unsupported backbone: {backbone}")
