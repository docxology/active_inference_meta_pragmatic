# Source guidance

Keep algorithms, statistical methods, experiments, plotting and manuscript validation in this directory; scripts provide CLI/I/O coordination. Use explicit type hints and informative docstrings for public APIs. Follow existing package imports and Black-compatible formatting.

`core/probability.py` owns categorical contracts. A and B are column stochastic; preserve exact zero support, reject malformed inputs, and document soft-evidence semantics. Share these contracts across model constructors and validators.

`analysis/experiments.py` owns the synthetic mechanisms. Keep training/test streams separate, evaluate paired seed units, retain raw evidence, and report sensing/training costs. Changes to the recorded design require updated results and manuscript descriptions.

Framework/modeler/control/security illustrations must not be described as empirically validated algorithms or calibrated risk estimates. Exact VFE and EFE are distinct from schematic illustrative scores. Maintain existing APIs where reasonable; document scientifically necessary behavior changes.

Add meaningful real-data/real-computation tests for changed contracts, using no mocks. Target at least 90% coverage for new modules and the repository gate; independently test mathematical identities rather than only checking return shapes.
