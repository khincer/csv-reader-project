"""Main script for reconciling MemberPress and Genius Referrals exports."""
from __future__ import annotations

from pathlib import Path

from csv_reader import CSVReader

OUTPUT_FILENAME = "missing-memberpress-users.csv"


def main() -> None:
    """Main entry point for exporting users missing from Genius Referrals."""

    reader = CSVReader()
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    output_dir = project_root / "output"

    memberpress_file = data_dir / "memberpress.csv"
    genius_referrals_file = data_dir / "genius-referrals.csv"
    _ensure_file_exists(memberpress_file)
    _ensure_file_exists(genius_referrals_file)

    missing_members = reader.find_missing_members(memberpress_file, genius_referrals_file)

    if missing_members.empty:
        print("All MemberPress users already exist in Genius Referrals. No export created.")
        return

    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / OUTPUT_FILENAME
    missing_members.to_csv(output_path, index=False)

    print(f"Found {len(missing_members)} MemberPress users missing from Genius Referrals.")
    print("Users that will be added:")
    for _, row in missing_members.iterrows():
        first = _safe_strip(row["First Name"])
        last = _safe_strip(row["Last name "])
        email = _safe_strip(row["Email"])
        print(f" - {first} {last} <{email}>")

    print(f"Missing users export saved to {output_path}")


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
