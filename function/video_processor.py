from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import cv2
from deep_sort_realtime.deepsort_tracker import DeepSort

from .color import get_colors
from .frame_processor import process_frame
from .image import resize_image
from .io_utils import ensure_parent_dir
from .tracking import draw_tracks


def _create_video_writer(output_path, first_frame, fps):
    save_path = ensure_parent_dir(output_path)
    frame_height, frame_width = first_frame.shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    effective_fps = fps if fps and fps > 0 else 20.0
    return cv2.VideoWriter(str(save_path), fourcc, effective_fps, (frame_width, frame_height))


def _temp_video_path(output_path: str | Path) -> Path:
    output = Path(output_path)
    return output.with_name(f"{output.stem}.temp_no_audio{output.suffix}")


def _finalize_video(silent_video_path: Path, final_output_path: str, keep_audio: bool, original_video_path: str | None) -> None:
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path is None:
        print("ffmpeg not found. Saving video as is (browser preview might not work).", flush=True)
        silent_video_path.replace(final_output_path)
        return

    if keep_audio and original_video_path and Path(original_video_path).exists():
        command = [
            ffmpeg_path,
            "-y",
            "-i",
            str(silent_video_path),
            "-i",
            original_video_path,
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-map",
            "0:v:0",
            "-map",
            "1:a?",
            "-shortest",
            final_output_path,
        ]
        print(f"[FFMPEG] Merging audio and encoding to H.264...", flush=True)
    else:
        command = [
            ffmpeg_path,
            "-y",
            "-i",
            str(silent_video_path),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            final_output_path,
        ]
        print(f"[FFMPEG] Encoding to H.264...", flush=True)

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        silent_video_path.unlink(missing_ok=True)
        print("[FFMPEG] Transcoding completed successfully.", flush=True)
    else:
        print("FFmpeg transcoding failed. Keeping original output.", flush=True)
        print(result.stderr.strip(), flush=True)
        silent_video_path.replace(final_output_path)


def process_video(
    cap,
    seg_model,
    emotion_model,
    display=True,
    output_path=None,
    device="cpu",
    source_path=None,
    keep_audio=True,
):
    all_id_emotions = []
    writer = None
    silent_output_path = None
    source_fps = cap.get(cv2.CAP_PROP_FPS)

    try:
        tracker = DeepSort(max_age=5, n_init=2)
        colors = get_colors(10)

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        current_frame = 0

        if output_path:
            silent_output_path = _temp_video_path(output_path) if keep_audio and source_path else Path(output_path)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            current_frame += 1
            if total_frames > 0:
                progress = min(99, int((current_frame / total_frames) * 100))
                print(f"[PROGRESS] {progress}", flush=True)

            detections = process_frame(frame, seg_model, emotion_model, device=device)
            tracks = tracker.update_tracks(detections, frame=frame)

            frame_id_emotions = []
            for track in tracks:
                if track.is_confirmed():
                    frame_id_emotions.append((track.track_id, track.det_class or "Unknown"))
            all_id_emotions.append(frame_id_emotions)

            processed_frame = draw_tracks(frame.copy(), tracks, colors)

            if silent_output_path and writer is None:
                writer = _create_video_writer(silent_output_path, processed_frame, source_fps)

            if writer is not None:
                writer.write(processed_frame)

            if display:
                resized_frame = resize_image(processed_frame)
                cv2.imshow("YOLO Face Emotion Recognition", resized_frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    except Exception as exc:
        print(f"Failed to process video: {exc}")
    finally:
        if writer is not None:
            writer.release()
        cap.release()
        if display:
            cv2.destroyAllWindows()

        if output_path and silent_output_path and silent_output_path.exists():
            final_output = str(ensure_parent_dir(output_path))
            _finalize_video(silent_output_path, final_output, keep_audio, source_path)

        print("[PROGRESS] 100", flush=True)

    return all_id_emotions
