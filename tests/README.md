# Tests

Run `MPLBACKEND=Agg uv run pytest --cov=src --cov-report=term-missing` after installing dev/research extras. Tests use real computations and temporary files, with no mocks. The coverage gate is 90%.

The original broad API suite is supplemented by analytical probability/free-energy checks and research-workflow tests. These verify soft evidence, exact support, asymmetric transition conventions, paired statistics, raw trial/replicate scoring, training/test design, manuscript references/rendering, and output digests. Coverage does not establish biological or physical validity.
