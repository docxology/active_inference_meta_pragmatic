# Style and claims

Use clear names, type hints, informative docstrings and Black-compatible formatting. Reusable calculations, plotting and validation belong in `src/`; scripts parse arguments and coordinate calls. Use local NumPy generators instead of resetting global random state.

Document A/B column orientation, evidence semantics, C normalization and mean/sum horizon aggregation whenever they matter. Preserve exact support rather than clipping impossible states into feasibility. Call illustrative model-free energy/security/control scores heuristics.

Scientific prose states the design and evidence first. Distinguish conceptual proposals, exact identities, software tests, synthetic experiments and literature context. Report costs, training information, independent units, uncertainty and multiplicity. Do not imply participant data, peer review, DOI assignment, preregistration or operational security efficacy.

Keep a single topic owner in `docs/`; link to related guides. Link bibliography metadata to primary records and identify preprints. Do not invent author identifiers, affiliations, funding or publication declarations.
