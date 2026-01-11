"""
Reproducibility utilities for UET tests.

This module provides tools for ensuring reproducible test results:
- Seed locking for all random number generators
- Dataset hashing for verification
- Artifact generation for audit trails

Usage:
    from research_uet.core.reproducibility import lock_all_seeds, hash_dataset
    lock_all_seeds(42)  # At top of every test file
"""

import hashlib
import json
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

import numpy as np

# UET Standard Seed
UET_SEED = 42


def lock_all_seeds(seed: int = UET_SEED) -> None:
    """
    Lock all random seeds for reproducibility.

    Call this at the top of every test file to ensure deterministic results.

    Args:
        seed: Random seed value (default: 42)

    Example:
        >>> lock_all_seeds(42)
        >>> np.random.rand()  # Same result every time
    """
    random.seed(seed)
    np.random.seed(seed)

    # PyTorch if available
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass

    # TensorFlow if available
    try:
        import tensorflow as tf

        tf.random.set_seed(seed)
    except ImportError:
        pass


def hash_dataset(data: Union[np.ndarray, bytes, str]) -> str:
    """
    Generate SHA256 hash of dataset for verification.

    Args:
        data: NumPy array, bytes, or string to hash

    Returns:
        First 16 characters of SHA256 hash

    Example:
        >>> data = np.array([1.0, 2.0, 3.0])
        >>> hash_dataset(data)
        'a1b2c3d4e5f67890'
    """
    if isinstance(data, np.ndarray):
        data_bytes = data.tobytes()
    elif isinstance(data, str):
        data_bytes = data.encode("utf-8")
    else:
        data_bytes = data

    return hashlib.sha256(data_bytes).hexdigest()[:16]


def hash_file(filepath: Union[str, Path]) -> str:
    """
    Generate SHA256 hash of a file.

    Args:
        filepath: Path to file

    Returns:
        Full SHA256 hash
    """
    filepath = Path(filepath)
    return hashlib.sha256(filepath.read_bytes()).hexdigest()


def generate_artifact(
    results: Dict[str, Any],
    dataset_hash: Optional[str] = None,
    topic: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate reproducibility artifact for test results.

    Args:
        results: Test results dictionary
        dataset_hash: Hash of input dataset
        topic: Topic name (e.g., "0.1_Galaxy_Rotation")

    Returns:
        Complete artifact with metadata
    """
    artifact = {
        "timestamp": datetime.now().isoformat(),
        "uet_version": "0.8.7",
        "python_version": sys.version.split()[0],
        "numpy_version": np.__version__,
        "seed": UET_SEED,
        "topic": topic,
        "dataset_hash": dataset_hash,
        "results": results,
    }

    # Add optional dependencies
    try:
        import scipy

        artifact["scipy_version"] = scipy.__version__
    except ImportError:
        pass

    return artifact


def save_artifact(artifact: Dict[str, Any], output_path: Union[str, Path]) -> Path:
    """
    Save artifact to JSON file.

    Args:
        artifact: Artifact dictionary
        output_path: Output file path

    Returns:
        Path to saved file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2, default=str)

    return output_path


def verify_reproducibility(
    result1: Dict[str, Any], result2: Dict[str, Any], tolerance: float = 1e-10
) -> bool:
    """
    Verify that two result sets are reproducible within tolerance.

    Args:
        result1: First result dictionary
        result2: Second result dictionary
        tolerance: Numerical tolerance for comparison

    Returns:
        True if results match
    """
    for key in result1:
        if key not in result2:
            return False

        v1, v2 = result1[key], result2[key]

        if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
            if abs(v1 - v2) > tolerance:
                return False
        elif v1 != v2:
            return False

    return True


# Version info for dependency tracking
def get_environment_info() -> Dict[str, str]:
    """
    Get current environment information for reproducibility.

    Returns:
        Dictionary of package versions
    """
    info = {
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "platform": sys.platform,
    }

    optional_packages = ["scipy", "pandas", "matplotlib", "torch", "tensorflow"]

    for pkg in optional_packages:
        try:
            module = __import__(pkg)
            info[pkg] = module.__version__
        except ImportError:
            pass

    return info
