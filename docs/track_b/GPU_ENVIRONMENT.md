# Track B GPU environment

**Verified 22 October 2026.** The host exposes an NVIDIA GeForce RTX 4050 Laptop GPU. Track B uses an isolated `.venv_trackb_gpu` environment; it does not modify `.venv_tracka_clean` or `.venv`.

The verified stack is Python 3.10.11, PyTorch 2.14.0 with CUDA 13.0 (`torch==2.14.0+cu130`), and NumPy 2.2.6. The machine reports NVIDIA driver 591.74. PyTorch's official version guidance lists CUDA 13.0 wheels for Windows, and its 2.14 release notes list CUDA 13.0 among supported binary configurations. See the [official PyTorch previous-version commands](https://pytorch.org/get-started/previous-versions/) and [2.14 release notes](https://pytorch.org/blog/pytorch-2-14-release-blog/).

Recreate the environment from the repository root in PowerShell:

```powershell
python -m venv .venv_trackb_gpu
.venv_trackb_gpu\Scripts\python.exe -m pip install --upgrade pip
.venv_trackb_gpu\Scripts\python.exe -m pip install -r requirements-trackb-gpu.txt --extra-index-url https://download.pytorch.org/whl/cu130
.venv_trackb_gpu\Scripts\python.exe scripts\track_b\check_gpu_runtime.py
```

The smoke check confirms CUDA discovery, executes a 96×96 positive-definite covariance solve in float64 on CPU and GPU, and requires maximum absolute disagreement below `1e-9`. Verified result: **PASS**, GPU `NVIDIA GeForce RTX 4050 Laptop GPU`, CUDA runtime `13.0`, maximum absolute error `3.397282455352979e-14`.

This proves the runtime and dense linear-algebra path work. It is not a scientific result, a speedup benchmark, or evidence that the eventual analysis benefits from GPU acceleration. CPU remains the correctness reference; benchmark representative workloads before choosing execution device. The initial installation is about 2 GB.
