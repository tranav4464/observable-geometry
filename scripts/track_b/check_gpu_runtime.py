"""Verify the isolated Track B CUDA runtime and its dense linear-algebra path."""
from __future__ import annotations

import json

import torch


def main() -> None:
    if not torch.cuda.is_available():
        raise SystemExit("FAIL: CUDA is not visible to the Track B PyTorch environment")

    generator = torch.Generator(device="cpu").manual_seed(20261022)
    matrix = torch.randn((96, 96), generator=generator, dtype=torch.float64)
    rhs = torch.randn((96, 8), generator=generator, dtype=torch.float64)
    covariance = matrix @ matrix.T + 0.5 * torch.eye(96, dtype=torch.float64)
    reference = torch.linalg.solve(covariance, rhs)
    device = torch.device("cuda:0")
    actual = torch.linalg.solve(covariance.to(device), rhs.to(device)).cpu()
    error = float(torch.max(torch.abs(reference - actual)))
    if not torch.isfinite(actual).all() or error > 1e-9:
        raise SystemExit(f"FAIL: CPU/CUDA solve mismatch: max_abs_error={error:.3g}")

    print(json.dumps({
        "status": "PASS",
        "torch_version": torch.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "gpu": torch.cuda.get_device_name(0),
        "double_precision_solve_max_abs_error": error,
        "smoke_test": "96x96 SPD solve, CPU/CUDA parity",
    }, indent=2))


if __name__ == "__main__":
    main()
