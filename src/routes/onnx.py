#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
:mod:`onnx` module
==================

This module defines the FastAPI routes used to export, store, and serve
client-specific ONNX models.

:author: Pather Stevenson
:date: March 2026
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import torch
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from routes.dependency import get_tracker
from tracker.ExportLRN import replace_crossmaplrn_for_onnx

router = APIRouter(prefix="/onnx", tags=["onnx"])

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts" / "onnx"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_ONNX_OPSET = 18

_CLIENT_LOCKS: Dict[str, threading.Lock] = {}
_CLIENT_LOCKS_GUARD = threading.Lock()


class OnnxExportResponse(BaseModel):
    client_id: str
    status: str
    model_version: str
    onnx_filename: str
    onnx_path: str


class OnnxStatusResponse(BaseModel):
    client_id: str
    training_status: str = "unknown"
    export_status: str = "unknown"
    has_onnx: bool
    model_version: str | None = None
    updated_at: str | None = None


class OnnxMetadataResponse(BaseModel):
    client_id: str
    model_type: str
    model_version: str
    created_at: str
    onnx_path: str
    opset: int
    input_names: List[str]
    output_names: List[str]
    input_shapes: Dict[str, List[int | str]]
    output_shapes: Dict[str, List[int | str]]
    dtype: str
    preprocessing: Dict[str, str] = Field(default_factory=dict)
    training_status: str = "unknown"
    export_status: str = "ready"
    model_name: str | None = None
    margin: int | None = None


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _client_lock(client_id: str) -> threading.Lock:
    with _CLIENT_LOCKS_GUARD:
        if client_id not in _CLIENT_LOCKS:
            _CLIENT_LOCKS[client_id] = threading.Lock()
        return _CLIENT_LOCKS[client_id]


def _safe_client_id(client_id: str) -> str:
    stripped = client_id.strip()
    if not stripped:
        raise HTTPException(status_code=400, detail="client_id cannot be empty")

    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
    if any(ch not in allowed for ch in stripped):
        raise HTTPException(
            status_code=400,
            detail="client_id contains forbidden characters",
        )
    return stripped


def _client_dir(client_id: str) -> Path:
    client_path = ARTIFACTS_DIR / client_id
    client_path.mkdir(parents=True, exist_ok=True)
    return client_path


def _latest_dir(client_id: str) -> Path:
    latest_path = _client_dir(client_id) / "latest"
    latest_path.mkdir(parents=True, exist_ok=True)
    return latest_path


def _registry_path(client_id: str) -> Path:
    return _client_dir(client_id) / "registry.json"


def _read_registry(client_id: str) -> Dict[str, Any]:
    path = _registry_path(client_id)
    if not path.exists():
        return {
            "client_id": client_id,
            "training_status": "unknown",
            "export_status": "unknown",
            "latest": None,
            "history": [],
        }

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid registry.json for client_id={client_id}: {exc}",
        ) from exc


def _write_registry(client_id: str, data: Dict[str, Any]) -> None:
    path = _registry_path(client_id)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _update_registry_status(
    client_id: str,
    *,
    training_status: str | None = None,
    export_status: str | None = None,
) -> Dict[str, Any]:
    registry = _read_registry(client_id)

    if training_status is not None:
        registry["training_status"] = training_status

    if export_status is not None:
        registry["export_status"] = export_status

    registry["updated_at"] = _utc_now_iso()
    _write_registry(client_id, registry)
    return registry


def _get_shared_model(gaze_tracker) -> torch.nn.Module:
    if gaze_tracker is None:
        raise HTTPException(
            status_code=500,
            detail="Shared gaze_tracker is not available.",
        )

    candidate_attrs = [
        "model",
        "gaze_model",
        "net",
        "network",
    ]

    for attr in candidate_attrs:
        if hasattr(gaze_tracker, attr):
            model = getattr(gaze_tracker, attr)
            if isinstance(model, torch.nn.Module):
                return model

    if isinstance(gaze_tracker, torch.nn.Module):
        return gaze_tracker

    raise HTTPException(
        status_code=500,
        detail=(
            "Unable to find a torch.nn.Module inside gaze_tracker. "
            "Adapt `_get_shared_model()` to your actual structure."
        ),
    )


