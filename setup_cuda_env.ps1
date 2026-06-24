$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

python -m venv .venv-cuda

& ".\.venv-cuda\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv-cuda\Scripts\python.exe" -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
& ".\.venv-cuda\Scripts\python.exe" -m pip install -r requirements.txt

Write-Host "CUDA environment is ready: .venv-cuda"
