# Main argument and technical supplements

The manuscript has two reading paths. Sections 1–10 develop the argument, show the two experimental tasks and retain the principal evidence and limitations. Section 11 is the technical supplement; section 12 consolidates notation and conceptual terms. Section 13 is the common bibliography. Numbered source filenames remain stable so the actual pinned template can render one combined PDF and HTML with cross-references intact.

Section 10 covers research integrity and includes subsections for author identity and publication status, synthetic intelligence assistance and human accountability, and synthetic data and declarations. The [research integrity guide](research_integrity.md) records these current additions..

## The abstract and early orientation

`01_abstract.md` contains exactly two prose paragraphs, followed by keywords and the quadrant orientation figure. The abstract states the conceptual proposal, implemented categorical methods, qualitative findings and limits without enumerating performance percentages. Its second paragraph displays the full public GitHub repository URL as a hyperlink. The first numbered visualization establishes Q1 inference, Q2 source context, Q3 monitoring and Q4 revision, with both axes and a distinct failure mode in every cell. Later sections refer back to this shared map.

## The models made visible

The main model diagram shows the sensor-study evidence flow and the four-state context/observation-mode action task. Its sensor labels come from actual imported GNN models and its nonself transition arrows come from the imported transition tensor. Shared initial observations, optional additional sensing and separate training are visually distinguished. World generation, agent computation and external scoring remain separate.

The supplementary matrix atlas imports all three packaged GNN specifications and displays every A/B/C/D value. The stay/switch model is a numerical control example, not a third experimental study. Probability scales and signed preference logits are distinguished. A repeated transition panel for the single-action binary model is explicitly labeled. The existing model–world mismatch figure explains why these declarations still need external evaluation.

## Technical supplement contents

| Material | Destination in `11_appendix.md` |
|---|---|
| Actual GNN tensor atlas | Models behind the diagrams |
| Probability contracts, Bayes, VFE/EFE and exact sensitivity | Probability contracts and exact inference |
| Full sensor/action/mismatch design and statistical procedures | Complete experimental and statistical protocol |
| Paired comparisons, threshold sweep and policy landscape | Paired contrasts, stopping rules and policy surfaces |
| Revision workflow, heuristic weighted objective and security API qualifications | Revision mechanics and diagnostic boundaries |
| Derivations, result tables, complexity and reproduction commands | Derivations, retained results and reproduction |

Every equation and figure has a stable reference label. The main paper links to the details rather than omitting experimental units, resource differences, uncertainty assumptions or failure cases. The numerical study and statistical families are unchanged.

## Notation and maintenance

`98_symbols_glossary.md` is the supplemental notation authority for both reading paths. It covers model components, evidence, policy distributions, information measures, heuristic scores, world/agent risk, statistical quantities and computational counts. It distinguishes the reward function from reliability, preference logits from probabilities, policy sequences from one-step action probabilities and branch-aware coverage from theoretical correctness. Computational counts use distinct symbols rather than overloading likelihood A or entropy H.

Plot code is split among `visualization.conceptual_figures`, `visualization.task_model_figures` and `visualization.model_atlas`, with the pipeline owning orchestration. The figure registry records accessible descriptions and actual model-source digests. Regenerate with script 07; render with the pinned actual template through script 08. Run the manuscript and [documentation validators](syntax_guide.md), real integration tests, and inspect PDF pages and HTML after any relocation or new symbol. Hyperlinks retain the red publication style. The PDF is not claimed to be tagged or fully accessible.
