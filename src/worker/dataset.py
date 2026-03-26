import os
from torchvision import datasets, transforms
from torch.utils.data import DataLoader


def get_transforms():
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

def get_datasets(train_dir, test_dir):
    transform = get_transforms()

    train_dataset = datasets.ImageFolder(
        root=train_dir,
        transform=transform
    )

    test_dataset = datasets.ImageFolder(
        root=test_dir,
        transform=transform
    )

    return train_dataset, test_dataset

def get_dataloaders(train_dir, test_dir, batch_size=32):
    train_dataset, test_dataset = get_datasets(train_dir, test_dir)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False
    )

    return train_loader, test_loader