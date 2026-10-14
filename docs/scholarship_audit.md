# Scholarship audit — 2026-10-13

This review checked the identity and selected metadata of the records cited in the revised manuscript against publisher, author-repository, PubMed/PMC, JOSS or arXiv records. It is a targeted source review, not a systematic literature search or independent peer review. The machine-readable source list is `scholarship_sources.json`. Uncited legacy entries were removed from the active bibliography; their original content remains in Git history.

The original draft conflated several papers or supplied incorrect author names and identifiers. Corrections include:

| Original issue | Corrected source |
|---|---|
| A 2015 entry combined the title of a 2017 curiosity paper with different authors/pages | [Active inference and epistemic value (2015)](https://pubmed.ncbi.nlm.nih.gov/25689102/) |
| Scaling active inference linked arXiv:2006.12911, an unrelated atmospheric-turbulence paper | [Tschantz, Baltieri, Seth and Buckley, arXiv:1911.10601](https://arxiv.org/abs/1911.10601) |
| A purported Sajid 2022 agency paper linked arXiv:2201.09302, an unrelated camera paper | Removed from the revised bibliography; the comparative argument uses [Sajid et al., demystified and compared](https://arxiv.org/abs/1909.10863) |
| Planning paper assigned to Champion and colleagues | [de Vries and colleagues, arXiv:2504.14898](https://arxiv.org/abs/2504.14898) |
| MetaMind used an incorrect given name and a nonauthor organization | [Zhang, Chen, Yeh and Li, arXiv:2505.18943](https://arxiv.org/abs/2505.18943) |
| FEPS used unrelated author names | [Pazem, Krumm, Vining, Fiderer and Briegel](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0331047) |
| SOFAI was attributed to Cerutti alone | [Bergamaschi Ganapini and colleagues](https://www.nature.com/articles/s44387-025-00027-5) |
| Scale-free paper listed volume 3 | [Frontiers in Network Physiology, volume 5](https://www.frontiersin.org/journals/network-physiology/articles/10.3389/fnetp.2025.1521963/full) |
| Discrete synthesis and learning papers had incorrect/incomplete author lists | [Da Costa et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC7732703/) and [Friston et al.](https://discovery.ucl.ac.uk/id/eprint/1506130/) |

The discussion now distinguishes posterior concentration from calibration using [Fleming and Lau](https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2014.00443/full), and distinguishes EFE assumptions from ordinary VFE using [Millidge, Tschantz and Buckley](https://arxiv.org/abs/2004.08128). MetaMind and SOFAI are architectural context, not evidence for the present active-inference experiment. Preprints are identified as such; their reported performance is not reproduced or adopted as this project's result.

A bulk Crossref title query was also attempted. Most requests were rate-limited (HTTP 429); those unavailable responses were not treated as evidence that an entry was invalid. The corrections above rely on directly inspected primary records. Unknown author ORCID/email fields and publication declarations remain unspecified. A human author should check submission-specific metadata and final interpretation before journal submission.
