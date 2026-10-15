"""Import the pinned upstream GNN parser and execute its categorical tensors.

The upstream checkout is an explicit scientific dependency, not vendored code.
The profile intentionally admits one categorical factor and modality. It rejects
warnings, duplicate sections, undeclared tensors and unsupported model families.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Final, Protocol

import numpy as np
from numpy.typing import ArrayLike

from .generative_models import GenerativeModel
from .gnn_serialization import serialize_categorical
from utils.exceptions import ValidationError

MODEL_DIRECTORY: Final = Path(__file__).parent / "gnn_models"
REQUIRED_SECTIONS: Final = (
    "GNNSection",
    "GNNVersionAndFlags",
    "ModelName",
    "ModelAnnotation",
    "StateSpaceBlock",
    "Connections",
    "InitialParameterization",
    "Equations",
    "Time",
    "ActInfOntologyAnnotation",
    "ModelParameters",
    "Footer",
    "Signature",
)


class ParsedVariable(Protocol):
    name: str
    dimensions: list[int]


class ParsedParameter(Protocol):
    name: str
    value: float | int | str | list


class ParsedModel(Protocol):
    variables: list[ParsedVariable]
    parameters: list[ParsedParameter]
    raw_sections: dict[str, str]


class ParsedResult(Protocol):
    success: bool
    errors: list[str]
    warnings: list[str]
    model: ParsedModel


class ReferenceParser(Protocol):
    def parse_string(self, content: str) -> ParsedResult: ...


@dataclass(frozen=True, slots=True)
class ImportedGNNModel:
    """The executed model and the exact specification that produced its tensors."""

    model: GenerativeModel
    specification: str
    specification_sha256: str
    upstream_revision: str


def _git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=True,
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
    ).stdout.strip()


def upstream_root() -> Path:
    """Resolve an explicit GNN_ROOT or the canonical sibling GitVault repository."""
    configured = os.environ.get("GNN_ROOT")
    if configured:
        return Path(configured).resolve()
    for parent in Path(__file__).resolve().parents:
        candidate = (
            parent
            / "Username/ActiveInferenceInstitute/Public/Generalized_Notation_Notation"
        )
        if candidate.is_dir():
            return candidate
    raise ValidationError(
        "Set GNN_ROOT to the pinned Generalized_Notation_Notation checkout"
    )


def verify_upstream(root: Path | None = None) -> str:
    """Require the pinned origin/revision and unchanged tracked parser source."""
    root = root or upstream_root()
    pin = json.loads((MODEL_DIRECTORY / "upstream.lock.json").read_text())
    try:
        revision = _git(root, "rev-parse", "HEAD")
        origin = _git(root, "remote", "get-url", "origin").removesuffix(".git")
        modified = _git(
            root, "status", "--porcelain", "--untracked-files=no", "--", "src/gnn"
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise ValidationError("GNN_ROOT must be a readable Git checkout") from exc
    origin = origin.replace("git@github.com:", "https://github.com/")
    if origin != pin["repository"] or revision != pin["revision"] or modified:
        raise ValidationError(
            "GNN checkout origin, revision or source differs from upstream.lock.json"
        )
    return revision


@lru_cache(maxsize=1)
def _reference_parser(root: Path) -> ReferenceParser:
    """Load the actual upstream parser once, preserving the caller's search path."""
    verify_upstream(root)
    original_path = sys.path.copy()
    try:
        sys.path.insert(0, str(root / "src"))
        from gnn.parsers.markdown_parser import MarkdownGNNParser

        module = sys.modules[MarkdownGNNParser.__module__]
        if (
            Path(module.__file__).resolve()
            != root / "src/gnn/parsers/markdown_parser.py"
        ):
            raise ValidationError("A different GNN parser is already imported")
        return MarkdownGNNParser()
    finally:
        sys.path[:] = original_path


