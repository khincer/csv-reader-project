"""Unit tests for the CSV reader module."""
import pytest
import pandas as pd
from pathlib import Path
import sys

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from csv_reader import CSVReader


def test_csv_reader_initialization():
    """Test CSVReader initialization."""
    reader = CSVReader()
    assert reader.encoding == 'utf-8'
    
    reader_custom = CSVReader(encoding='latin-1')
    assert reader_custom.encoding == 'latin-1'


def test_get_csv_info():
    """Test get_csv_info method."""
    reader = CSVReader()
    
    # Create a sample DataFrame
    df = pd.DataFrame({
        'name': ['Alice', 'Bob', None],
        'age': [25, 30, 35],
        'city': ['New York', 'London', 'Paris']
    })
    
    info = reader.get_csv_info(df)
    
    assert info['rows'] == 3
    assert info['columns'] == 3
    assert 'name' in info['column_names']
    assert info['missing_values']['name'] == 1
    assert info['missing_values']['age'] == 0


def test_find_missing_members(tmp_path):
    """Verify we can build the Genius Referrals import file from missing members."""

    reader = CSVReader()

    memberpress_df = pd.DataFrame(
        [
            {"first_name": "Alice", "last_name": "Smith", "email": "alice@example.com"},
            {"first_name": "Bob", "last_name": "Brown", "email": "bob@example.com"},
            {"first_name": "Carol", "last_name": "Jones", "email": "carol@example.com"},
        ]
    )
    memberpress_path = tmp_path / "memberpress.csv"
    memberpress_df.to_csv(memberpress_path, index=False)

    genius_df = pd.DataFrame(
        [
            {"MEMBER_EMAIL": "bob@example.com"},
            {"MEMBER_EMAIL": "CAROL@EXAMPLE.COM"},
        ]
    )
    genius_path = tmp_path / "genius-referrals.csv"
    genius_df.to_csv(genius_path, index=False)

    missing_df = reader.find_missing_members(memberpress_path, genius_path)

    assert list(missing_df.columns) == [
        "First Name",
        "Last name ",
        "Email",
        " Payout threshold",
        " Currency code",
        "Member type",
        "Campaign slug  (optional)",
        "Referrer’s email (optional)",
        " note (optional)",
    ]

    assert missing_df.shape[0] == 1
    row = missing_df.iloc[0]
    assert row["First Name"] == "Alice"
    assert row["Last name "] == "Smith"
    assert row["Email"] == "alice@example.com"
    assert row[" Payout threshold"] == 1
    assert row[" Currency code"] == "USD"
    assert row["Member type"] == "ADVOCATE"
    assert row["Campaign slug  (optional)"] == ""
    assert row["Referrer’s email (optional)"] == ""
    assert row[" note (optional)"] == ""
