@echo off
chcp 65001 >nul
title YOLO 人脸表情识别监控中心 - 一键启动器
echo ==================================================
echo      YOLO 人脸表情识别监控中心 - 一键启动器
echo ==================================================
echo.

:: 1. 检测 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python 环境！
    echo 请先安装 Python 3.12 (并务必勾选 "Add Python to PATH")。
    echo 官方下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b
)

:: 2. 检测并创建 CPU 虚拟环境并安装依赖
if not exist ".venv" (
    echo [提示] 首次运行，正在为您创建虚拟环境并安装依赖，这需要几分钟时间...
    echo.
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [错误] 创建虚拟环境失败，请检查 Python 安装是否完整。
        pause
        exit /b
    )
    echo 正在升级 pip...
    .\.venv\Scripts\python -m pip install --upgrade pip >nul 2>&1
    echo 正在安装项目依赖 (requirements.txt)...
    .\.venv\Scripts\pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败，请检查网络连接后重试。
        pause
        exit /b
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
    echo [提示] 正在尝试使用已编译的 EXE 启动...
    if exist "launch_web_ui.exe" (
        launch_web_ui.exe
    ) else (
        echo [错误] 启动服务失败！请检查控制台报错日志。
    )
)

pause
