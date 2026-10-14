"""Minimal figure management utilities for the Active Inference Meta-Pragmatic Framework.

This module provides basic figure registration functionality.
"""

import json
import os
import tempfile
import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from .logging import get_logger
from .exceptions import ValidationError

logger = get_logger(__name__)


@dataclass
class FigureMetadata:
    """Metadata for a registered figure."""

    filename: str
    caption: str
    label: Optional[str] = None
    section: Optional[str] = None
    generated_by: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    alt_text: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class FigureManager:
    """Minimal figure manager for registering figures."""

    def __init__(self, registry_file: Optional[str] = None):
        """Initialize figure manager.

        Args:
            registry_file: Path to figure registry file
        """
        if registry_file is None:
            # Resolve relative to project root, not cwd
            # Pipeline sets PROJECT_DIR; standalone uses file ancestry
            project_dir = os.environ.get("PROJECT_DIR")
            if project_dir:
                registry_file = str(
                    Path(project_dir) / "output" / "figures" / "figure_registry.json"
                )
            else:
                # src/utils/figure_manager.py → project root
                registry_file = str(
                    Path(__file__).resolve().parent.parent.parent
                    / "output"
                    / "figures"
                    / "figure_registry.json"
                )

        self.registry_file = Path(registry_file)
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        self.figures: Dict[str, FigureMetadata] = {}
        self._load_registry()
        logger.info(f"Initialized FigureManager (registry: {self.registry_file})")

    def register_figure(
        self,
        filename: str,
        caption: str,
        label: Optional[str] = None,
        section: Optional[str] = None,
        generated_by: Optional[str] = None,
        alt_text: Optional[str] = None,
        **kwargs,
    ) -> FigureMetadata:
        """Register a figure.

        Args:
            filename: Figure filename
            caption: Figure caption
            label: Figure label (auto-generated if None)
            section: Section where figure appears
            generated_by: Script that generated the figure
            alt_text: Accessible description, when supplied
            **kwargs: Additional parameters

        Returns:
            FigureMetadata object
        """
        if alt_text is not None and (
            not isinstance(alt_text, str) or not alt_text.strip()
        ):
            raise ValidationError("Figure alt text must be a nonempty string")
        # Generate label if not provided
        if label is None:
            base_name = Path(filename).stem
            label = f"fig:{base_name}"

        # Create metadata
        metadata = FigureMetadata(
            filename=filename,
            caption=caption,
            label=label,
            section=section,
            generated_by=generated_by,
            parameters=kwargs if kwargs else None,
            alt_text=alt_text,
        )

        # Register
        self.figures[label] = metadata
        self._save_registry()
        logger.info(f"Registered figure: {label} ({filename})")

        return metadata

    def _load_registry(self) -> None:
        """Load figure registry from file."""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, "r") as f:
                    data = json.load(f)
                    for label, fig_data in data.items():
                        self.figures[label] = FigureMetadata(**fig_data)
            except (ValueError, TypeError, KeyError, AttributeError):
                # Preserve unreadable content before a later registration replaces it.
                original = self.registry_file.read_bytes()
                digest = hashlib.sha256(original).hexdigest()[:12]
                archive = self.registry_file.with_name(
                    self.registry_file.name + f".corrupt-{digest}"
                )
                if not archive.exists():
                    archive.write_bytes(original)
                logger.warning("Preserved invalid figure registry at %s", archive)
                self.figures = {}

    def _save_registry(self) -> None:
        """Save figure registry to file."""
        data = {label: fig.to_dict() for label, fig in self.figures.items()}
        descriptor, temporary = tempfile.mkstemp(
            prefix=".figure-registry-", dir=self.registry_file.parent
        )
        try:
            with os.fdopen(descriptor, "w") as handle:
                json.dump(data, handle, indent=2, default=str)
                handle.write("\n")
            os.replace(temporary, self.registry_file)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
