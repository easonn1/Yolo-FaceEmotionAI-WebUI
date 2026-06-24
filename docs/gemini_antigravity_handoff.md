# Gemini Antigravity 接管前端 UI 交接说明

## 你的任务

请接管当前项目的前端/UI 部分，为这个基于 YOLO 的人脸情绪识别项目制作一个更易用的本地操作界面。

目标不是重写模型，而是基于现有 Python 推理能力，做一个更好用、更适合作业展示的前端 UI。

---

## 项目类型

这是一个本地运行的 Python 项目，功能是：

- 对图片进行人脸情绪识别
- 对视频进行人脸情绪识别
- 保存识别结果
- 支持 CPU 版和 GPU/CUDA 版两套运行环境

当前已经能跑通，不需要你处理模型训练问题。

---

## 项目根目录

请在这个文件夹中工作：

(项目根目录)

---

## 当前已经存在的运行方式

### CPU 版命令行

```powershell
.\.venv\Scripts\python main.py --source image --input "assets/inputs/images/lena.jpg" --no-display
.\.venv\Scripts\python main.py --source video --input "assets/inputs/videos/face_walk.mp4" --no-display
```

### GPU 版命令行

```powershell
.\.venv-cuda\Scripts\python main_cuda.py --source image --input "assets/inputs/images/lena.jpg" --no-display
.\.venv-cuda\Scripts\python main_cuda.py --source video --input "assets/inputs/videos/face_walk.mp4" --no-display
```

### 现有 GUI 入口

```powershell
.\.venv\Scripts\python launch_gui.py
.\.venv-cuda\Scripts\python launch_gui_cuda.py
```

---

## 当前重要文件

请先阅读这些文件，再开始做 UI：

```text
main.py
main_cuda.py
launch_gui.py
launch_gui_cuda.py
function/cli.py
function/model_loader.py
function/image_processor.py
function/video_processor.py
gui/main_gui.py
docs/quick_start.md
docs/command_cheatsheet.md
```

---

## 你需要实现的目标

请制作一个更适合作业展示和日常操作的 UI，建议目标如下：

### 1. 统一操作入口

希望用户打开界面后，可以直接完成：

- 选择图片
- 选择视频
- 选择运行设备：CPU / GPU
- 启动识别
- 查看输出文件保存位置

### 2. 更清晰的界面结构

界面建议至少包含：

- 项目标题
- 输入文件选择区域
- 运行模式选择区域
- 输出路径提示区域
- 开始处理按钮
- 状态/日志显示区域

### 3. 更适合作业展示

UI 需要比当前 Tkinter 三按钮版更完整一些，尽量做到：

- 看起来像一个完整的小系统
- 操作路径清晰
- 适合老师演示
- 适合截图写进报告

### 4. 尽量不要改动核心推理逻辑

优先复用现有后端能力，不要重写模型推理流程。

也就是说，你的 UI 应该尽量调用现有入口，而不是重新发明一套识别逻辑。

---

## 推荐实现方向

你可以在以下方向中自行选择更合适的一种：

- 改进现有 Tkinter GUI
- 做一个本地 Web UI
- 做一个更现代的桌面 UI 外壳

但请满足这几个条件：

- 本机可直接运行
- 不依赖远程服务
- 能调用现有 Python 推理逻辑
- 适合 Windows 本地使用

如果你选择 Web UI，请尽量让它本地启动简单。

---

## 建议支持的功能

请优先完成这些功能：

- 选择图片并识别
- 选择视频并识别
- 选择 CPU / GPU
- 显示“当前运行设备”
- 显示结果保存位置
- 运行完成后给出成功提示

如果可以，再做这些增强：

- 显示处理进度
- 显示最近一次输出文件
- 一键打开输出目录
- 简单预览输入文件

---

## 不要破坏的内容

请尽量保留以下能力：

- CPU 版 `.venv`
- GPU 版 `.venv-cuda`
- 命令行入口 `main.py`
- 命令行入口 `main_cuda.py`
- 现有输入输出目录结构 `assets/`

不要把项目改成只能通过 UI 才能运行。

---

## 输入输出目录约定

请继续沿用当前目录结构：

```text
assets/inputs/images/
assets/inputs/videos/
assets/outputs/images/
assets/outputs/videos/
assets/outputs/screenshots/
```

---

## 成功标准

完成后，希望达到这些效果：

- 非技术用户也能看懂怎么用
- 老师演示时可以直接点选图片/视频完成识别
- 能明确切换 CPU / GPU
- 输出结果路径清楚
- 不破坏现有可运行的命令行版本

---

## 你可以直接使用的测试命令

### GPU 图片测试

```powershell
.\.venv-cuda\Scripts\python main_cuda.py --source image --input "assets/inputs/images/lena.jpg" --no-display
```

### GPU 视频测试

```powershell
.\.venv-cuda\Scripts\python main_cuda.py --source video --input "assets/inputs/videos/face_walk.mp4" --no-display
```

### CPU 图片测试

```powershell
.\.venv\Scripts\python main.py --source image --input "assets/inputs/images/lena.jpg" --no-display
```

---

## 额外说明

当前项目已经确认：

- CPU 版可运行
- GPU 版可运行
- GPU 环境可识别到 `NVIDIA GeForce RTX 4060 Laptop GPU`

因此你不需要先处理 CUDA 可用性问题，重点放在 UI 和交互体验上即可。

---

## 期望你最终交付的内容

请交付：

- 新的 UI 代码
- UI 启动方式
- 简要使用说明
- 如有必要，补充依赖说明

如果你新增了新的前端目录或入口文件，请同时说明：

- 启动命令
- 依赖安装方式
- 与现有 Python 推理逻辑的衔接方式
