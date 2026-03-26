import torch.nn as nn
from torchvision import models

class EmotionModel(nn.Module):
    def __init__(self, num_classes=7):
        super(EmotionModel,self).__init__()

        self.model = models.resnet18(pretrained=True)

        for param in self.model.parameters():
            param.requires_grad = True

        in_features = self.model.fc.in_features
        self.model.fc = nn.Linear(in_features, num_classes)

    def forward(self, x):
        return self.model(x)
