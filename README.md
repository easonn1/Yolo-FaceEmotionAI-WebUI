# YOLO v8 人脸表情识别监控中心 (YOLO Face Emotion Monitoring Center)

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.12-blue?logo=python)](https://www.python.org/)
[![YOLOv8](https://img.shields.io/badge/YOLO-v8-cyan?logo=ultralytics)](https://github.com/ultralytics/ultralytics)
[![Windows Compatible](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)](https://www.microsoft.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

这是一个基于深度学习（YOLOv8 & DeepSORT）的实时人脸表情识别与多目标跟踪系统，配备了极具现代科技感的玻璃拟态（Glassmorphism）Web 交互监控仪表盘。

---

## 📌 致谢与声明
本程序是基于开源项目 [Wyatt-Happy/Yolo-FaceEmotionAI](https://github.com/Wyatt-Happy/Yolo-FaceEmotionAI) 进行了深度二次开发、UI 界面重构与性能改进设计。

### 主要改进与升级亮点：
1. **全新开发交互式 Web UI 监控面板**：完全脱离命令行，通过高颜值的深色玻璃拟态网页控制台进行全方位交互，支持拖拽上传、媒体预览和独立终端日志区。
2. **新增 GPU 显卡加速版支持**：实现了 CPU 虚拟环境（`.venv`）与 GPU 显卡环境（`.venv-cuda`）双版本在网页端的无缝点选与一键切换。
3. **数据可视化优化（新增置信度显示）**：优化了画面框选与文字标签渲染，在中文标出情绪类别的同时，**额外标注了每个目标的置信度百分比**（如 `ID: 1 愤怒 85.0%`），并配合 DeepSORT 稳定分配 ID。
4. **视频网页预览黑屏修复（H.264 自动转码）**：针对 OpenCV 输出视频在网页中黑屏、无画面问题，集成了后台 `ffmpeg` 转码引擎，生成结果时自动转码为 H.264/AVC 编码，确保网页端直接预览顺畅播放。
5. **智能重新识别冲突确认弹窗**：针对同名文件二次推理，网页端提供“覆盖”或“生成新文件（自增计数后缀，如 `_result_1.mp4`）”的友好弹窗供用户选择。
6. **文件便捷管理集成**：
   - **重命名**：可直接在网页修改已生成文件名，且后端会自动重构 `history.json` 历史关联数据。
   - **定位文件位置**：可在已生成内容旁，一键在 Windows 资源管理器中打开对应路径并**自动选中/高亮**该文件。
   - **快捷打开文件夹**：输入和输出文件夹一键拉起。
7. **提供双击即用的编译 EXE 启动器**：打包生成了 `launch_web_ui.exe`，实现无命令环境下的单进程后台启动，且完美隔离、联动 adjacent 虚拟环境。

---

## 🛠️ 项目结构

```text
YOLO emotion recognition/
├── assets/                       # 多媒体数据与历史记录
│   ├── inputs/                   # 待识别素材
│   │   ├── images/
│   │   └── videos/
│   ├── outputs/                  # 识别结果输出
│   │   ├── images/
│   │   └── videos/
│   └── history.json              # 历史运行记录数据
├── function/                     # 后端核心计算模块
│   ├── cli.py                    # 命令行参数解析
│   ├── frame_processor.py        # 图像帧预处理与情感预测（包含置信度格式化）
│   ├── image_processor.py        # 图片推理核心流程
│   ├── io_utils.py               # IO 目录处理工具
│   ├── model_loader.py           # 神经网络模型载入
│   ├── tracking.py               # DeepSORT 多目标跟踪与绘制标签
│   └── video_processor.py        # 视频读取、帧循环、音频合并与 H.264 转码
├── models/                       # YOLO 权重
│   ├── best.pt                   # 表情分类权重
│   └── yolo11n-seg.pt            # 人脸分割权重
├── web_ui/                       # 前端仪表盘静态文件
│   ├── index.html                # 玻璃拟态仪表盘页面
│   ├── style.css                 # 现代发光特效、监控图表与响应式样式
│   └── app.js                    # 硬件 stats 轮询、上传、冲突模态弹窗与定位逻辑
├── web_server.py                 # 轻量级 Python HTTP API 服务端
├── launch_web_ui.py              # Web 控制中心启动脚本（多线程/单进程）
├── launch_web_ui.exe             # 编译打包好的 Windows 单文件快速启动器
└── requirements.txt              # Python 依赖清单
```

---

## 🚀 环境准备与运行

本系统支持两种运行环境：CPU 纯算力版和 GPU 显卡加速版，两者在后台目录相互隔离，可在 Web 界面自由点选切换。

### 1. 配置 CPU 环境 (.venv)
推荐使用现有的 Python 3.12：
```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. 配置 GPU CUDA 显卡加速环境 (.venv-cuda)
若拥有 NVIDIA 独立显卡并希望使用 GPU 进行极速推理：
1. 确保安装了 NVIDIA 显卡驱动以及相应的 CUDA Toolkit（推荐 CUDA 12.x）。
2. 在项目根目录下，使用 PowerShell 运行我们提供的环境配置脚本（会创建并部署 `.venv-cuda` 虚拟环境，并安装 CUDA 版 PyTorch）：
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
   .\setup_cuda_env.ps1
   ```

### 3. 一键启动监控中心
有以下三种启动方式：
- **方式 A（一键全自动启动 - 推荐零基础小白）**：直接双击运行项目根目录下的 **`一键启动服务.bat`**。该脚本会自动检测 Python 环境，如果是首次运行，会自动为您创建虚拟环境、安装依赖并自动打开浏览器启动 Web 界面！
- **方式 B（双击即用 - 推荐已配置好环境者）**：直接在项目根目录下双击 **`launch_web_ui.exe`**。
- **方式 C（手动脚本启动）**：在激活虚拟环境后，于终端运行：
  ```bash
  .venv\Scripts\python launch_web_ui.py
  ```

启动后，系统会自动打开默认浏览器并导航至 `http://localhost:8000`，展现“YOLO v8 人脸表情识别监控中心”。

---

## 🎨 仪表盘界面展示

监控中心包含以下三大版块：
* **文件控制中心**：支持文件拖拽上传并改名，分类展示输入、输出文件，可一键打开对应的磁盘文件夹。
* **系统资源实时占用监控**：采用类似 Windows 任务管理器的环形 Gauge 图与脉冲波动图，实时反映本机的 CPU、内存、GPU 以及显存的占用百分比，并可动态探测当前的 CPU 和 GPU 显卡型号。
* **媒体预览窗口与运行终端**：内置输入与结果预览标签页（视频自动转码保障播放），并在右侧提供带彩色日志输出 of YOLO 执行控制台，支持进度百分比动态刷新。

---

## 📝 贡献说明与授权

- 本项目的算法权重及基础检测部分引用自 [Wyatt-Happy/Yolo-FaceEmotionAI](https://github.com/Wyatt-Happy/Yolo-FaceEmotionAI)。
- 本项目重构修改的 UI 界面、多线程 Web 服务器、智能冲突弹窗、文件位置自动高亮以及视频 H.264 自动转码逻辑遵循 [MIT License](LICENSE)。欢迎在 GitHub 提交 Issue 和 Pull Request 进行持续迭代改进！