def _infer_model_type(model: torch.nn.Module) -> str:
    return model.__class__.__name__


def _get_tracker_model_name(gaze_tracker) -> str | None:
    if gaze_tracker is None:
        return None
    return getattr(gaze_tracker, "mp", None)


def _get_tracker_margin(gaze_tracker) -> int | None:
    if gaze_tracker is None:
        return None
    return getattr(gaze_tracker, "margin", None)


def _build_dummy_inputs(
    model: torch.nn.Module,
    gaze_tracker,
) -> Tuple[
    Tuple[torch.Tensor, ...],
    List[str],
    List[str],
    Dict[str, List[int | str]],
    Dict[str, List[int | str]],
    Dict[str, str],
]:
    if gaze_tracker is not None and hasattr(gaze_tracker, "get_onnx_dummy_inputs"):
        result = gaze_tracker.get_onnx_dummy_inputs()
        if not isinstance(result, dict):
            raise HTTPException(
                status_code=500,
                detail="gaze_tracker.get_onnx_dummy_inputs() must return a dict",
            )

        required_keys = {
            "inputs",
            "input_names",
            "output_names",
            "input_shapes",
            "output_shapes",
            "preprocessing",
        }
        missing = required_keys.difference(result.keys())
        if missing:
            raise HTTPException(
                status_code=500,
                detail=f"Missing keys in get_onnx_dummy_inputs(): {sorted(missing)}",
            )

        return (
            tuple(result["inputs"]),
            list(result["input_names"]),
            list(result["output_names"]),
            dict(result["input_shapes"]),
            dict(result["output_shapes"]),
            dict(result["preprocessing"]),
        )

    device = next(model.parameters()).device if any(True for _ in model.parameters()) else torch.device("cpu")

    face = torch.randn(1, 3, 224, 224, device=device, dtype=torch.float32)
    left_eye = torch.randn(1, 3, 224, 224, device=device, dtype=torch.float32)
    right_eye = torch.randn(1, 3, 224, 224, device=device, dtype=torch.float32)
    face_grid = torch.randn(1, 625, device=device, dtype=torch.float32)

    input_names = ["face", "left_eye", "right_eye", "face_grid"]
    output_names = ["gaze"]

    input_shapes = {
        "face": [1, 3, 224, 224],
        "left_eye": [1, 3, 224, 224],
        "right_eye": [1, 3, 224, 224],
        "face_grid": [1, 625],
    }

    output_shapes = {
        "gaze": [1, 2],
    }

    preprocessing = {
        "face": "float32 normalized BGR face tensor in CHW order",
        "left_eye": "float32 normalized BGR left eye tensor in CHW order",
        "right_eye": "float32 normalized BGR right eye tensor in CHW order",
        "face_grid": "float32 flattened face grid tensor",
    }

    return (
        (face, left_eye, right_eye, face_grid),
        input_names,
        output_names,
        input_shapes,
        output_shapes,
        preprocessing,
    )


def _export_model_to_onnx(
    model: torch.nn.Module,
    export_path: Path,
    gaze_tracker,
    *,
    opset: int = DEFAULT_ONNX_OPSET,
) -> Dict[str, Any]:
    export_model = replace_crossmaplrn_for_onnx(model)
    export_model.eval()

    dummy_inputs, input_names, output_names, input_shapes, output_shapes, preprocessing = _build_dummy_inputs(
        export_model,
        gaze_tracker,
    )

    dynamic_axes = {
        input_name: {0: "batch_size"} for input_name in input_names
    }
    dynamic_axes.update({
        output_name: {0: "batch_size"} for output_name in output_names
    })

    export_path.parent.mkdir(parents=True, exist_ok=True)

    with torch.no_grad():
        try:
            torch.onnx.export(
                export_model,
                dummy_inputs,
                str(export_path),
                export_params=True,
                opset_version=opset,
                do_constant_folding=False,
                input_names=input_names,
                output_names=output_names,
                dynamic_axes=dynamic_axes,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"ONNX export failed: {exc}",
            ) from exc

    return {
        "input_names": input_names,
        "output_names": output_names,
        "input_shapes": input_shapes,
        "output_shapes": output_shapes,
        "dtype": "float32",
        "opset": opset,
        "preprocessing": preprocessing,
    }


