"""Documentation contract for TASK-006; deployment actions need separate evidence."""

from pathlib import Path


def test_tc_025_readme_discloses_production_limits():
    """TC-025: production boundaries are explicit in the project documentation."""
    readme = (Path(__file__).resolve().parents[1] / "README.md").read_text()
    limits = " ".join(
        readme.split("## Production limitations (TC-025 / REQ-016)", 1)[1]
        .lower()
        .split()
    )
    for disclosure in (
        "not production ready",
        "synthetic",
        "in-memory sink",
        "lost on restart",
        "cross-worker consistency",
        "production identity",
        "real mail",
        "durable storage",
        "transactions",
        "transactional outbox",
        "retention",
        "key rotation",
        "abuse prevention",
        "delivery and failure monitoring",
    ):
        assert disclosure in limits, f"README omits {disclosure!r}"
