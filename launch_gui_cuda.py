from gui.main_gui import YOLOObjectDetectionGUI


if __name__ == "__main__":
    app = YOLOObjectDetectionGUI(device="cuda")
    app.run()
