import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import ocr


FRONTEND_URL = os.environ.get('FRONTEND_URL')
origins = [
    FRONTEND_URL,
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.include_router(ocr.router)
