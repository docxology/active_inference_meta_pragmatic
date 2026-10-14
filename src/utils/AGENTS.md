# Utility guidance

Keep filesystem operations local and explicit. Figure registries use atomic replacement and preserve corrupted bytes before a subsequent registration replaces the active file. Do not silently erase unreadable user content.

Markdown insertion must match the complete requested heading and avoid duplicate figure labels. Manuscript validation reads numbered sections, checks citation/reference uniqueness and figure existence, and excludes guidance documents. Rendering must fail on unsupported equations rather than silently dropping them.

Provenance records source/configuration/environment/output digests without embedding credentials or machine-specific source paths. Exclude the manifest itself from output hashing to avoid cycles. Git revision is the base revision; source hashes identify the actual executed files.

Tests use real temporary files and computations, without mocks.
