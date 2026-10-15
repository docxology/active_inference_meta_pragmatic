# Executable GNN model contract

GNN means Generalized Notation Notation, not a graph neural network. This project imports the actual upstream `gnn.parsers.markdown_parser.MarkdownGNNParser` from the checkout declared by `GNN_ROOT`. The local adapter is in `src/core/gnn.py`; the executable specifications and pin are in `src/core/gnn_models/`. No upstream parser code is copied or approximated.

The checkout must match origin, pinned revision, and unchanged tracked `src/gnn` source. Missing or mismatched dependencies fail explicitly. Set `GNN_ROOT` for noncanonical placement. The parser's XML and YAML imports require `defusedxml` and `pyyaml`, declared in the package. Upstream GNN 4.1 requires Python 3.11 or newer; this revision therefore raises the package's supported minimum to 3.11.

The admitted profile has one categorical factor, one observation modality, and finite A/B/C/D tensors. Sections must appear once in canonical order. Extension flags, extra variables, alternative dependency graphs, contradictory dimensions and invalid probability contracts are rejected. The profile is deliberately narrower than the upstream ecosystem; no multi-agent, continuous, hierarchical or native-backend support is implied.

```python
from core.gnn import load_gnn_model, sensor_model

declared = load_gnn_model()
posterior = declared.model.perform_inference(0)
assert abs(posterior[0] - 0.8) < 1e-12
revised = sensor_model(0.55)
assert abs(revised.model.perform_inference(0)[0] - 0.55) < 1e-12
```

`specified_model(A, B, C, D)` materializes each parameter realization as GNN Markdown and imports it through the same parser. It returns the model, source, content digest and upstream revision. The main experiment, exact identity checks, sensitivity sweep, and demonstration factory use this route. Direct `GenerativeModel` construction remains a low-level API and independent numerical oracle.

`core.gnn_serialization.serialize_categorical` owns numerical materialization. Replacements are scoped to named sections; nonparameter assignments in equations, annotations and ontology text are preserved. Missing or duplicated target sections fail. The public `specified_model` API still imports every resulting source through upstream, rather than executing the serializer's in-memory inputs directly. [World sampling](world_simulation.md) and [exact mismatch evaluation](model_robustness.md) are separate consumers of these imported models.

The experiment exports materialized sensor sources to `results/gnn/` and retains their source text/digests in `results/summary.json`. The pinned checkout is a separate scientific dependency; the installed wheel includes the authored specifications and lock but does not bundle the upstream project. Reproduction requires both. The upstream repository's licensing remains its own; the local package license does not relicense it.

Tests include malformed specifications, asymmetric transitions, impossible evidence, exact zero support, preference-driven policy changes, uninformative metadata, and actual fixed/adaptive sensing costs. These establish the bounded adapter/runtime contract, not the scientific adequacy of arbitrary models.