def _save_metadata(client_id: str, version_dir: Path, metadata: Dict[str, Any]) -> Path:
    metadata_path = version_dir / "metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return metadata_path


def _refresh_latest_pointer(client_id: str, version_dir: Path) -> None:
    latest = _latest_dir(client_id)

    onnx_src = version_dir / "model.onnx"
    metadata_src = version_dir / "metadata.json"

    onnx_dst = latest / "model.onnx"
    metadata_dst = latest / "metadata.json"

    onnx_dst.write_bytes(onnx_src.read_bytes())
    metadata_dst.write_text(metadata_src.read_text(encoding="utf-8"), encoding="utf-8")


def _load_latest_metadata(client_id: str) -> Dict[str, Any]:
    metadata_path = _latest_dir(client_id) / "metadata.json"
    if not metadata_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No ONNX metadata found for client_id={client_id}",
        )

    try:
        return json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid latest metadata for client_id={client_id}: {exc}",
        ) from exc


def _latest_onnx_path(client_id: str) -> Path:
    path = _latest_dir(client_id) / "model.onnx"
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No ONNX model found for client_id={client_id}",
        )
    return path


def _tensor_to_chw_list(tensor: torch.Tensor) -> tuple[list[int], list[float]]:
    t = tensor.detach().cpu()

    if t.ndim == 4 and t.shape[0] == 1:
        t = t.squeeze(0)

    if t.ndim == 3 and t.shape[-1] == 3:
        t = t.permute(2, 0, 1).contiguous()

    return list(t.shape), t.flatten().tolist()


@router.post("/export/{client_id}", response_model=OnnxExportResponse)
def export_onnx_model(
    client_id: str,
    opset: int = Query(DEFAULT_ONNX_OPSET, ge=11, le=20),
    gaze_tracker=Depends(get_tracker),
) -> OnnxExportResponse:
    client_id = _safe_client_id(client_id)
    lock = _client_lock(client_id)

    if not lock.acquire(blocking=False):
        raise HTTPException(
            status_code=409,
            detail=f"An ONNX export is already running for client_id={client_id}",
        )

    try:
        _update_registry_status(
            client_id,
            training_status="finished",
            export_status="exporting",
        )

        model = _get_shared_model(gaze_tracker)
        model_type = _infer_model_type(model)

        version = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
        version_dir = _client_dir(client_id) / version
        version_dir.mkdir(parents=True, exist_ok=True)

        onnx_path = version_dir / "model.onnx"

        export_info = _export_model_to_onnx(
            model,
            onnx_path,
            gaze_tracker,
            opset=opset,
        )

        metadata = {
            "client_id": client_id,
            "model_type": model_type,
            "model_version": version,
            "created_at": _utc_now_iso(),
            "onnx_path": str(onnx_path.resolve()),
            "opset": export_info["opset"],
            "input_names": export_info["input_names"],
            "output_names": export_info["output_names"],
            "input_shapes": export_info["input_shapes"],
            "output_shapes": export_info["output_shapes"],
            "dtype": export_info["dtype"],
            "preprocessing": export_info["preprocessing"],
            "training_status": "finished",
            "export_status": "ready",
            "model_name": _get_tracker_model_name(gaze_tracker),
            "margin": _get_tracker_margin(gaze_tracker),
        }

        _save_metadata(client_id, version_dir, metadata)
        _refresh_latest_pointer(client_id, version_dir)

        registry = _read_registry(client_id)
        registry["training_status"] = "finished"
        registry["export_status"] = "ready"
        registry["updated_at"] = _utc_now_iso()
        registry["latest"] = {
            "model_version": version,
            "onnx_path": str((_latest_dir(client_id) / "model.onnx").resolve()),
            "metadata_path": str((_latest_dir(client_id) / "metadata.json").resolve()),
        }
        registry.setdefault("history", []).append(
            {
                "model_version": version,
                "created_at": metadata["created_at"],
                "onnx_path": str(onnx_path.resolve()),
                "metadata_path": str((version_dir / "metadata.json").resolve()),
            }
        )
        _write_registry(client_id, registry)

        return OnnxExportResponse(
            client_id=client_id,
            status="exported",
            model_version=version,
            onnx_filename="model.onnx",
            onnx_path=str((_latest_dir(client_id) / "model.onnx").resolve()),
        )

    except HTTPException:
        _update_registry_status(client_id, export_status="failed")
        raise
    except Exception as exc:
        _update_registry_status(client_id, export_status="failed")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected ONNX export error: {exc}",
        ) from exc
    finally:
        lock.release()


