import redis
import base64
import json
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

with open("test.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode()

task = {
    "task_id": "test",
    "user_id": 1,
    "file_name": "test.jpg",
    "image_data": image_base64
}

r.lpush("image_tasks", json.dumps(task))

print("Task sent")

while True:
    _, result = r.brpop("image_results")
    print("Result:", result)