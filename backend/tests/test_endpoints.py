import json
import base64
import time
from fastapi.testclient import TestClient
from app.main import app  

client = TestClient(app)

image_path = image_path_1 = image_path_2 = "tests/sampletext.png"

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_image

def test_ocr_synchronous_single_image():
    base64_encoded_image = encode_image_to_base64(image_path)
    
    valid_input = {
        "image_data": base64_encoded_image
    }

    response = client.post("/image-sync", json=valid_input)


    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Sample text\n"

def test_ocr_synchronous_multiple_images():
    base64_encoded_image_1 = encode_image_to_base64(image_path_1)
    base64_encoded_image_2 = encode_image_to_base64(image_path_2)
    
    valid_input = {
        "image_data": [base64_encoded_image_1, base64_encoded_image_2]
    }

    response = client.post("/image-sync", json=valid_input)

    assert response.status_code == 200
    data = response.json()
    assert data["text"] == ["Sample text\n", "Sample text\n"]

def test_ocr_create_task():
    base64_encoded_image = encode_image_to_base64(image_path)
    
    valid_input = {
        "image_data": base64_encoded_image
    }

    response = client.post("/image", json=valid_input)

    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data

    task_id = data["task_id"]

    time.sleep(5)
    response = client.get(f"/image?task_id={task_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Sample text\n"
