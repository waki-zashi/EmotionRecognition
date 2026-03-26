import os
import torch
from PIL import Image
from torchvision import transforms

from src.model import EmotionModel

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class_names = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

def load_model(device):
    model = EmotionModel(num_classes=7)
    model_path = os.path.join(BASE_DIR, "outputs", "models", "emotion_model.pth")

    model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))
    model.to(device)
    model.eval()

    return model

def predict_image(model, image_path, transform, device):
    image = Image.open(image_path).convert("RGB")
    image = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(image)
        probs = torch.softmax(output, dim=1)
        confidence, predicted = torch.max(probs,1)

    return class_names[predicted.item()], confidence.item()

def run_predict_suite(test_dir):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    model = load_model(device)

    for filename in sorted(os.listdir(test_dir)):
        file_path = os.path.join(test_dir, filename)

        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        emotion, conf = predict_image(model, file_path, transform, device)

        print(f"Photo: {filename} -> {emotion} ({conf:.2f})")

if __name__ == "__main__":
    test_dir = os.path.join(BASE_DIR, "data", "single_test")
    run_predict_suite(test_dir)
