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

## 🚀 环境准备与运行（极速部署与启动指南）

无论您是零基础新手还是进行课程演示的老师，只需按照以下步骤，即可在一分钟内快速完成部署与运行：

### 第一步：安装 Python 环境（最基础）

本项目是基于 Python 语言开发的，若您的电脑尚未安装 Python，请按以下步骤操作：

1. **下载 Python 3.12**：
   - 官方下载链接：[Python 3.12.0 官方下载](https://www.python.org/downloads/release/python-3120/) (滑动到网页底部选择 **Windows installer (64-bit)** 下载)。
2. **安装时的关键步骤 (务必注意！)**：
   - 双击打开下载好的 Python 安装包。
   - **在安装界面的最下方，必须勾选：`[√] Add python.exe to PATH`**（将 Python 添加到系统环境变量中，这非常关键！）。
   - 点击 **`Install Now`** 直到安装完成即可。

> 💡 **如果您的电脑上已经安装了其他版本的 Python (例如 3.8、3.9、3.10、3.11)？**
> 不需要重新安装 3.12！本项目做了**全版本兼容与自适应设计**：
> 1. 项目的依赖配置文件（`requirements.txt`）会自动识别您的 Python 版本并自动下载安装对应版本的库（如 `numpy` 等）。
> 2. 一键启动脚本会自动探测并使用您现有的 Python 3.8 ~ 3.12 任意版本来创建隔离环境并运行。
> 3. *注：不建议使用极新版 Python 3.13 及以上，因为深度学习框架 PyTorch 官方对它的兼容性尚不稳定。*

> 💡 **如果您忘记勾选 PATH 怎么办？**
> 没关系！项目内置的一键启动脚本具有**智能检索功能**，即使您没有勾选该选项，脚本也会自动尝试在 Windows 的常见默认安装路径中寻找并调用 Python，保障服务正常运行。

---

### 第二步：双击一键运行（推荐：CPU 纯算力版）

这是最快看到运行效果的方式，不需要您手动输入任何命令行：

1. 在解压后的项目根目录下，直接双击运行 **`一键启动服务.bat`**。
2. 启动器会自动帮您完成以下工作：
   - 检测您电脑上的 Python 运行环境。
   - 自动创建 Python 独立虚拟隔离环境 (`.venv`)。
   - 自动通过**国内清华大学镜像源**高速下载并安装所有需要的依赖包（避免了因为国外服务器连接超时导致的报错）。
   - 自动启动后台服务并**为您拉起默认浏览器**打开控制中心网页（`http://localhost:8000`）。

> 💡 **以后每次启动，都只需双击运行 `一键启动服务.bat` 即可！**

---

### 第三步：配置 GPU/CUDA 显卡加速（可选：进阶版，支持 20/30/40/50 系显卡）

如果您的电脑配备了 NVIDIA 独立显卡（支持 RTX 20/30/40/50 系列等所有主流显卡），并且希望获得流畅的实时视频识别速度，可以配置 GPU 加速环境：

1. **显卡驱动要求**：
   - 请确保您的电脑已经更新了最新的 NVIDIA 官方显卡驱动。
   - **原生支持 50 系显卡**：本项目的一键 GPU 配置脚本默认采用最新的 **CUDA 12.8** 核心库，完全兼容并原生支持 RTX 5080 / 5090 等最新 50 系列（Blackwell 架构）显卡。
   - 💡 *特大福利：只要您更新了最新的 NVIDIA 显卡驱动，您甚至不需要手动下载安装巨型 CUDA Toolkit 软件！双击一键部署脚本后，系统会自动下载包含 CUDA 运行时环境的 PyTorch 核心包，直接实现显卡加速。*
2. **双击一键部署**：
   - 在项目根目录下，直接双击运行 **`一键配置GPU环境.bat`**。
   - 脚本会自动创建 GPU 专属虚拟环境 (`.venv-cuda`)，并自动为您下载安装 GPU 版的 PyTorch 深度学习计算库及相关依赖。
   - *(由于 GPU 核心库较大，需要几分钟下载时间，请保持网络畅通)*。
3. **在网页端开启显卡加速**：
   - 成功配置后，双击运行 `一键启动服务.bat` 打开网页。
   - 在网页控制中心右上角切换版本环境为 `GPU 显卡 (.venv-cuda)`，启动情绪识别即可启用极速显卡推理。

---

### 💻 开发者调试/手动运行（备用）

如果您熟悉命令行操作，可以在激活相应虚拟环境后，通过终端运行：

- **CPU 版手动运行**：
  ```bash
  .venv\Scripts\python launch_web_ui.py
  ```
- **GPU 版手动运行**：
  ```powershell
  .venv-cuda\Scripts\python launch_web_ui.py
  ```


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
