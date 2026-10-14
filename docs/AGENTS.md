# Documentation guidance

Keep `docs/README.md` as the topic index and include every guide there. Each page owns one topic; link to the methods/statistics/rendering guides instead of repeating their full contracts. Update documented commands and paths together with code changes.

Describe implemented behavior and retained evidence. Label proposals, heuristic examples, synthetic results, numerical identities, software coverage and publication status separately. Never invent results, metadata, reviewer approval or security assurances.

Run `python scripts/09_validate_documentation.py` after editing links. Run the research and rendering workflows after changing numerical/manuscript sources, then rebuild both manifests. Preserve private content and follow parent GitVault write guards.
