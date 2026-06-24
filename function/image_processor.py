from __future__ import annotations

import cv2
from deep_sort_realtime.deepsort_tracker import DeepSort

from .color import get_colors
from .frame_processor import process_frame
from .image import resize_image
from .io_utils import ensure_parent_dir
from .tracking import draw_tracks


def process_image(file_path, seg_model, emotion_model, display=True, output_path=None, device="cpu"):
    try:
        print("[PROGRESS] 10", flush=True)
        image = cv2.imread(file_path)
        if image is None:
            raise ValueError(f"Unable to read image file: {file_path}")

        print("[PROGRESS] 30", flush=True)
        tracker = DeepSort(max_age=5, n_init=2)
        colors = get_colors(10)
        detections = process_frame(image, seg_model, emotion_model, device=device)
        
        print("[PROGRESS] 60", flush=True)
        tracks = tracker.update_tracks(detections, frame=image)

        print("[PROGRESS] 80", flush=True)
        id_emotions = []
        for track in tracks:
            if track.is_confirmed():
                id_emotions.append((track.track_id, track.det_class or "Unknown"))

        processed_image = draw_tracks(image.copy(), tracks, colors)
        resized_image = resize_image(processed_image)

        if output_path:
            save_path = ensure_parent_dir(output_path)
            cv2.imwrite(str(save_path), processed_image)

        if display:
            cv2.imshow("YOLO Face Emotion Recognition", resized_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        print("[PROGRESS] 100", flush=True)
        return processed_image, id_emotions
    except Exception as exc:
        print(f"Failed to process image: {exc}")
        print("[PROGRESS] 100", flush=True)
        return None, []
