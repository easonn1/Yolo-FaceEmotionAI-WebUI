from __future__ import annotations

import cv2
from deep_sort_realtime.deepsort_tracker import DeepSort

from .color import get_colors
from .frame_processor import process_frame
from .image import resize_image
from .io_utils import ensure_parent_dir
from .tracking import draw_notice, draw_tracks


def process_image(file_path, seg_model, emotion_model, display=True, output_path=None, device="cpu"):
    try:
        print("[PROGRESS] 10", flush=True)
        image = cv2.imread(file_path)
        if image is None:
            raise ValueError(f"Unable to read image file: {file_path}")

        print("[PROGRESS] 30", flush=True)
        tracker = DeepSort(max_age=5, n_init=1)
        colors = get_colors(10)
        detections = process_frame(image, seg_model, emotion_model, device=device)
        raw_detections = [(bbox, score, emotion_label) for bbox, score, emotion_label, _ in detections]
        others = [metadata for _, _, _, metadata in detections]

        print("[PROGRESS] 60", flush=True)
        tracks = tracker.update_tracks(raw_detections, frame=image, others=others)

        print("[PROGRESS] 80", flush=True)
        id_emotions = []
        for track in tracks:
            if track.is_confirmed():
                supplementary = track.get_det_supplementary() or {}
                id_emotions.append(
                    (
                        track.track_id,
                        supplementary.get("emotion_label") or track.get_det_class() or "Unknown",
                    )
                )

        if not id_emotions:
            for index, detection in enumerate(detections, start=1):
                id_emotions.append((f"det-{index}", detection[2]))

        processed_image = draw_tracks(image.copy(), tracks, colors, detections=detections)
        if not detections:
            print("No face detected.", flush=True)
            processed_image = draw_notice(processed_image, "No face detected.", position="top_left")
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
