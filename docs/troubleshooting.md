# Troubleshooting

**Installed imports fail:** run `uv sync --locked --extra dev --extra research`. Installed package imports are `core`, `framework`, `analysis`, `visualization` and `utils`; `src` reexports support checkout use. Confirm the active interpreter belongs to this project.

**Invalid model or evidence:** check dimensions and finite nonnegative probabilities. A/B columns must sum to one, C is a finite logit vector, D is normalized, and action indices are valid. Impossible evidence is an input/model conflict; do not hide it by clipping probabilities.

**Missing manuscript figures:** reproduce the default research pipeline first. Authored source paths refer to `results/figures/`; a custom output directory does not rewrite them.

**Template pin or cleanliness failure:** inspect `template.lock.json`, `git -C "$TEMPLATE_ROOT" rev-parse HEAD` and `git -C "$TEMPLATE_ROOT" status --short`. Preserve upstream work and use a clean checkout at the pinned commit. Do not silently relax the check.

**XeLaTeX, BibTeX or package errors:** ensure the TeX bin directory is on PATH and inspect `output/pdf/` logs. Install the reported package in the chosen TeX distribution, then rerun. Pandoc must also be available. Fix manuscript/preamble source rather than patching generated LaTeX.

**HTML equations do not typeset:** the template edition needs the pinned MathJax CDN. Use the PDF or offline `results/manuscript.html` preview when disconnected. Preserve sibling figure assets when copying HTML.

**Documentation link validation fails:** resolve the reported path and update the page's link or index entry. Documentation validation reads actual files; missing links are not silently ignored.

**Vault write guard refuses:** respect the migration marker, shared operation lock and active Git transfers. Coordinate the owning operation and retry after release; never delete the lock or kill a clone/fetch.
