"""Check the Phase 1 Python and CUDA environment; exit nonzero if it is unusable."""

from __future__ import annotations

import importlib
import sys
from importlib.metadata import PackageNotFoundError, version


PACKAGES = {
    "torch": "torch",
    "torchvision": "torchvision",
    "torchaudio": "torchaudio",
    "transformers": "transformers",
    "sklearn": "scikit-learn",
    "xgboost": "xgboost",
    "catboost": "catboost",
    "optuna": "optuna",
    "pandas": "pandas",
    "numpy": "numpy",
    "pyarrow": "pyarrow",
    "yaml": "PyYAML",
    "tqdm": "tqdm",
    "fastapi": "fastapi",
    "pydantic": "pydantic",
}


def main() -> int:
    print(f"Python: {sys.version.split()[0]}")
    ok = sys.version_info >= (3, 10)
    if not ok:
        print("Python 3.10 or newer is required")

    missing = []
    for module, distribution in PACKAGES.items():
        try:
            importlib.import_module(module)
            print(f"{distribution}: {version(distribution)}")
        except (ImportError, OSError, PackageNotFoundError) as exc:
            missing.append(distribution)
            print(f"{distribution}: unavailable ({exc})")

    try:
        import torch

        cuda_available = torch.cuda.is_available()
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA Available: {cuda_available}")
        print(f"CUDA runtime: {torch.version.cuda or 'unavailable'}")
        if cuda_available:
            for index in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(index)
                print(f"GPU {index}: {props.name}, VRAM: {props.total_memory / 1024**3:.2f} GiB")
        else:
            ok = False
    except (ImportError, OSError) as exc:
        print(f"PyTorch unavailable: {exc}")
        print("CUDA Available: False")
        ok = False

    if missing:
        print("Missing packages: " + ", ".join(missing))
    return 0 if ok and not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
