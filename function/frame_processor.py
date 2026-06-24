from __future__ import annotations

from .emotion_labels import to_chinese_label
from .image import resize_image


def _extract_emotion_prediction(result, emotion_model):
    if getattr(result, "probs", None) is not None:
        top1 = int(result.probs.top1)
        top1_conf = result.probs.top1conf
        confidence = float(top1_conf.item() if hasattr(top1_conf, "item") else top1_conf)
        return emotion_model.names[top1], confidence

    if result.boxes is not None and len(result.boxes) > 0:
        best_index = 0
        if getattr(result.boxes, "conf", None) is not None and len(result.boxes.conf) > 0:
            best_index = int(result.boxes.conf.argmax().item())
            confidence = float(result.boxes.conf[best_index].item())
        else:
            confidence = None

        emotion_class_id = int(result.boxes.cls[best_index].item())
        return emotion_model.names[emotion_class_id], confidence

    return "Unknown", None


def _format_emotion_label(emotion_name, confidence):
    display_name = to_chinese_label(emotion_name)

    if confidence is None:
        return display_name

    return f"{display_name} {confidence * 100:.1f}%"


def process_frame(frame, seg_model, emotion_model, device="cpu"):
    seg_results = seg_model(frame, verbose=False, device=device)
    detections = []

    for result in seg_results:
        if result.boxes is None or len(result.boxes) == 0:
            continue

        for index in range(len(result.boxes)):
            class_id = int(result.boxes.cls[index].item())
            if class_id != 0:
                continue

            x1, y1, x2, y2 = map(int, result.boxes.xyxy[index].cpu().numpy())
            person_image = frame[y1:y2, x1:x2]
            if person_image.size == 0:
                continue

            resized_person = resize_image(person_image, 640)
            emotion_results = emotion_model(resized_person, verbose=False, device=device)
            emotion_name, confidence = _extract_emotion_prediction(emotion_results[0], emotion_model)
            emotion_label = _format_emotion_label(emotion_name, confidence)

            detections.append(([x1, y1, x2 - x1, y2 - y1], 1.0, emotion_label))

    return detections
