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

    # Use a high-contrast dark panel with a colored border so the text stays readable.
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


def draw_tracks(frame, tracks, colors):
    """Draw confirmed DeepSORT tracks on a frame."""
    person_count = 0

    for track in tracks:
        if not track.is_confirmed():
            continue

        track_id = track.track_id
        x1, y1, x2, y2 = map(int, track.to_ltrb())
        emotion_label = track.det_class or "未知"
        color = colors[person_count % len(colors)]
        person_count += 1

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)

        label_text = f"ID: {track_id}  {emotion_label}"
        label_anchor_y = y1 - 6 if y1 > 48 else y1 + 42
        frame = _draw_label(frame, label_text, x1, label_anchor_y, color)

    return frame