@router.get("/status/{client_id}", response_model=OnnxStatusResponse)
def get_onnx_status(client_id: str) -> OnnxStatusResponse:
    client_id = _safe_client_id(client_id)
    registry = _read_registry(client_id)

    has_onnx = (_latest_dir(client_id) / "model.onnx").exists()

    latest = registry.get("latest") or {}
    return OnnxStatusResponse(
        client_id=client_id,
        training_status=registry.get("training_status", "unknown"),
        export_status=registry.get("export_status", "unknown"),
        has_onnx=has_onnx,
        model_version=latest.get("model_version"),
        updated_at=registry.get("updated_at"),
    )


@router.get("/metadata/{client_id}", response_model=OnnxMetadataResponse)
def get_onnx_metadata(client_id: str) -> OnnxMetadataResponse:
    client_id = _safe_client_id(client_id)
    metadata = _load_latest_metadata(client_id)
    return OnnxMetadataResponse(**metadata)


@router.get("/means/{client_id}")
def get_onnx_means(
    client_id: str,
    gaze_tracker=Depends(get_tracker),
) -> Dict[str, Any]:
    client_id = _safe_client_id(client_id)

    if gaze_tracker is None:
        raise HTTPException(status_code=500, detail="Shared gaze_tracker is not available")

    if not hasattr(gaze_tracker, "faceMean") or not hasattr(gaze_tracker, "eyeLeftMean") or not hasattr(gaze_tracker, "eyeRightMean"):
        raise HTTPException(status_code=500, detail="Mean tensors are not available in gaze_tracker")

    face_shape, face_data = _tensor_to_chw_list(gaze_tracker.faceMean)
    left_shape, left_data = _tensor_to_chw_list(gaze_tracker.eyeLeftMean)
    right_shape, right_data = _tensor_to_chw_list(gaze_tracker.eyeRightMean)

    return {
        "client_id": client_id,
        "model_name": getattr(gaze_tracker, "mp", None),
        "face": {
            "shape": face_shape,
            "data": face_data,
        },
        "eye_left": {
            "shape": left_shape,
            "data": left_data,
        },
        "eye_right": {
            "shape": right_shape,
            "data": right_data,
        },
    }


@router.get("/latest/{client_id}")
def download_latest_onnx_model(client_id: str) -> FileResponse:
    client_id = _safe_client_id(client_id)
    onnx_path = _latest_onnx_path(client_id)

    return FileResponse(
        path=onnx_path,
        media_type="application/octet-stream",
        filename=f"{client_id}_model.onnx",
    )


@router.delete("/{client_id}")
def delete_client_onnx_artifacts(client_id: str) -> Dict[str, str]:
    client_id = _safe_client_id(client_id)
    client_dir = _client_dir(client_id)

    if not client_dir.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No ONNX artifacts found for client_id={client_id}",
        )

    for path in sorted(client_dir.rglob("*"), reverse=True):
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            path.rmdir()

    if client_dir.exists():
        client_dir.rmdir()

    return {
        "client_id": client_id,
        "status": "deleted",
    }