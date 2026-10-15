# Version 1.0.0: public release and archival history

## Identity and author authorization

The author explicitly authorized changing `docxology/active_inference_meta_pragmatic` to public and publishing version 1.0.0 on GitHub and Zenodo on 2026-10-15. This supersedes the earlier private-only distribution instruction for this project. The existing Zenodo draft, record 23397453, is reused; its reserved DOI is 10.5281/zenodo.23397453. Its pre-publication state was independently retrieved as unsubmitted, restricted and empty. No duplicate draft or automatic GitHub–Zenodo integration is introduced.

This is the first public release. Internal 1.1/1.2 labels were development markers. The [changelog](../CHANGELOG.md) preserves the three prior `main` commits and the reviewed checkpoint `58b2871`; the annotated tag selects the public release without rewriting history. The package, checkout compatibility metadata, manuscript and citation file use 1.0.0.

## Scientific and publication scope

The archive contains a preprint and reproducible synthetic research, not peer-reviewed findings or independent replication. Source-qualified scholarship, known limitations, funding/competing-interest omissions and the synthetic-intelligence disclosure remain explicit. Software and research files retain the repository's Apache-2.0 license. [Research integrity](research_integrity.md) preserves the authoring checks and [statistics](statistics.md) defines the inferential scope.

## Assets and binding

The release includes the actual pinned-template PDF, a web edition with its local assets, wheel and source distribution, a Git source ZIP, a Git bundle of the selected ancestry, a release manifest and SHA-256 checksums. The Git ZIP/bundle bind source to the tagged commit; the research manifest binds executed sources and outputs, and the renderer manifest binds the unchanged external template. Self-referential archive or commit hashes are not embedded in their own contents.

Credential checks cover the selected Git history and staged bytes against known local credential values and specific token/private-key patterns. A synthetic token control confirms the detector can fail. These bounded checks do not certify the absence of every possible secret. Credentials and task-specific operational logs remain outside tracked release files.

## Publication sequence and confirmation

Prepare and test the versioned sources, render and inspect the publication editions, then freeze a release commit. Build the source ZIP and Git bundle from that commit. Change GitHub visibility and fast-forward `main`, create the annotated tag and release, update/upload the existing Zenodo draft and publish it. Confirm repository visibility, tag/commit identity, public record metadata and anonymous downloads against the retained checksums. Preserve failed receipts and report any incomplete step. A later verification commit records observed publication state without moving the release tag.

At the tagged release-preparation cut, publication was pending. Publication subsequently completed at the [GitHub release](https://github.com/docxology/active_inference_meta_pragmatic/releases/tag/v1.0.0) and [Zenodo record](https://zenodo.org/records/23397453), DOI [10.5281/zenodo.23397453](https://doi.org/10.5281/zenodo.23397453). The annotated `v1.0.0` tag selects commit `eadfa2f030ea068df7ebdddc341829f20b85c713`; the publication-verification commit follows on `main` without moving that tag. The archive is open access and versioned 1.0.0.

The [publication receipt](release_v1.0.0_receipt.json) records the public metadata, tag identity, DOI resolver result and SHA-256/byte counts of all nine assets downloaded anonymously from each service. It includes the PDF, web ZIP, source ZIP, Git history bundle, wheel, source distribution, release notes, release manifest and checksum inventory. The [identity receipt](publication_identity.json) preserves the original restricted, empty draft reservation separately from the published state.

Both GitHub Actions runs for the release commit passed all four jobs: numerical/package validation on Python 3.11, 3.12 and 3.13, and actual template rendering. Run [38770684472](https://github.com/docxology/active_inference_meta_pragmatic/actions/runs/38770684472) and run [38770685013](https://github.com/docxology/active_inference_meta_pragmatic/actions/runs/38770685013) are remote execution evidence in addition to the local 629-test matrix. These checks verify the software and build workflows, not scientific replication or peer review.
