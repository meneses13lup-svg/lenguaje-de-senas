import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

class Config:
    ROOT_DIR = ROOT_DIR
    CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", 0))
    FRAME_WIDTH = int(os.getenv("FRAME_WIDTH", 640))
    FRAME_HEIGHT = int(os.getenv("FRAME_HEIGHT", 480))
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{ROOT_DIR}/data/senavoz.db")
    APP_NAME = os.getenv("APP_NAME", "SeñaVoz")