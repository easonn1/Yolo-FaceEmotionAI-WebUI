@echo off
chcp 65001 >nul
title YOLO 人脸表情识别监控中心 - 一键启动器
echo ==================================================
echo      YOLO 人脸表情识别监控中心 - 一键启动器
echo ==================================================
echo.

:: 1. 检测 Python 是否安装，并在没有 PATH 的情况下进行智能检索
set "PYTHON_CMD=python"
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] 未在系统 PATH 环境变量中检测到 'python' 命令，正在尝试搜索 Windows 默认路径...
    
    :: 搜索 AppData 局部安装路径 (常见的 Python 3.10 / 3.11 / 3.12 / 3.13 默认路径)
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
    for /d %%d in ("C:\Program Files (x86)\Python*") do (
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
    echo --------------------------------------------------
    echo 解决步骤：
    echo 1. 请先下载并安装 Python (推荐使用 3.10 或 3.12 版本)。
    echo    官方下载地址: https://www.python.org/downloads/
    echo 2. 安装时请务必勾选 "[√] Add Python.exe to PATH" 选项！
    echo --------------------------------------------------
    echo.
    pause
    exit /b
)

:python_found
if "%PYTHON_CMD%" neq "python" (
    echo [提示] 在默认路径下成功找到 Python: "%PYTHON_CMD%"
)

:: 2. 检测并创建 CPU 虚拟环境并安装依赖
if not exist ".venv" (
    echo [提示] 首次运行，正在为您创建 CPU 虚拟环境并自动配置依赖...
    echo (此过程仅在第一次运行时执行，需要连接网络，请耐心等待数分钟)
    echo.
    
    "%PYTHON_CMD%" -m venv .venv
    if %errorlevel% neq 0 (
        echo [错误] 创建虚拟环境 (.venv) 失败，请检查 Python 安装是否完整。
        pause
        exit /b
    )
    
    echo 正在使用清华大学镜像源升级 pip...
    .\.venv\Scripts\python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
    if %errorlevel% neq 0 (
        echo [提示] 清华镜像连接失败，正在尝试使用官方源升级 pip...
        .\.venv\Scripts\python -m pip install --upgrade pip >nul 2>&1
    )
    
    echo 正在通过国内镜像加速安装项目依赖 (requirements.txt)...
    .\.venv\Scripts\pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if %errorlevel% neq 0 (
        echo [提示] 镜像站下载失败，正在尝试使用默认官方源重新安装...
        .\.venv\Scripts\pip install -r requirements.txt
        if %errorlevel% neq 0 (
            echo [错误] 依赖安装失败，请检查您的网络连接并重试。
            pause
            exit /b
        )
    )
    echo.
    echo [成功] 虚拟环境与依赖配置完成！
    echo.
)

:: 3. 运行 Web UI 启动服务
echo 正在为您启动 Web 监控中心...
.\.venv\Scripts\python launch_web_ui.py

if %errorlevel% neq 0 (
    echo.
    echo [提示] 启动脚本报错或退出，正在尝试使用已编译的二进制启动器运行...
    if exist "launch_web_ui.exe" (
        launch_web_ui.exe
    ) else (
        echo [错误] 启动服务失败！请检查控制台报错日志。
    )
)

pause
