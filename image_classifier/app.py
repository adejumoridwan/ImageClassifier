import uvicorn
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
import os
from .database import engine, create_db_and_tables
from sqlmodel import Session
from .models import Image
from .utilis import classify_image
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

templates = Jinja2Templates(directory="image_classifier/templates")

upload_dir = "image_classifier/static"

if not os.path.exists(upload_dir):
    os.mkdir(upload_dir)

app.mount("/static", StaticFiles(directory=upload_dir), name="static")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/", response_class=HTMLResponse)
def get_image_upload_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.post("/image", response_class=HTMLResponse)
def upload_image(request: Request, file: UploadFile = File(...)):
    allowed_extensions = ('.jpg', '.jpeg', '.png', '.gif')
    if not file.filename.lower().endswith(allowed_extensions):
        return JSONResponse(content={"error": "Only images allowed"}, status_code=400)

    image_path = os.path.join(upload_dir, file.filename)
    with open(image_path, "wb") as image_file:
        image_file.write(file.file.read())

    image_label = classify_image(image_path)

    with Session(engine) as session:
        image = Image(image_path=file.filename, image_label=image_label)
        session.add(image)
        session.commit()

    return templates.TemplateResponse("home.html", {"request": request,
                                                    "message": "File uploaded successfully",
                                                    "image_label": image_label,
                                                    "image_path": f"/static/{file.filename}"}, status_code=200)


if __name__ == "__main__":
    uvicorn.run("image_classifier.app:app",
                host="127.0.0.1", port=8000, reload=True)
