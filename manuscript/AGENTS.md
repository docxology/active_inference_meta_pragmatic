# Manuscript guidance

Publishable source consists of numbered sections 01--11, 98 (symbols) and 99 (references). AGENTS.md, README.md, config.yaml and preamble.md are supporting metadata/guidance, not manuscript sections.

Use explicit labels, references, citation keys and figure paths. `utils.manuscript.validate_manuscript` rejects duplicates/unresolved labels/citations and missing figure files; the renderer produces native MathML HTML. Register newly generated figures and validate rendering after changes.

Every quantitative claim must trace to retained experiment evidence. Distinguish analytical identities, synthetic experiments, illustrative heuristics, untested proposals and literature context. Report seeds/units, train/test separation, controls, resource costs, uncertainty, multiplicity and limitations. Avoid unmeasured benchmarks, biological generalization, clinical guidance and security guarantees.

Bibliographic metadata must match the cited source. Keep author/publication declarations unknown when not supplied; do not invent affiliations, funding, ORCID, email or journal status. See `docs/scholarship_audit.md` for the source-review scope.
