import os
import sys
import json
import shutil
import urllib.parse
import subprocess
import threading
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Optional psutil for CPU/RAM metrics
try:
    import psutil
except ImportError:
    psutil = None

try:
    import winreg
except ImportError:
    winreg = None

# Global application state
run_state = {
    "status": "idle",  # "idle", "running", "completed", "error"
    "progress": 0,
    "logs": [],
    "input_file": None,
    "output_file": None,
    "device_type": None,  # "cpu" or "cuda"
    "error": None
}
current_process = None
state_lock = threading.Lock()

# Directory configuration
if getattr(sys, 'frozen', False):
    PROJECT_ROOT = Path(sys.executable).resolve().parent
else:
    PROJECT_ROOT = Path(__file__).resolve().parent

if hasattr(sys, "_MEIPASS"):
    WEB_UI_DIR = Path(sys._MEIPASS) / "web_ui"
else:
    WEB_UI_DIR = PROJECT_ROOT / "web_ui"

INPUT_IMAGES_DIR = PROJECT_ROOT / "assets" / "inputs" / "images"
INPUT_VIDEOS_DIR = PROJECT_ROOT / "assets" / "inputs" / "videos"
OUTPUT_IMAGES_DIR = PROJECT_ROOT / "assets" / "outputs" / "images"
OUTPUT_VIDEOS_DIR = PROJECT_ROOT / "assets" / "outputs" / "videos"
HISTORY_FILE = PROJECT_ROOT / "assets" / "history.json"

