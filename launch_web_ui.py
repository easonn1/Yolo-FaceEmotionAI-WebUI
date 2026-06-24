import os
import sys
import time
import threading
import webbrowser
from pathlib import Path
import web_server

def main():
    if getattr(sys, 'frozen', False):
        project_root = Path(sys.executable).resolve().parent
    else:
        project_root = Path(__file__).resolve().parent

    print("==================================================")
    print("     YOLO 人脸表情识别监控中心启动工具             ")
    print("==================================================")
    print("正在启动 Web 服务...")
    
    # Start web server in a daemon thread so it exits when the main thread exits
    server_thread = threading.Thread(target=web_server.run, args=(8000,), daemon=True)
    server_thread.start()
    
    # Give the server a moment to start
    time.sleep(1.2)
    
    url = "http://localhost:8000"
    print(f"已在后台启动 Web 服务。")
    print(f"即将为您打开浏览器访问: {url}")
    print("--------------------------------------------------")
    print("【注意】请勿关闭当前窗口，关闭它将终止服务。")
    print("按 Ctrl + C 或直接关闭窗口可以停止运行并退出。")
    print("==================================================")
    
    try:
        # Open default web browser
        webbrowser.open(url)
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止 Web 服务...")
        print("服务已停止。感谢使用！")

if __name__ == "__main__":
    main()
