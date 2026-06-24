from __future__ import annotations

import os
from functools import lru_cache

import cv2


@lru_cache(maxsize=1)
def load_face_cascade():
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cascade_path = os.path.join(base_path, "models", "haarcascade_frontalface_default.xml")
    cascade = cv2.CascadeClassifier(cascade_path)
    if cascade.empty():
        raise RuntimeError(f"Failed to load face cascade: {cascade_path}")
    return cascade


@lru_cache(maxsize=1)
def load_yunet_detector():
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_path, "models", "face_detection_yunet_2023mar.onnx")

    if not os.path.exists(model_path):
        return None

    try:
        return cv2.FaceDetectorYN_create(
            model_path,
            "",
            (320, 320),
            score_threshold=0.7,
            nms_threshold=0.3,
            top_k=5000,
        )
    except Exception:
        return None


def _detect_faces_yunet(frame):
    detector = load_yunet_detector()
    if detector is None:
        return []

    height, width = frame.shape[:2]
    detector.setInputSize((width, height))
    _, faces = detector.detect(frame)

    if faces is None:
        return []

    results = []
    for face in faces:
        x, y, w, h = face[:4]
        if w < 24 or h < 24:
            continue
        results.append((int(x), int(y), int(w), int(h)))
    return results


def expand_face_box(x, y, w, h, frame_width, frame_height, scale=0.35):
    pad_w = int(w * scale)
    pad_h = int(h * scale)

    x1 = max(0, x - pad_w)
    y1 = max(0, y - pad_h)
    x2 = min(frame_width, x + w + pad_w)
    y2 = min(frame_height, y + h + pad_h)
    return x1, y1, x2, y2


def detect_faces(frame):
    faces = _detect_faces_yunet(frame)
    if faces:
        return faces

    cascade = load_face_cascade()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    fallback_faces = cascade.detectMultiScale(
        gray,
        scaleFactor=1.08,
        minNeighbors=4,
        minSize=(30, 30),
    )
    return [(int(x), int(y), int(w), int(h)) for (x, y, w, h) in fallback_faces]
