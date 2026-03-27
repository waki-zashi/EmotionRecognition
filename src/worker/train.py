import os
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
from tqdm import tqdm
from sklearn.metrics import classification_report
from collections import Counter

from src.worker.dataset import get_dataloaders
from src.worker.model import EmotionModel
from src.worker.utils import plot_confusion_matrix, setup_logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def train():
    log_dir = os.path.join(BASE_DIR, "outputs", "logs")
    logger = setup_logger(log_dir)

    try:
        logger.info("Training started")

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Device: {device}")
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

        print("Calculating class weights...")
        all_labels = []
        for _, labels in train_loader:
            all_labels.extend(labels.cpu().numpy())

        counter = Counter(all_labels)
        total = sum(counter.values())

        class_weights = [total / (len(counter) * counter[i]) for i in range(7)]
        class_weights = torch.tensor(class_weights, dtype=torch.float32).to(device)

        logger.info(f"Class weights: {class_weights.tolist()}")

        criterion = nn.CrossEntropyLoss(weight=class_weights)
        optimizer = optim.Adam(model.parameters(), lr=0.001)

        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode='max',
            factor=0.3,
            patience=2
        )

        train_losses = []
        num_epochs = 10

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

            train_acc = evaluate(model, train_loader, device)
            print(f"Train Accuracy: {train_acc:.2f}%")

            test_acc = evaluate(model, test_loader, device)
            print(f"Test Accuracy: {test_acc:.2f}%")

            scheduler.step(test_acc)

            if epoch == 4:
                logger.info("Unfreezing layer4 for fine-tuning")
                print("Unfreezing layer4...")
                for param in model.model.layer4.parameters():
                    param.requires_grad = True

                optimizer = optim.Adam(model.parameters(), lr=0.0001)

            current_lr = optimizer.param_groups[0]['lr']

            logger.info(
                f"Epoch {epoch+1}/{num_epochs} | "
                f"Loss: {epoch_loss:.4f} | "
                f"Train Acc: {train_acc:.2f}% | "
                f"Test Acc: {test_acc:.2f}% | "
                f"LR: {current_lr}"
            )

        logger.info("Starting final evaluation")

        y_true, y_pred = evaluate_full(model, test_loader, device)

        plot_confusion_matrix(
            y_true, y_pred,
            class_names=['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        )

        report = classification_report(y_true, y_pred)
        print(report)

        logger.info("\n" + report)

        plt.plot(train_losses)
        plt.title("Training Loss")
        plt.xlabel("Epoch")
        plt.ylabel("Loss")
        plt.show()

        model_path = os.path.join(BASE_DIR, "outputs", "models", "emotion_model.pth")
        torch.save(model.state_dict(), model_path)

        logger.info(f"Model saved to {model_path}")
        print("Model saved")

        logger.info("Training finished successfully")

    except Exception as e:
        logger.exception(f"Training crashed with exception: {str(e)}")
        print("Error of training: ", str(e))
        raise e

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
