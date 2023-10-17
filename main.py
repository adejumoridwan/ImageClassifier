from fastapi import FastAPI
from models import User

app = FastAPI()

@app.post("/image/"):
