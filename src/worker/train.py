import os
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
from tqdm import tqdm
from sklearn.metrics import classification_report

from src.worker.dataset import get_dataloaders
from src.worker.model import EmotionModel
from src.worker.utils import plot_confusion_matrix

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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
    optimizer = optim.Adam(model.parameters(), lr=0.0001)

    train_losses = []
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

        epoch_loss = total_loss / len(train_loader)
        train_losses.append(epoch_loss)
        print(f"Epoch {epoch+1}, Loss: {epoch_loss}")

        test_acc = evaluate(model, test_loader, device)
        print(f"Test Accuracy: {test_acc:.2f}%")

    y_true, y_pred = evaluate_full(model, test_loader, device)

    plot_confusion_matrix(
        y_true, y_pred,
        class_names=['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
    )

    print(classification_report(y_true, y_pred))

    plt.plot(train_losses)
    plt.title("Training Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.show()

    model_path = os.path.join(BASE_DIR, "outputs", "models", "emotion_model.pth")
    torch.save(model.state_dict(), model_path)
    print("Model saved")

def evaluate(model, loader, device):
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)

            outputs = model(images)
            _, predicted = torch.max(outputs, 1)

            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    accuracy = 100 * correct / total

    return accuracy


def evaluate_full(model, loader, device):
    model.eval()

    all_preds = []
    all_labels = []

    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)

            outputs = model(images)
            _, predicted = torch.max(outputs, 1)

            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    return all_labels, all_preds


if __name__ == "__main__":
    train()
