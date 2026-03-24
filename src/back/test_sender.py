import redis
import base64
import json
import time
import uuid

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

with open("test.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode()

task_id = str(uuid.uuid4())

task = {
    "task_id": task_id,
    "user_id": 1,
    "file_name": "test.jpg",
    "image_data": image_base64
}

r.lpush("image_tasks", json.dumps(task))

print("Task sent")

while True:
    result = r.get(f"result:{task_id}")

    if result:
        print("Result:", result)
        break

    time.sleep(1)
