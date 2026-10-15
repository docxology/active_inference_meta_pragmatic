"""Materialize categorical tensors within named GNN sections."""

import json
import re

import numpy as np
from numpy.typing import ArrayLike

from .probability import model_matrices
from utils.exceptions import ValidationError


def _section(content: str, name: str, body: str) -> str:
    pattern = rf"(^## {name}\n).*?(?=^## |\Z)"
    content, count = re.subn(
        pattern, lambda m: m[1] + body + "\n\n", content, flags=re.M | re.S
    )
    if count != 1:
        raise ValidationError(f"GNN template requires exactly one {name} section")
    return content


def serialize_categorical(
    template: str, A: ArrayLike, B: ArrayLike, C: ArrayLike, D: ArrayLike, name: str
) -> str:
    """Change numerical sections without rewriting ontology or annotation text."""
    arrays = model_matrices(A, B, C, D)
    if not name.strip() or "\n" in name or "\r" in name:
        raise ValidationError("Model name must be one nonempty line")
    content = _section(template, "ModelName", name)
    declarations = [
        key + "[" + ",".join(map(str, array.shape)) + ",type=float]"
        for key, array in zip(("A", "B", "C", "D"), arrays)
    ]
    declarations.extend(
        (f"s[{arrays[3].size},type=float]", "o[1,type=int]", "u[1,type=int]")
    )
    content = _section(content, "StateSpaceBlock", "\n".join(declarations))
    values = [
        key + "=" + json.dumps(array.tolist(), allow_nan=False)
        for key, array in zip(("A", "B", "C", "D"), arrays)
    ]
    content = _section(content, "InitialParameterization", "\n".join(values))
    content = _section(
        content,
        "ModelParameters",
        f"num_hidden_states: {arrays[3].size}\nnum_obs: {arrays[0].shape[0]}\nnum_actions: {arrays[1].shape[2]}",
    )
    static = all(
        np.array_equal(arrays[1][:, :, action], np.eye(arrays[3].size))
        for action in range(arrays[1].shape[2])
    )
    content = _section(content, "Time", "Static" if static else "Dynamic")
    return content.replace(
        "Single hidden state factor, one binary observation modality, fixed state within a trial.",
        "Single categorical hidden state factor and observation modality; tensors define the dynamics.",
        1,
    )
