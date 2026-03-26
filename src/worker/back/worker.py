import os
import redis
import json
import base64
import io
from PIL import Image

import torch
from torchvision import transforms

from src.worker.model import EmotionModel

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = 6379

TASK_QUEUE = "image_tasks"
RESULT_QUEUE = "image_results"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class_names = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

model = EmotionModel(num_classes=7)

model_path = os.path.join(BASE_DIR, "outputs", "models", "emotion_model.pth")
model.load_state_dict(torch.load(model_path, map_location=DEVICE))
model.to(DEVICE)
model.eval()

transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

print("Worker started. Waiting for tasks...")

while True:
    _, task_data = r.brpop(TASK_QUEUE)
    task = json.loads(task_data)

    try:
        task_id = task["task_id"]
        user_id = task["user_id"]
        image_base64 = task["image_data"]

        print(f"Processing task {task_id}")

        image_bytes = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        input_tensor = transform(image).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            outputs = model(input_tensor)
            probs = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probs, 1)

        result_text = class_names[predicted.item()]

        response = {
            "task_id": task_id,
            "user_id": user_id,
            "status": "success",
            "answer": result_text
        }
        print(f"Task {task_id} successfully finished! Answer: {result_text}")

    except Exception as e:
        print("Error", str(e))

        response = {
            "task_id": task.get("task_id", "unknown"),
            "user_id": task.get("user_id", "unknown"),
            "status": "error",
            "answer": str(e)
        }

    r.setex(f"result:{task_id}", 60, json.dumps(response))




