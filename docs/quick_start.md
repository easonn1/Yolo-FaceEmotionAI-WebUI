# 快速使用说明

这是一份面向新手的最短使用说明。

如果你只想完成下面这件事：

- 对图片进行情绪识别
- 对视频进行情绪识别
- 保存识别结果

那么直接照着这份做就够了。

---

## 一、先做什么

先打开 PowerShell，然后进入项目目录：

```powershell
cd "C:\Users\27993\Desktop\Professional course coding learning\Second semester of freshman year\Comprehensive Innovation Practice I\YOLO emotion recognition"
```

---

## 二、最快的运行方式

### 1. GPU 版图片识别

```powershell
.\.venv-cuda\Scripts\python main_cuda.py --source image --input "assets/inputs/images/lena.jpg" --no-display
```

### 2. GPU 版视频识别

```powershell
.\.venv-cuda\Scripts\python main_cuda.py --source video --input "assets/inputs/videos/face_walk.mp4" --no-display
```

如果你只是想更快看到效果，优先用这两条。

---

## 三、运行完成后去哪里看结果

识别后的结果会自动保存。

保存位置如下：

- 图片结果：`assets/outputs/images/`
- 视频结果：`assets/outputs/videos/`

---

## 四、如果你想换成自己的素材

### 图片

把你的图片放到：

```text
assets/inputs/images/
```

例如：

```text
assets/inputs/images/test.jpg
```

然后运行：

```powershell
.\.venv-cuda\Scripts\python main_cuda.py --source image --input "assets/inputs/images/test.jpg" --no-display
```

### 视频

把你的视频放到：

```text
assets/inputs/videos/
```

例如：

```text
assets/inputs/videos/test.mp4
```

然后运行：

```powershell
.\.venv-cuda\Scripts\python main_cuda.py --source video --input "assets/inputs/videos/test.mp4" --no-display
```

---

## 五、如果你不想用 GPU

可以改用 CPU 版：

图片：

```powershell
.\.venv\Scripts\python main.py --source image --input "assets/inputs/images/lena.jpg" --no-display
```

视频：

```powershell
.\.venv\Scripts\python main.py --source video --input "assets/inputs/videos/face_walk.mp4" --no-display
```

---

## 六、如果你想点按钮操作

### GPU 版图形界面

```powershell
.\.venv-cuda\Scripts\python launch_gui_cuda.py
```

### CPU 版图形界面

```powershell
.\.venv\Scripts\python launch_gui.py
```

打开后：

1. 点击 `Select Image` 或 `Select Video`
2. 选择文件
3. 等待处理完成
4. 去输出目录查看结果

---

## 七、怎么判断现在是不是在用显卡

如果命令输出中出现：

```text
Device: cuda
```

说明当前正在使用 GPU。

如果出现：

```text
Device: cpu
```

说明当前正在使用 CPU。

---

## 八、最短结论

如果你只记一套命令，就记这两条：

```powershell
.\.venv-cuda\Scripts\python main_cuda.py --source image --input "assets/inputs/images/lena.jpg" --no-display
.\.venv-cuda\Scripts\python main_cuda.py --source video --input "assets/inputs/videos/face_walk.mp4" --no-display
```

它们会：

- 使用显卡
- 自动完成识别
- 自动保存结果
