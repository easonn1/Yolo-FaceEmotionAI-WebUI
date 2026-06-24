import argparse

from gui.main_gui import YOLOObjectDetectionGUI


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