# Ensure dirs exist
for d in [INPUT_IMAGES_DIR, INPUT_VIDEOS_DIR, OUTPUT_IMAGES_DIR, OUTPUT_VIDEOS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def get_cpu_name():
    if not winreg:
        return "Unknown CPU"
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
        name, _ = winreg.QueryValueEx(key, "ProcessorNameString")
        winreg.CloseKey(key)
        return name.strip()
    except Exception:
        return "Unknown CPU"


def find_nvidia_smi():
    # 1. Try standard system PATH lookup
    smi = shutil.which("nvidia-smi")
    if smi:
        return smi
    # 2. Try common locations on Windows
    paths = [
        r"C:\Windows\System32\nvidia-smi.exe",
        r"C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe",
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def add_history_entry(source, input_file, device, output_file, status, error=None):
    from datetime import datetime
    import time
    
    entry = {
        "id": str(int(time.time() * 1000)),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "filename": os.path.basename(input_file),
        "source": source,
        "device": device,
        "output_file": output_file,
        "status": status,
        "error": error
    }
    
    try:
        history = []
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        history.insert(0, entry) # Add to the beginning (newest first)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Failed to write history: {e}")


def get_system_stats():
    stats = {
        "cpu_usage": 0.0,
        "ram_usage": 0.0,
        "gpu_usage": 0.0,
        "gpu_mem_used": 0.0,
        "gpu_mem_total": 0.0,
        "gpu_name": "N/A",
        "cpu_name": get_cpu_name()
    }

    # CPU/RAM
    if psutil:
        stats["cpu_usage"] = psutil.cpu_percent()
        stats["ram_usage"] = psutil.virtual_memory().percent
    else:
        # Fallback if psutil fails
        stats["cpu_usage"] = 0.0
        stats["ram_usage"] = 0.0

    # GPU (NVIDIA check)
    smi_path = find_nvidia_smi()
    if smi_path:
        try:
            # Query gpu utilization, memory used, total and name
            out = subprocess.check_output(
                [smi_path, "--query-gpu=name,utilization.gpu,memory.used,memory.total", "--format=csv,noheader,nounits"],
                text=True,
                stderr=subprocess.DEVNULL
            )
            parts = out.strip().split(",")
            if len(parts) >= 4:
                stats["gpu_name"] = parts[0].strip()
                stats["gpu_usage"] = float(parts[1].strip())
                stats["gpu_mem_used"] = float(parts[2].strip())
                stats["gpu_mem_total"] = float(parts[3].strip())
        except Exception:
            pass

    return stats


def subprocess_worker(cmd, source, input_path_str, device_type, expected_output_str):
    global run_state, current_process
    
    with state_lock:
        run_state["status"] = "running"
        run_state["progress"] = 0
        run_state["logs"] = []
        run_state["input_file"] = input_path_str
        run_state["output_file"] = None
        run_state["device_type"] = device_type
        run_state["error"] = None

    try:
        input_path = Path(input_path_str)
        expected_output = Path(expected_output_str)

        # Launch process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            universal_newlines=True,
            cwd=str(PROJECT_ROOT)
        )
        
        current_process = process
        
        for line in process.stdout:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Print to python console too
            print(f"[YOLO SUBPROCESS] {stripped}")
            
            if stripped.startswith("[PROGRESS]"):
                try:
                    pct = int(stripped.split()[1])
                    with state_lock:
                        run_state["progress"] = pct
                except Exception:
                    pass
            else:
                with state_lock:
                    run_state["logs"].append(stripped)
                    # Limit logs size
                    if len(run_state["logs"]) > 1000:
                        run_state["logs"].pop(0)

        process.wait()
        
        with state_lock:
            if process.returncode == 0:
                run_state["status"] = "completed"
                run_state["progress"] = 100
                # Use output path relative to web server directory
                # (so frontend can load it via /assets/...)
                rel_output = expected_output.relative_to(PROJECT_ROOT).as_posix()
                run_state["output_file"] = rel_output
                add_history_entry(source, input_path_str, device_type, rel_output, "completed")
            else:
                run_state["status"] = "error"
                run_state["error"] = f"Subprocess exited with error code {process.returncode}."
                add_history_entry(source, input_path_str, device_type, None, "error", run_state["error"])
                
    except Exception as e:
        with state_lock:
            run_state["status"] = "error"
            run_state["error"] = f"Failed to run subprocess: {str(e)}"
            add_history_entry(source, input_path_str, device_type, None, "error", run_state["error"])
    finally:
        current_process = None


class DashboardHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Mute default request logs to keep server console clean
        pass

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # Serve Dashboard HTML / CSS / JS
        if path == "/" or path == "/index.html":
            self.serve_file(WEB_UI_DIR / "index.html", "text/html")
            return
        elif path == "/style.css":
            self.serve_file(WEB_UI_DIR / "style.css", "text/css")
            return
        elif path == "/app.js":
            self.serve_file(WEB_UI_DIR / "app.js", "application/javascript")
            return

        # Serve static assets from project/assets folder
        if path.startswith("/assets/"):
            # Unquote spaces/special characters
            rel_path = urllib.parse.unquote(path.lstrip("/"))
            file_path = PROJECT_ROOT / rel_path
            
            # Prevent directory traversal vulnerability
            try:
                file_path.relative_to(PROJECT_ROOT)
            except ValueError:
                self.send_error(403, "Access Denied")
                return

            if file_path.is_file():
                ext = file_path.suffix.lower()
                content_type = "application/octet-stream"
                if ext in [".jpg", ".jpeg"]:
                    content_type = "image/jpeg"
                elif ext == ".png":
                    content_type = "image/png"
                elif ext == ".bmp":
                    content_type = "image/bmp"
                elif ext == ".mp4":
                    content_type = "video/mp4"
                elif ext in [".mov", ".avi", ".mkv"]:
                    content_type = "video/quicktime"
                
                self.serve_file(file_path, content_type)
                return
            else:
                self.send_error(404, "Asset Not Found")
                return

        # API Endpoints
        if path == "/api/system_stats":
            stats = get_system_stats()
            self.send_json(stats)
            return

        elif path == "/api/files":
            files_data = {
                "inputs": {
                    "images": sorted([f.name for f in INPUT_IMAGES_DIR.iterdir() if f.is_file()]),
                    "videos": sorted([f.name for f in INPUT_VIDEOS_DIR.iterdir() if f.is_file()])
                },
                "outputs": {
                    "images": sorted([f.name for f in OUTPUT_IMAGES_DIR.iterdir() if f.is_file()]),
                    "videos": sorted([f.name for f in OUTPUT_VIDEOS_DIR.iterdir() if f.is_file()])
                }
            }
            self.send_json(files_data)
            return

        elif path == "/api/run_status":
            with state_lock:
                self.send_json(run_state)
            return

        elif path == "/api/history":
            history = []
            if HISTORY_FILE.exists():
                try:
                    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                        history = json.load(f)
                except Exception:
                    pass
            self.send_json(history)
            return

        # Fallback to 404
        self.send_error(404, "Page Not Found")

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/upload":
            query = urllib.parse.parse_qs(parsed_url.query)
            filename = query.get("filename", ["file"])[0]
            
            content_length = int(self.headers.get("Content-Length", 0))
            file_data = self.rfile.read(content_length)
            
            ext = os.path.splitext(filename)[1].lower()
            if ext in [".jpg", ".jpeg", ".png", ".bmp"]:
                target_dir = INPUT_IMAGES_DIR
            elif ext in [".mp4", ".avi", ".mov", ".mkv"]:
                target_dir = INPUT_VIDEOS_DIR
            else:
                target_dir = INPUT_IMAGES_DIR
            
            target_path = target_dir / filename
            with open(target_path, "wb") as f:
                f.write(file_data)
                
            rel_path = target_path.relative_to(PROJECT_ROOT).as_posix()
            self.send_json({
                "status": "success", 
                "filename": filename,
                "path": rel_path
            })
            return

        elif path == "/api/run":
            global current_process
            if current_process is not None:
                self.send_json({"status": "error", "message": "A job is already running."}, code=400)
                return

            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode("utf-8"))

            source = params.get("source")       # "image" or "video"
            input_file = params.get("file")     # e.g., "assets/inputs/images/lena.jpg"
            device_choice = params.get("device", "cpu")  # "cpu" or "cuda"
            output_mode = params.get("output_mode", "overwrite") # "overwrite" or "new"

            # Validate local path
            local_input = PROJECT_ROOT / input_file
            if not local_input.is_file():
                self.send_json({"status": "error", "message": f"Input file not found: {input_file}"}, code=400)
                return

            # Determine the output path based on output_mode
            input_path = Path(local_input)
            suffix = input_path.suffix or (".jpg" if source == "image" else ".mp4")
            base_output_dir = OUTPUT_IMAGES_DIR if source == "image" else OUTPUT_VIDEOS_DIR

            if output_mode == "new":
                expected_output = base_output_dir / f"{input_path.stem}_result{suffix}"
                if expected_output.exists():
                    counter = 1
                    while True:
                        candidate = base_output_dir / f"{input_path.stem}_result_{counter}{suffix}"
                        if not candidate.exists():
                            expected_output = candidate
                            break
                        counter += 1
            else:  # "overwrite"
                expected_output = base_output_dir / f"{input_path.stem}_result{suffix}"
                if expected_output.exists():
                    try:
                        expected_output.unlink()
                    except Exception:
                        pass

            # Prepare commands depending on CPU (.venv) or GPU (.venv-cuda)
            # We explicitly execute python inside the correct virtual environment folder
            if device_choice == "cuda":
                python_exe = PROJECT_ROOT / ".venv-cuda" / "Scripts" / "python.exe"
                script_file = "main_cuda.py"
            else:
                python_exe = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
                script_file = "main.py"

            if not python_exe.exists():
                self.send_json({
                    "status": "error", 
                    "message": f"Virtual environment Python not found: {python_exe.relative_to(PROJECT_ROOT)}. Please ensure setup_cuda_env has been run."
                }, code=400)
                return

            cmd = [
                str(python_exe),
                script_file,
                "--source", source,
                "--input", str(local_input),
                "--output", str(expected_output),
                "--no-display"
            ]

            # Start worker thread
            thread = threading.Thread(
                target=subprocess_worker, 
                args=(cmd, source, str(local_input), device_choice, str(expected_output))
            )
            thread.start()

            self.send_json({"status": "success", "message": "Inference started."})
            return

        elif path == "/api/kill":
            if current_process is not None:
                try:
                    current_process.terminate()
                    with state_lock:
                        run_state["status"] = "idle"
                        run_state["progress"] = 0
                        run_state["error"] = "Process killed by user."
                    self.send_json({"status": "success", "message": "Process terminated."})
                except Exception as e:
                    self.send_json({"status": "error", "message": str(e)}, code=500)
            else:
                self.send_json({"status": "error", "message": "No active process to stop."}, code=400)
            return

        elif path == "/api/open_folder":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode("utf-8"))
            folder_type = params.get("type", "images")  # "images", "videos", "input_images", "input_videos", "output_images", "output_videos"
            
            if folder_type == "input_images":
                target = INPUT_IMAGES_DIR
            elif folder_type == "input_videos":
                target = INPUT_VIDEOS_DIR
            elif folder_type == "output_images" or folder_type == "images":
                target = OUTPUT_IMAGES_DIR
            elif folder_type == "output_videos" or folder_type == "videos":
                target = OUTPUT_VIDEOS_DIR
            else:
                target = PROJECT_ROOT
                
            try:
                # Use subprocess to run explorer.exe to avoid os.startfile issues on some Windows systems
                subprocess.Popen(["explorer.exe", str(target.resolve())])
                self.send_json({"status": "success"})
            except Exception as e:
                # Fallback to os.startfile
                try:
                    os.startfile(str(target))
                    self.send_json({"status": "success"})
                except Exception as e2:
                    self.send_json({"status": "error", "message": f"explorer: {str(e)}, startfile: {str(e2)}"}, code=500)
            return

        elif path == "/api/open_file":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode("utf-8"))
            rel_file = params.get("file") # e.g. "assets/outputs/images/lena_result.jpg"
            
            target = PROJECT_ROOT / rel_file
            try:
                if target.is_file():
                    os.startfile(str(target))
                    self.send_json({"status": "success"})
                else:
                    self.send_json({"status": "error", "message": "File not found"}, code=404)
            except Exception as e:
                self.send_json({"status": "error", "message": str(e)}, code=500)
            return

        elif path == "/api/open_file_location":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode("utf-8"))
            rel_file = params.get("file") # e.g. "assets/outputs/images/lena_result.jpg"
            
            target = PROJECT_ROOT / rel_file
            try:
                if target.is_file():
                    subprocess.Popen(["explorer.exe", "/select,", str(target.resolve())])
                    self.send_json({"status": "success"})
                else:
                    self.send_json({"status": "error", "message": "File not found"}, code=404)
            except Exception as e:
                self.send_json({"status": "error", "message": str(e)}, code=500)
            return

        elif path == "/api/rename_file":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode("utf-8"))
            rel_file = params.get("file")      # e.g. "assets/outputs/images/lena_result.jpg"
            new_name = params.get("new_name")  # e.g. "lena_processed.jpg"
            
            if not rel_file or not new_name:
                self.send_json({"status": "error", "message": "Missing file or new_name"}, code=400)
                return
                
            old_path = PROJECT_ROOT / rel_file
            if not old_path.is_file():
                self.send_json({"status": "error", "message": "File not found"}, code=404)
                return
                
            # Prevent directory traversal
            new_name = os.path.basename(new_name)
            new_path = old_path.parent / new_name
            
            if new_path.exists():
                self.send_json({"status": "error", "message": "A file with this name already exists."}, code=400)
                return
                
            try:
                old_path.rename(new_path)
                new_rel_file = new_path.relative_to(PROJECT_ROOT).as_posix()
                
                # Update history.json
                if HISTORY_FILE.exists():
                    try:
                        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                            history = json.load(f)
                        updated = False
                        for entry in history:
                            if entry.get("output_file") == rel_file:
                                entry["output_file"] = new_rel_file
                                entry["filename"] = new_name
                                updated = True
                        if updated:
                            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                                json.dump(history, f, indent=2, ensure_ascii=False)
                    except Exception as he:
                        print(f"Failed to update history on rename: {he}")
                        
                self.send_json({
                    "status": "success",
                    "new_path": new_rel_file
                })
            except Exception as e:
                self.send_json({"status": "error", "message": str(e)}, code=500)
            return

        elif path == "/api/delete_history":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode("utf-8")) if content_length > 0 else {}
            
            entry_id = params.get("id") # None means delete all
            delete_files = params.get("delete_files", True)
            
            if HISTORY_FILE.exists():
                try:
                    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                        history = json.load(f)
                    
                    new_history = []
                    for entry in history:
                        if entry_id is None or entry["id"] == entry_id:
                            if delete_files and entry.get("output_file"):
                                file_path = PROJECT_ROOT / entry["output_file"]
                                if file_path.is_file():
                                    try:
                                        file_path.unlink()
                                    except Exception:
                                        pass
                        else:
                            new_history.append(entry)
                            
                    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                        json.dump(new_history, f, indent=2, ensure_ascii=False)
                except Exception as e:
                    self.send_json({"status": "error", "message": str(e)}, code=500)
                    return
            self.send_json({"status": "success"})
            return

        self.send_error(404, "Not Found")

    def serve_file(self, file_path, content_type):
        try:
            with open(file_path, "rb") as f:
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(file_path.stat().st_size))
                # Disable caching entirely to ensure dynamic changes are instantly visible
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
                self.end_headers()
                shutil.copyfileobj(f, self.wfile)
        except Exception:
            self.send_error(500, "Internal Server Error")

    def send_json(self, data, code=200):
        try:
            payload = json.dumps(data).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except Exception:
            self.send_error(500, "Internal Server Error")


def run(port=8000):
    server_address = ("", port)
    httpd = ThreadingHTTPServer(server_address, DashboardHTTPHandler)
    print(f"YOLO Emotion Dashboard Server running on http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()


if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run(port)
