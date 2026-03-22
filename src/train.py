import os
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm

from src.dataset import get_dataloaders
from src.model import EmotionModel

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def train():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    train_dir = os.path.join(BASE_DIR, "data", "train")
    test_dir = os.path.join(BASE_DIR, "data", "test")

    train_loader, test_loader = get_dataloaders(
        train_dir,
        test_dir,
        batch_size=32
    )

    model = EmotionModel(num_classes=7)
    model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    num_epochs = 5

    for epoch in range(num_epochs):
        model.train()
        total_loss = 0

        loop = tqdm(train_loader)

        for images, labels in loop:
            images, labels = images.to(device), labels.to(device)

            output = model(images)
            loss = criterion(output, labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

            loop.set_description(f"Epoch [{epoch+1}/{num_epochs}]")
            loop.set_postfix(loss=loss.item())

        print(f"Epoch {epoch+1}, Loss: {total_loss/len(train_loader)}")
        test_acc = evaluate(model, test_loader, device)
        print(f"Test Accuracy: {test_acc:.2f}%")

    model_path = os.path.join(BASE_DIR, "outputs", "models", "emotion_model.pth")
    torch.save(model.state_dict(), model_path)
    print("Model saved")

def evaluate(model, loader, device):
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in loader:
            images, label = images.to(device), label.to(device)

            outputs = model(images)
            _, predicted = torch.max(outputs, 1)

            total += labels.size(0)
            correct += (predicted == label).sum().item()

    accuracy = 100 * correct / total

    return accuracy


if __name__ == "__main__":
    train()
