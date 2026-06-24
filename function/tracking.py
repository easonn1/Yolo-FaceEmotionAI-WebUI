from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


FONT_CANDIDATES = (
    Path("C:/Windows/Fonts/msyh.ttc"),
    Path("C:/Windows/Fonts/msyhbd.ttc"),
    Path("C:/Windows/Fonts/simhei.ttf"),
    Path("C:/Windows/Fonts/simsun.ttc"),
)


def _load_font(font_size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for font_path in FONT_CANDIDATES:
        if font_path.exists():
            return ImageFont.truetype(str(font_path), font_size)
    return ImageFont.load_default()


def _draw_label(frame, text: str, anchor_x: int, anchor_y: int, accent_color):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_frame)
    draw = ImageDraw.Draw(pil_image, "RGBA")

    font = _load_font(24)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    padding_x = 12
    padding_y = 8
    label_x1 = max(0, anchor_x)
    label_y2 = max(text_height + padding_y * 2, anchor_y)
    label_y1 = max(0, label_y2 - (text_height + padding_y * 2))
    label_x2 = min(frame.shape[1], label_x1 + text_width + padding_x * 2)

    draw.rounded_rectangle(
        (label_x1, label_y1, label_x2, label_y2),
        radius=8,
        fill=(18, 18, 18, 220),
        outline=(int(accent_color[2]), int(accent_color[1]), int(accent_color[0]), 255),
        width=2,
    )

    text_x = label_x1 + padding_x
    text_y = label_y1 + padding_y - 1
    draw.text((text_x + 1, text_y + 1), text, font=font, fill=(0, 0, 0, 255))
    draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255, 255))

    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)


def _draw_single_box(frame, x1, y1, x2, y2, label_text, color):
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
    label_anchor_y = y1 - 6 if y1 > 48 else y1 + 42
    return _draw_label(frame, label_text, x1, label_anchor_y, color)


def draw_notice(frame, text: str, position: str = "top_left"):
    notice_color = (0, 140, 255)
    margin = 12

    if position == "top_left":
        anchor_x = margin
        anchor_y = 44
    elif position == "bottom_left":
        anchor_x = margin
        anchor_y = frame.shape[0] - margin
    else:
        anchor_x = margin
        anchor_y = 44

    return _draw_label(frame, text, anchor_x, anchor_y, notice_color)


def draw_tracks(frame, tracks, colors, detections=None):
    """Draw DeepSORT tracks when available, otherwise fall back to raw detections."""
    person_count = 0
    drew_confirmed_track = False

    for track in tracks:
        if not track.is_confirmed():
            continue

        drew_confirmed_track = True
        track_id = track.track_id
        x1, y1, x2, y2 = map(int, track.to_ltrb())
        supplementary = track.get_det_supplementary() or {}
        emotion_label = supplementary.get("emotion_label") or track.get_det_class() or "Unknown"
        color = colors[person_count % len(colors)]
        person_count += 1

        label_text = f"ID: {track_id}  {emotion_label}"
        frame = _draw_single_box(frame, x1, y1, x2, y2, label_text, color)

    if drew_confirmed_track or not detections:
        return frame

    for index, detection in enumerate(detections):
        bbox, _, emotion_label, *_ = detection
        x1, y1, width, height = bbox
        x2 = x1 + width
        y2 = y1 + height
        color = colors[index % len(colors)]
        label_text = f"{emotion_label}"
        frame = _draw_single_box(frame, x1, y1, x2, y2, label_text, color)

    return frame
