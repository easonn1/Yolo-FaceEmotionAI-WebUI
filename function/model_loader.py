import os
import sys

from ultralytics import YOLO

from .runtime import resolve_device


def load_models(device="auto"):
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    emotion_model_path = os.path.join(base_path, "models", "best.pt")

    try:
        emotion_model = YOLO(emotion_model_path)
    except Exception as exc:
        print(f"Failed to load emotion model: {exc}")
        raise

    resolved_device = resolve_device(device)
    return None, emotion_model, resolved_device
