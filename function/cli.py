from __future__ import annotations

import argparse
from pathlib import Path

from function.io_utils import OUTPUT_IMAGES_DIR, OUTPUT_VIDEOS_DIR, ensure_project_dirs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="YOLO-based face emotion recognition for images and videos.",
    )
    parser.add_argument(
        "--source",
        required=True,
        choices=("image", "video"),
        help="Input source type.",
    )
    parser.add_argument(
        "--input",
        required=True,
        dest="input_path",
        help="Path to the input image or video.",
    )
    parser.add_argument(
        "--output",
        help="Path to save the processed image or video. Uses default output folders when omitted.",
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Disable preview window during processing.",
    )
    parser.add_argument(
        "--device",
        choices=("auto", "cpu", "cuda"),
        default="auto",
        help="Inference device. Use cuda in the GPU environment.",
    )
    return parser


def default_output_path(source: str, input_path: Path) -> Path:
    if source == "image":
        return OUTPUT_IMAGES_DIR / f"{input_path.stem}_result{input_path.suffix or '.jpg'}"
    return OUTPUT_VIDEOS_DIR / f"{input_path.stem}_result{input_path.suffix or '.mp4'}"


def main() -> int:
    ensure_project_dirs()
    parser = build_parser()
    args = parser.parse_args()

    import cv2

    from function.image_processor import process_image
    from function.model_loader import load_models
    from function.video_processor import process_video

    input_path = Path(args.input_path).expanduser().resolve()
    if not input_path.exists():
        parser.error(f"Input path does not exist: {input_path}")

    output_path = Path(args.output).expanduser().resolve() if args.output else default_output_path(args.source, input_path)

    seg_model, emotion_model, resolved_device = load_models(device=args.device)

    if args.source == "image":
        process_image(
            str(input_path),
            seg_model,
            emotion_model,
            display=not args.no_display,
            output_path=str(output_path),
            device=resolved_device,
        )
        print(f"Device: {resolved_device}")
        print(f"Saved processed image to: {output_path}")
        return 0

    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        parser.error(f"Unable to open video: {input_path}")

    process_video(
        cap,
        seg_model,
        emotion_model,
        display=not args.no_display,
        output_path=str(output_path),
        device=resolved_device,
        source_path=str(input_path),
        keep_audio=True,
    )
    print(f"Device: {resolved_device}")
    print(f"Saved processed video to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
