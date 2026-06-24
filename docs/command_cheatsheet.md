# CPU / GPU 命令使用对照表

本项目现在有两套可并行使用的运行环境：

- CPU 版本：`.venv`
- GPU 版本：`.venv-cuda`

如果你只是想先跑通，用 CPU 版也可以。
如果你想用 RTX 4060 加速，就使用 GPU 版。

---

## 1. 进入项目目录

无论 CPU 还是 GPU，第一步都一样：

```powershell
cd "C:\path\to\Yolo-FaceEmotionAI-WebUI"
```

---

## 2. 图片识别命令对照

### CPU 版

```powershell
.\.venv\Scripts\python main.py --source image --input "assets/inputs/images/lena.jpg" --no-display
```

### GPU 版

```powershell
.\.venv-cuda\Scripts\python main_cuda.py --source image --input "assets/inputs/images/lena.jpg" --no-display
```

---

## 3. 视频识别命令对照

### CPU 版

```powershell
.\.venv\Scripts\python main.py --source video --input "assets/inputs/videos/face_walk.mp4" --no-display
```

### GPU 版

```powershell
.\.venv-cuda\Scripts\python main_cuda.py --source video --input "assets/inputs/videos/face_walk.mp4" --no-display
```

---

## 4. 图形界面命令对照

### CPU 版

```powershell
.\.venv\Scripts\python launch_gui.py
```

### GPU 版

```powershell
.\.venv-cuda\Scripts\python launch_gui_cuda.py
```

---

## 5. 使用自己的图片

先把图片放到：

```text
assets/inputs/images/
```

例如文件名叫：

```text
assets/inputs/images/my_photo.jpg
```

### CPU 版

```powershell
.\.venv\Scripts\python main.py --source image --input "assets/inputs/images/my_photo.jpg" --no-display
```

### GPU 版

```powershell
.\.venv-cuda\Scripts\python main_cuda.py --source image --input "assets/inputs/images/my_photo.jpg" --no-display
```

---

## 6. 使用自己的视频

先把视频放到：

```text
assets/inputs/videos/
```

例如文件名叫：

```text
assets/inputs/videos/my_video.mp4
```

### CPU 版

```powershell
.\.venv\Scripts\python main.py --source video --input "assets/inputs/videos/my_video.mp4" --no-display
```

### GPU 版

```powershell
.\.venv-cuda\Scripts\python main_cuda.py --source video --input "assets/inputs/videos/my_video.mp4" --no-display
```

---

## 7. 结果保存位置对照

两套环境的结果保存位置相同：

- 图片结果：
  - `assets/outputs/images/`
- 视频结果：
  - `assets/outputs/videos/`
- 报告截图：
  - `assets/outputs/screenshots/`

---

## 8. 如何判断当前是不是用了显卡

如果你运行的是 GPU 版命令：

```powershell
.\.venv-cuda\Scripts\python main_cuda.py ...
```

程序输出里会看到类似：

```text
Device: cuda
```

这就说明当前确实在使用显卡。

如果看到：

```text
Device: cpu
```

说明当前没有走 GPU。

---

## 9. 最推荐的使用习惯

- 课堂演示前快速跑通：优先用 GPU 版
- 小测试、改代码、简单验证：CPU 版也可以
- 写报告留结果图：统一把素材和输出都放到 `assets` 目录下

---

## 10. 你现在最常用的四条命令

CPU 图片：

```powershell
.\.venv\Scripts\python main.py --source image --input "assets/inputs/images/lena.jpg" --no-display
```

CPU 视频：

```powershell
.\.venv\Scripts\python main.py --source video --input "assets/inputs/videos/face_walk.mp4" --no-display
```

GPU 图片：

```powershell
.\.venv-cuda\Scripts\python main_cuda.py --source image --input "assets/inputs/images/lena.jpg" --no-display
```

GPU 视频：

```powershell
.\.venv-cuda\Scripts\python main_cuda.py --source video --input "assets/inputs/videos/face_walk.mp4" --no-display
```
