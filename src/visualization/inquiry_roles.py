"""Shared names and operational descriptions for the four conceptual inquiry roles."""

from typing import NamedTuple


class InquiryRole(NamedTuple):
    """A figure label and explanation, distinct from an implemented cognitive module."""

    code: str
    title: str
    operation: str
    fill: str
    ink: str


INQUIRY_ROLES = (
    InquiryRole(
        "Q1",
        "Infer and act",
        "Update beliefs from observations;\nevaluate actions under a model.",
        "#E5EDF4",
        "#245D87",
    ),
    InquiryRole(
        "Q2",
        "Contextualize evidence",
        "Condition on source reliability;\nexamine the context of evidence.",
        "#DFF0EE",
        "#236E66",
    ),
    InquiryRole(
        "Q3",
        "Monitor inquiry",
        "Assess uncertainty and cost;\nregulate further observation.",
        "#F5EADC",
        "#916133",
    ),
    InquiryRole(
        "Q4",
        "Evaluate and revise",
        "Challenge model assumptions;\njustify revisions before adoption.",
        "#ECE7F3",
        "#6B5289",
    ),
)
