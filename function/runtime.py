from __future__ import annotations

import torch


def resolve_device(requested_device: str = "auto") -> str:
    requested = (requested_device or "auto").lower()

    if requested == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"

    if requested == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is not available in the current Python environment.")
        return "cuda"

    if requested == "cpu":
        return "cpu"

    raise ValueError(f"Unsupported device: {requested_device}")
