"""Shared MATLAB and dataset helpers for the Cheng preparation scripts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import h5py
import numpy as np
from scipy.io import loadmat


CLASS_NAMES = {1: "meningioma", 2: "glioma", 3: "pituitary"}
EXPECTED_CLASS_COUNTS = {1: 708, 2: 1426, 3: 930}


def stable_sample_id(relative_path: str) -> str:
    normalized = relative_path.replace("\\", "/")
    return "cheng_" + hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _field(value: Any, key: str) -> Any:
    if isinstance(value, dict):
        return value.get(key)
    if isinstance(value, np.ndarray) and value.dtype.names and key in value.dtype.names:
        return value[key].squeeze()
    if isinstance(value, np.void) and value.dtype.names and key in value.dtype.names:
        return value[key]
    return getattr(value, key, None)


def _matlab_array(value: np.ndarray) -> np.ndarray:
    """Convert HDF5's reversed MATLAB dimension order to MATLAB array order."""
    if value.ndim > 1:
        return np.transpose(value, axes=tuple(reversed(range(value.ndim))))
    return value


def _hdf5_value(handle: h5py.File, value: Any) -> Any:
    if isinstance(value, h5py.Dataset):
        raw = value[()]
        if h5py.check_dtype(ref=value.dtype) is not None:
            refs = np.asarray(raw)
            resolved = []
            for ref in refs.ravel(order="F"):
                resolved.append(_hdf5_value(handle, handle[ref]) if ref else None)
            if len(resolved) == 1:
                return resolved[0]
            return np.asarray(resolved, dtype=object).reshape(refs.shape, order="F")
        return _matlab_array(np.asarray(raw))
    if isinstance(value, h5py.Group):
        return {name: _hdf5_value(handle, member) for name, member in value.items()}
    return value


def read_cjdata(path: Path) -> tuple[dict[str, Any], str]:
    """Read a standard MAT struct or MATLAB 7.3 HDF5 cjdata struct."""
    try:
        contents = loadmat(path, struct_as_record=False, squeeze_me=True)
        cjdata = contents.get("cjdata")
        if cjdata is None:
            raise ValueError("MAT file does not contain cjdata")
        fields = {name: _field(cjdata, name) for name in
                  ("label", "PID", "image", "tumorBorder", "tumorMask")}
        return fields, "scipy"
    except NotImplementedError:
        pass
    except ValueError as error:
        # MATLAB 7.3 files may be recognized by SciPy as unsupported before
        # their HDF5 representation is examined.
        if not path.read_bytes()[:19].startswith(b"MATLAB 7.3 MAT-file"):
            raise error

    with h5py.File(path, "r") as handle:
        if "cjdata" not in handle:
            raise ValueError("MAT file does not contain cjdata")
        group = handle["cjdata"]
        if not isinstance(group, h5py.Group):
            raise ValueError("cjdata is not a MATLAB struct group")
        fields = {name: _hdf5_value(handle, group[name]) if name in group else None
                  for name in ("label", "PID", "image", "tumorBorder", "tumorMask")}
    return fields, "hdf5-mat73"


def scalar_number(value: Any, field_name: str) -> float:
    if value is None:
        raise ValueError(f"Missing required cjdata.{field_name}")
    array = np.asarray(value)
    if array.size != 1:
        raise ValueError(f"cjdata.{field_name} must contain exactly one value")
    number = float(array.reshape(-1)[0])
    if not np.isfinite(number):
        raise ValueError(f"cjdata.{field_name} is not finite")
    return number


def patient_id_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, bytes):
        text = value.decode("utf-8", errors="strict")
        return text if text.strip() else None
    if isinstance(value, str):
        return value if value.strip() else None
    array = np.asarray(value)
    if array.dtype.kind in "ui":
        codes = [int(x) for x in array.ravel(order="F") if int(x) != 0]
        try:
            text = bytes(np.asarray(codes, dtype="<u2").tobytes()).decode("utf-16-le")
        except UnicodeDecodeError:
            text = "".join(chr(code) for code in codes)
        return text if text.strip() else None
    if array.dtype.kind in "US":
        text = "".join(str(x) for x in array.ravel(order="F")).replace("\x00", "")
        return text if text.strip() else None
    if array.size == 1:
        text = str(array.reshape(-1)[0])
        return text if text.strip() else None
    return None


def native_array(value: Any) -> np.ndarray | None:
    if value is None:
        return None
    if isinstance(value, (bytes, str)):
        return np.asarray(value)
    return np.asarray(value)


def json_value(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)

