import os
import sys
import tkinter as tk
import argparse
from pathlib import Path
from tkinter import filedialog, messagebox

import cv2

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from function.image_processor import process_image
from function.io_utils import OUTPUT_IMAGES_DIR, OUTPUT_VIDEOS_DIR, ensure_project_dirs
from function.model_loader import load_models
from function.video_processor import process_video


class YOLOObjectDetectionGUI:
    def __init__(self, device="auto"):
        ensure_project_dirs()
        self.seg_model, self.emotion_model, self.device = load_models(device=device)

        self.root = tk.Tk()
        self.root.title("YOLO Face Emotion Recognition")
        self.root.geometry("360x260")

        self.outer_frame = tk.Frame(self.root)
        self.outer_frame.pack(expand=True)

        self.button_frame = tk.Frame(self.outer_frame)
        self.button_frame.pack()

        self.create_buttons()

    def detect_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg;*.png;*.jpeg;*.bmp")]
        )
        if not file_path:
            return

        input_path = Path(file_path)
        output_path = OUTPUT_IMAGES_DIR / f"{input_path.stem}_gui{input_path.suffix or '.jpg'}"
        _, id_emotions = process_image(
            file_path,
            self.seg_model,
            self.emotion_model,
            display=True,
            output_path=str(output_path),
            device=self.device,
        )
        messagebox.showinfo(
            "Image Detection Complete",
            f"Result saved to:\n{output_path}\n\nDetected tracks:\n{id_emotions}",
        )

    def detect_video(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4;*.avi;*.mov;*.mkv")]
        )
        if not file_path:
            return

        input_path = Path(file_path)
        output_path = OUTPUT_VIDEOS_DIR / f"{input_path.stem}_gui.mp4"
        cap = cv2.VideoCapture(file_path)
        id_emotions = process_video(
            cap,
            self.seg_model,
            self.emotion_model,
            display=True,
            output_path=str(output_path),
            device=self.device,
            source_path=file_path,
            keep_audio=True,
        )
        messagebox.showinfo(
            "Video Detection Complete",
            f"Result saved to:\n{output_path}\n\nProcessed frames: {len(id_emotions)}",
        )

    def detect_camera(self):
        messagebox.showinfo(
            "Camera Reserved",
            "Camera mode is kept as an optional extra item. Please prioritize image/video tests first.",
        )

    def create_buttons(self):
        image_button = tk.Button(
            self.button_frame,
            text="Select Image",
            command=self.detect_image,
            width=24,
            height=2,
        )
        image_button.pack(pady=10)

        video_button = tk.Button(
            self.button_frame,
            text="Select Video",
            command=self.detect_video,
            width=24,
            height=2,
        )
        video_button.pack(pady=10)

        camera_button = tk.Button(
            self.button_frame,
            text="Camera (Optional)",
            command=self.detect_camera,
            width=24,
            height=2,
        )
        camera_button.pack(pady=10)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Launch the GUI for face emotion recognition.")
    parser.add_argument(
        "--device",
        choices=("auto", "cpu", "cuda"),
        default="auto",
        help="Inference device for the GUI session.",
    )
    args = parser.parse_args()

    app = YOLOObjectDetectionGUI(device=args.device)
    app.run()
