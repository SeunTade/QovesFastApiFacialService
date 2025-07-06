import base64
import json
import requests
import time
import ast


API_URL = "http://localhost:8000/api/v1/frontal/crop/submit"
STATUS_BASE_URL = "http://localhost:8000/api/v1/frontal/crop/status"
LANDMARKS_PATH = "Backend_Engineer/landmarks.txt"
IMAGE_PATH = "Backend_Engineer/original_image.png"
SEGMENTATION_PATH = "Backend_Engineer/segmentation_map.png"

print("📤 Preparing job payload...")

# Load image and segmentation map as base64
with open(IMAGE_PATH, "rb") as img_file:
    image_b64 = base64.b64encode(img_file.read()).decode()

with open(SEGMENTATION_PATH, "rb") as seg_file:
    segmentation_b64 = base64.b64encode(seg_file.read()).decode()

# Load landmarks (from a Python dict literal structure)
with open(LANDMARKS_PATH, "r") as f:
    raw = f.read()
    data = ast.literal_eval(raw)  # Safe evaluation of the literal dict
    raw_landmarks = data["landmarks"][0]  # Take the first face
    landmarks = [{"x": pt["x"], "y": pt["y"]} for pt in raw_landmarks]

# Prepare payload
payload = {
    "image": image_b64,
    "segmentation_map": segmentation_b64,
    "landmarks": landmarks
}

print("🚀 Sending request to:", API_URL)

try:
    response = requests.post(API_URL, json=payload)
    print("Response status:", response.status_code)
    response_data = response.json()
    print("🧾 Response JSON:", response_data)
except Exception as e:
    print("Request failed:", str(e))
    exit(1)

# 🆔 Extract job_id and poll for completion
job_id = response_data.get("id")
if not job_id:
    print("No job_id returned!")
    exit(1)

print(f"🔄 Polling status for job ID: {job_id}")
max_attempts = 30
interval_seconds = 2

for attempt in range(max_attempts):
    try:
        status_response = requests.get(f"{STATUS_BASE_URL}/{job_id}")
        if status_response.status_code != 200:
            print("Status check failed:", status_response.text)
            break

        status_data = status_response.json()
        status = status_data.get("status")
        print(f"⏱️ Attempt {attempt + 1}: Status = {status}")

        if status in ("complete", "done"):
            print("Job finished with status:", status)
            print("🖼️ SVG snippet:", status_data.get("svg", "")[:200] + "...")
            print("🗺️ Mask contours snippet:", json.dumps(status_data.get("mask_contours"), indent=2)[:200] + "...")
            break
        elif status == "failed":
            print("Job failed.")
            break

        time.sleep(interval_seconds)

    except Exception as e:
        print("Error while polling status:", str(e))
        break
else:
    print("Timed out waiting for job to complete.")
