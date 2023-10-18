from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os
from database import engine, create_db_and_tables
from sqlmodel import Session
from models import Image
from utilis import classify_image

app = FastAPI()

upload_dir = "uploads"

if not os.path.exists(upload_dir):
    os.mkdir(upload_dir)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/image/")
def upload_image(file: UploadFile = File(...)):
    allowed_extensions = ('.jpg', '.jpeg', '.png', '.gif')
    if not file.filename.lower().endswith(allowed_extensions):
        # Use 400 status code for invalid requests
        return JSONResponse(content={"error": "Only images allowed"}, status_code=400)

    file_dir = "uploads"
    os.makedirs(file_dir, exist_ok=True)

    image_path = os.path.join(file_dir, file.filename)
    with open(image_path, "wb") as image_file:
        image_file.write(file.file.read())

    image_label = classify_image(image_path)

    with Session(engine) as session:
        image = Image(image_path=file.filename, image_label=image_label)
        session.add(image)
        session.commit()

    return JSONResponse(content={"message": "File uploaded successfully", "image_label": image_label}, status_code=200)
