import matplotlib.pyplot as plt
from matplotlib.text import Text
from xml.etree import ElementTree

from visualization.graphical_abstract import create_graphical_abstract
from visualization.publication_style import MINIMUM_FONT, save_publication_figure


def test_export_enforces_font_floor_and_preserves_larger_type(tmp_path):
    fig, axis = plt.subplots()
    small = axis.text(0.2, 0.3, "Readable probability", fontsize=4)
    large = axis.text(0.2, 0.6, "Important title", fontsize=20)
    save_publication_figure(fig, tmp_path / "figure.svg")
    assert small.get_fontsize() == MINIMUM_FONT
    assert large.get_fontsize() == 20
    assert all(t.get_fontsize() >= MINIMUM_FONT for t in fig.findobj(match=Text))
    svg = (tmp_path / "figure.svg").read_text()
    assert not any(line.rstrip() != line for line in svg.splitlines())
    save_publication_figure(fig, tmp_path / "figure.pdf")
    assert (tmp_path / "figure.pdf").read_bytes().startswith(b"%PDF")
    plt.close(fig)


def test_cover_reports_exact_policy_and_percentage_accuracy(tmp_path):
    study = {
        "estimates": [
            {
                "strategy": "EFE_sampled",
                "metric": "mean_inspections",
                "exact_expectation": 0.17,
                "mean": 0.99,
            }
        ]
    }
    experiment = {
        "summary": {
            name: {
                "accuracy": {
                    "mean": value,
                    "lower_bound": value - 0.02,
                    "upper_bound": value + 0.02,
                }
            }
            for name, value in (
                ("Q1_fixed", 0.666),
                ("Q2_metadata", 0.777),
                ("Q2_misleading", 0.444),
            )
        }
    }
    create_graphical_abstract(study, experiment, tmp_path)
    svg = ElementTree.parse(tmp_path / "scientific_graphical_abstract.svg")
    labels = {node.text for node in svg.iter("{http://www.w3.org/2000/svg}text")}
    assert {"17.0", "83.0", "66.6", "77.7", "44.4"} <= labels
    assert "99.0" not in labels
    assert "Held-out accuracy (%)" in labels
    assert "Policy probability (%)" in labels
    assert {
        "Q1  Infer and act",
        "Q2  Contextualize evidence",
        "Q3  Monitor inquiry",
        "Q4  Evaluate and revise",
        "Update beliefs from observations;",
        "Condition on source reliability;",
        "Assess uncertainty and cost;",
        "Challenge model assumptions;",
    } <= labels
