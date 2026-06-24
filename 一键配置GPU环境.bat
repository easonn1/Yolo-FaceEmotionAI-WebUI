@echo off
chcp 936 >nul
title YOLO 人脸表情识别监控中心 - 一键配置 GPU 环境
echo ==================================================
echo      YOLO 人脸表情识别监控中心 - 一键配置 GPU 环境
echo ==================================================
echo.
echo [提示] 运行此配置前，请确保：
echo 1. 本机配置了 NVIDIA 显卡 (如 RTX 30/40/50 系列)
echo 2. 已安装 NVIDIA 显卡驱动以及 CUDA Toolkit 驱动开发包。
echo.

:: 1. 检测 Python 是否安装，并在没有 PATH 的情况下进行智能检索
set "PYTHON_CMD=python"
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] 未在系统 PATH 环境变量中检测到 'python' 命令，正在尝试搜索 Windows 默认路径...
    
    :: 搜索 AppData 局部安装路径
    for /d %%d in ("%USERPROFILE%\AppData\Local\Programs\Python\Python*") do (
        if exist "%%d\python.exe" (
            set "PYTHON_CMD=%%d\python.exe"
            goto :python_found
        )
    )
    
    :: 搜索 Program Files 全局安装路径
    for /d %%d in ("C:\Program Files\Python*") do (
        if exist "%%d\python.exe" (
            set "PYTHON_CMD=%%d\python.exe"
            goto :python_found
        )
    )
    
    :: 搜索 C 盘根目录
    for /d %%d in ("C:\Python*") do (
        if exist "%%d\python.exe" (
            set "PYTHON_CMD=%%d\python.exe"
            goto :python_found
        )
    )
    
    echo [错误] 未检测到 Python 运行环境！
    echo 请先安装 Python (推荐 3.10 或 3.12 版本) 并勾选 "Add Python.exe to PATH"。
    pause
    exit /b
)

:python_found
if "%PYTHON_CMD%" neq "python" (
    echo [提示] 在默认路径下成功找到 Python: "%PYTHON_CMD%"
)

:: 2. 创建 GPU 虚拟环境并配置依赖
if not exist ".venv-cuda" (
    echo.
    echo 正在为您创建 GPU 虚拟环境 (.venv-cuda)...
    "%PYTHON_CMD%" -m venv .venv-cuda
    if %errorlevel% neq 0 (
        echo [错误] 创建 GPU 虚拟环境失败！
        pause
        exit /b
    )
)

echo.
echo 正在升级 .venv-cuda 中的 pip...
.\.venv-cuda\Scripts\python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
if %errorlevel% neq 0 (
    .\.venv-cuda\Scripts\python -m pip install --upgrade pip >nul 2>&1
)

echo.
echo 正在为您安装 NVIDIA GPU 加速版 PyTorch (这需要下载约 2GB 数据，请保持网络畅通)...
.\.venv-cuda\Scripts\python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
if %errorlevel% neq 0 (
    echo [警告] CUDA 版本的 PyTorch 安装失败。
    echo 尝试使用默认源进行安装...
    .\.venv-cuda\Scripts\python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    if %errorlevel% neq 0 (
        echo [错误] GPU 核心库安装失败！请检查您的网络连接并重试。
        pause
        exit /b
    )
)

echo.
echo 正在安装项目其他依赖 (requirements.txt)...
.\.venv-cuda\Scripts\python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if %errorlevel% neq 0 (
    .\.venv-cuda\Scripts\python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [错误] 项目依赖安装失败！
        pause
        exit /b
    )
)

echo.
echo ==================================================
echo [成功] GPU/CUDA 加速环境配置成功！
echo 现在您可以在 Web UI 控制中心中随时点选切换为 GPU (cuda) 进行识别了。
echo ==================================================
echo.
pause
