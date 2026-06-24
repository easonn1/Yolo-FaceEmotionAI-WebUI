EMOTION_LABELS_ZH = {
    "Anger": "\u6124\u6012",
    "Angry": "\u6124\u6012",
    "Contempt": "\u8f7b\u8511",
    "Disgust": "\u538c\u6076",
    "Fear": "\u6050\u60e7",
    "Happy": "\u5f00\u5fc3",
    "Neutral": "\u4e2d\u6027",
    "Sad": "\u60b2\u4f24",
    "Surprise": "\u60ca\u8bb6",
    "Unknown": "\u672a\u77e5",
}


def to_chinese_label(label: str) -> str:
    return EMOTION_LABELS_ZH.get(label, label)