def import_gnn(content: str) -> ImportedGNNModel:
    """Compile real GNN Markdown into the strict exact categorical runtime."""
    sections = re.findall(r"^## (\w+)\s*$", content, re.M)
    if sections != list(REQUIRED_SECTIONS):
        raise ValidationError(
            "GNN profile requires each canonical section once and in order"
        )
    parser = _reference_parser(upstream_root())
    parsed = parser.parse_string(content)
    if not parsed.success or parsed.errors or parsed.warnings:
        raise ValidationError(
            f"Upstream GNN parser rejected source: {parsed.errors + parsed.warnings}"
        )
    ir = parsed.model
    if ir.raw_sections["GNNSection"].strip() != "ActInfPOMDP":
        raise ValidationError("Only ActInfPOMDP models are supported")
    if ir.raw_sections["GNNVersionAndFlags"].strip() != "GNN v1":
        raise ValidationError("Only GNN v1 without extension flags is supported")
    if ir.raw_sections["Time"].strip() not in ("Static", "Dynamic"):
        raise ValidationError("Only categorical Static or Dynamic models are supported")
    parameters = {p.name: p.value for p in ir.parameters}
    allowed = {"A", "B", "C", "D", "num_hidden_states", "num_obs", "num_actions"}
    if len(parameters) != len(ir.parameters) or set(parameters) != allowed:
        raise ValidationError(
            "Exactly one A/B/C/D and each model dimension parameter is required"
        )
    dimensions = {v.name: tuple(v.dimensions) for v in ir.variables}
    if len(dimensions) != len(ir.variables):
        raise ValidationError("Duplicate state-space declarations")
    try:
        arrays = [
            np.asarray(parameters[key], dtype=float) for key in ("A", "B", "C", "D")
        ]
    except (ValueError, TypeError) as exc:
        raise ValidationError(
            "GNN parameters must be finite numerical tensors"
        ) from exc
    for key, array in zip(("A", "B", "C", "D"), arrays):
        if dimensions.get(key) != array.shape:
            raise ValidationError(
                f"GNN {key} declared dimensions differ from its values"
            )
    model = GenerativeModel(*arrays)
    if (
        parameters["num_hidden_states"],
        parameters["num_obs"],
        parameters["num_actions"],
    ) != (model.n_states, model.n_observations, model.n_actions):
        raise ValidationError("ModelParameters contradict the tensor dimensions")
    if set(dimensions) != {"A", "B", "C", "D", "s", "o", "u"}:
        raise ValidationError("Unsupported state-space variable in categorical profile")
    if (dimensions["s"], dimensions["o"], dimensions["u"]) != (
        (model.n_states,),
        (1,),
        (1,),
    ):
        raise ValidationError(
            "State, observation or action declaration is incompatible"
        )
    edges = [
        line.strip()
        for line in ir.raw_sections["Connections"].splitlines()
        if line.strip()
    ]
    if edges != ["D>s", "s>A", "A>o", "s>B", "u>B", "B>s"]:
        raise ValidationError("Unsupported dependency graph in categorical profile")
    revision = json.loads((MODEL_DIRECTORY / "upstream.lock.json").read_text())[
        "revision"
    ]
    return ImportedGNNModel(
        model, content, hashlib.sha256(content.encode()).hexdigest(), revision
    )


def load_gnn_model(path: Path | None = None) -> ImportedGNNModel:
    """Load a declared model; absence or malformed input never selects a fallback."""
    return import_gnn((path or MODEL_DIRECTORY / "binary_sensor.md").read_text())


def specified_model(
    A: ArrayLike,
    B: ArrayLike,
    C: ArrayLike,
    D: ArrayLike,
    name: str = "Materialized categorical model",
) -> ImportedGNNModel:
    """Materialize a parameter revision as GNN and re-import the actual source.

    Generated studies vary tensor values and dimensions; every realization is
    parsed by upstream and can be retained verbatim in an execution receipt.
    """
    return import_gnn(
        serialize_categorical(
            (MODEL_DIRECTORY / "binary_sensor.md").read_text(), A, B, C, D, name
        )
    )


def sensor_model(reliability: float) -> ImportedGNNModel:
    """A reliability intervention changes the declared likelihood tensor."""
    return specified_model(
        [[reliability, 1 - reliability], [1 - reliability, reliability]],
        np.eye(2),
        [0.0, 0.0],
        [0.5, 0.5],
        "Binary sensor reliability revision",
    )
