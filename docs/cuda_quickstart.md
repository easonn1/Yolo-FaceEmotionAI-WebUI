# CUDA / GPU Version Quickstart

This project now supports a second GPU environment without changing the existing CPU environment.

## Create the GPU environment

Run this in the project root:

```powershell
.\setup_cuda_env.ps1
```

It will:

- create `.venv-cuda`
- install CUDA-enabled PyTorch
- install the rest of the project dependencies

## Verify CUDA

```powershell
.\.venv-cuda\Scripts\python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
```

If the last line is `True`, the GPU environment is ready.

## Run image inference on GPU

```powershell
.\.venv-cuda\Scripts\python main_cuda.py --source image --input "assets/inputs/images/lena.jpg" --no-display
```

## Run video inference on GPU

```powershell
.\.venv-cuda\Scripts\python main_cuda.py --source video --input "assets/inputs/videos/face_walk.mp4" --no-display
```

## Run the GUI on GPU

```powershell
.\.venv-cuda\Scripts\python launch_gui_cuda.py
```

## Keep the CPU version unchanged

The existing CPU environment still works:

```powershell
.\.venv\Scripts\python main.py --source image --input "assets/inputs/images/lena.jpg" --no-display
```
