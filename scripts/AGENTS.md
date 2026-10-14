# Script guidance

Scripts are thin coordinators: import calculations and plotting from `src/`, parse CLI options, manage paths, and handle I/O. Avoid dependencies on unprovided parent infrastructure.

Scripts 01--05 produce educational illustrations in `output/figures/`. Their registrations and captions must identify schematic or synthetic demonstrations; do not present those diagrams as the retained experiment.

Script 06 validates explicit manuscript figure placement and optionally renders HTML. Script 07 reproduces the six-stage standalone workflow. Keep `--dry-run` free of output writes and make stage dependencies explicit. Fail with nonzero status on computation, validation or rendering errors.

Use paths derived from this repository or explicit user CLI paths. Register figures in the same output directory that receives them. Do not silently report success when figures or references are missing.
