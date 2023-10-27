import os
import requests
from dotenv import load_dotenv

load_dotenv()

hugging_api_key = os.getenv("HUGGING_API_KEY")


def find_max_score_label(data):
    if not data:
        return None

    max_dict = max(data, key=lambda x: float(x['score']))
    return max_dict["label"]


def query(filename):
    api_url = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"
    headers = {"Authorization": f"Bearer {hugging_api_key}"}

    with open(filename, "rb") as f:
        data = f.read()

    response = requests.post(api_url, headers=headers, data=data)
    return response.json()


def classify_image(image_url):
    output = query(image_url)
    return find_max_score_label(output)

