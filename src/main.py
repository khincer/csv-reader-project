"""Main script for reconciling MemberPress and Genius Referrals exports."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from csv_reader import CSVReader

DEFAULT_OUTPUT_FILENAME = "missing-memberpress-users.csv"


def main(argv: Sequence[str] | None = None) -> None:
    """Main entry point for exporting users missing from Genius Referrals."""

    project_root = Path(__file__).parent.parent
    args = _parse_args(project_root, argv)

    reader = CSVReader()

    memberpress_file = Path(args.memberpress)
    genius_referrals_file = Path(args.genius)
    output_path = Path(args.output)

    _ensure_file_exists(memberpress_file)
    _ensure_file_exists(genius_referrals_file)

    missing_members = reader.find_missing_members(memberpress_file, genius_referrals_file)

    if missing_members.empty:
        print("All MemberPress users already exist in Genius Referrals. No export created.")
        return

    output_path.parent.mkdir(exist_ok=True, parents=True)
    missing_members.to_csv(output_path, index=False)

    print(f"Found {len(missing_members)} MemberPress users missing from Genius Referrals.")
    print("Users that will be added:")
    for _, row in missing_members.iterrows():
        first = _safe_strip(row["First Name"])
        last = _safe_strip(row["Last name "])
        email = _safe_strip(row["Email"])
        print(f" - {first} {last} <{email}>")

    print(f"Missing users export saved to {output_path}")


def _parse_args(project_root: Path, argv: Sequence[str] | None) -> argparse.Namespace:
    """Build and run the CLI parser."""

    data_dir = project_root / "data"
    output_dir = project_root / "output"

    parser = argparse.ArgumentParser(
        description="Compare MemberPress and Genius Referrals exports and build an import file."
    )
    parser.add_argument(
        "--memberpress",
        default=data_dir / "memberpress.csv",
        help="Path to the MemberPress CSV export (default: data/memberpress.csv)",
    )
    parser.add_argument(
        "--genius",
        default=data_dir / "genius-referrals.csv",
        help="Path to the Genius Referrals CSV export (default: data/genius-referrals.csv)",
    )
    parser.add_argument(
        "--output",
        default=output_dir / DEFAULT_OUTPUT_FILENAME,
        help="Where to write the missing-member CSV (default: output/missing-memberpress-users.csv)",
    )

    return parser.parse_args(argv)


def _ensure_file_exists(file_path: Path) -> None:
    """Validate that a required CSV is available before processing."""

    if not file_path.exists():
        raise FileNotFoundError(f"Required file not found: {file_path}")


def _safe_strip(value: object) -> str:
    """Convert a possibly missing value to a trimmed string."""

    if value is None or value != value:  # NaN check via self inequality
        return ""
    return str(value).strip()


if __name__ == "__main__":
    main()
