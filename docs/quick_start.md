# ⚡ 快速使用说明 (Quick Start)

本文档面向对命令行有一定了解、希望快速调试或二次开发的用户。

---

## 🚀 一键极速启动 (推荐)

项目内置了双击即用的 Windows 批处理启动脚本：

1. **CPU 纯算力运行**：直接双击项目根目录下的 **`一键启动服务.bat`**。
2. **GPU CUDA 加速配置**：如果你有 NVIDIA 显卡，直接双击 **`一键配置GPU环境.bat`** 进行一键环境创建。配置完成后即可双击 `一键启动服务.bat` 并在网页控制台切换 `cuda` 运行。

---

## 💻 命令行手动启动与调试

如果你希望通过终端激活虚拟环境并手动执行脚本：

### 1. 激活虚拟环境

- **CPU 环境 (.venv)**：
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- **GPU 环境 (.venv-cuda)**：
  ```powershell
  .venv-cuda\Scripts\Activate.ps1
  ```

### 2. 手动启动 Web 交互监控中心

在激活环境（推荐 CPU 环境 `.venv`）下，运行启动入口：
```powershell
python launch_web_ui.py
```
启动后服务将在本地 `http://localhost:8000` 监听。

### 3. 命令行独立推理测试

如果你不想通过网页，可以直接使用命令行执行单张图片或单个视频的识别。

#### 📷 图片识别测试
- **CPU 模式**：
  ```powershell
  .venv\Scripts\python main.py --source image --input "assets/inputs/images/lena.jpg" --no-display
  ```
- **GPU (CUDA) 模式**：
  ```powershell
  .venv-cuda\Scripts\python main_cuda.py --source image --input "assets/inputs/images/lena.jpg" --no-display
  ```

#### 🎥 视频识别与多目标跟踪测试
- **CPU 模式**：
  ```powershell
  .venv\Scripts\python main.py --source video --input "assets/inputs/videos/face_walk.mp4" --no-display
  ```
- **GPU (CUDA) 模式**：
  ```powershell
  .venv-cuda\Scripts\python main_cuda.py --source video --input "assets/inputs/videos/face_walk.mp4" --no-display
  ```

---

## 📂 素材与结果保存路径约定

- **输入素材存放**：
  - 待识别的图片：`assets/inputs/images/`
  - 待识别的视频：`assets/inputs/videos/`
- **输出结果保存**：
  - 识别完成的图片：`assets/outputs/images/` (自增命名或覆盖)
  - 识别及转码完成的视频：`assets/outputs/videos/` (自增命名或覆盖)
  - 报告截图：`assets/outputs/screenshots/`

---

## 🖥️ 运行设备状态确认

在执行推理时，控制台输出将标明当前所采用的硬件加速设备：
- `Device: cuda`：代表当前正在调用 NVIDIA GPU 进行加速推理。
- `Device: cpu`：代表当前正在调用 CPU 进行纯算力推理。
