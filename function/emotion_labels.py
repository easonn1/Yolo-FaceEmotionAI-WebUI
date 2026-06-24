EMOTION_LABELS_ZH = {
    "Anger": "愤怒",
    "Angry": "愤怒",
    "Contempt": "轻蔑",
    "Disgust": "厌恶",
    "Fear": "恐惧",
    "Happy": "开心",
    "Neutral": "中性",
    "Sad": "悲伤",
    "Surprise": "惊讶",
    "Unknown": "未知",
}


def to_chinese_label(label: str) -> str:
    return EMOTION_LABELS_ZH.get(label, label)
