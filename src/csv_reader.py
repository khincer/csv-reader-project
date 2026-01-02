"""CSV Reader module for processing CSV files."""
from __future__ import annotations

import pandas as pd
from pathlib import Path


MISSING_MEMBER_OUTPUT_COLUMNS = [
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


class CSVReader:
    """Class for reading and processing CSV files."""
    
    def __init__(self, encoding: str = 'utf-8'):
        """
        Initialize the CSV reader.
        
        Args:
            encoding: Character encoding for reading files (default: utf-8)
        """
        self.encoding = encoding
    
    def read_csv(self, file_path: str | Path, **kwargs) -> pd.DataFrame:
        """
        Read a CSV file and return a pandas DataFrame.
        
        Args:
            file_path: Path to the CSV file
            **kwargs: Additional arguments to pass to pandas.read_csv()
        
        Returns:
            DataFrame containing the CSV data
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        df = pd.read_csv(file_path, encoding=self.encoding, **kwargs)
        return df
    
    def read_multiple_csvs(self, file_paths: list[str | Path]) -> dict[str, pd.DataFrame]:
        """
        Read multiple CSV files and return a dictionary of DataFrames.
        
        Args:
            file_paths: List of paths to CSV files
        
        Returns:
            Dictionary with filenames as keys and DataFrames as values
        """
        dataframes = {}
        
        for file_path in file_paths:
            file_path = Path(file_path)
            df = self.read_csv(file_path)
            dataframes[file_path.name] = df
        
        return dataframes
    
    def get_csv_info(self, df: pd.DataFrame) -> dict:
        """
        Get basic information about a CSV DataFrame.
        
        Args:
            df: pandas DataFrame
        
        Returns:
            Dictionary containing DataFrame statistics
        """
        return {
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict()
        }

    def find_missing_members(
        self,
        memberpress_path: str | Path,
        genius_referrals_path: str | Path,
    ) -> pd.DataFrame:
        """Build an export of MemberPress users missing from Genius Referrals.

        Args:
            memberpress_path: CSV containing MemberPress users (expects first_name, last_name, email).
            genius_referrals_path: CSV from Genius Referrals (expects ADVOCATE_EMAIL column).

        Returns:
            DataFrame ready to export using the example.csv column structure.

        Raises:
            ValueError: If the expected columns are not present in either file.
        """

        memberpress_df = self.read_csv(memberpress_path)
        genius_df = self.read_csv(genius_referrals_path)

        required_memberpress_columns = {"first_name", "last_name", "email"}
        missing_memberpress_columns = required_memberpress_columns - set(memberpress_df.columns)
        if missing_memberpress_columns:
            raise ValueError(
                "MemberPress CSV missing required columns: "
                + ", ".join(sorted(missing_memberpress_columns))
            )

        if "ADVOCATE_EMAIL" not in genius_df.columns:
            raise ValueError("Genius Referrals CSV missing required column: ADVOCATE_EMAIL")

        memberpress_emails = self._normalize_email_series(memberpress_df["email"])
        genius_emails = self._normalize_email_series(genius_df["ADVOCATE_EMAIL"])

        missing_mask = ~memberpress_emails.isin(genius_emails)
        missing_df = memberpress_df.loc[missing_mask, ["first_name", "last_name", "email"]].copy()

        missing_df.rename(
            columns={
                "first_name": "First Name",
                "last_name": "Last name ",
                "email": "Email",
            },
            inplace=True,
        )

        missing_df[" Payout threshold"] = 1
        missing_df[" Currency code"] = "USD"
        missing_df["Member type"] = "ADVOCATE"
        missing_df["Campaign slug  (optional)"] = ""
        missing_df["Referrer’s email (optional)"] = ""
        missing_df[" note (optional)"] = ""

        return missing_df[MISSING_MEMBER_OUTPUT_COLUMNS]

    @staticmethod
    def _normalize_email_series(series: pd.Series) -> pd.Series:
        """Normalize email addresses for reliable comparisons."""

        return series.fillna("").astype(str).str.strip().str.lower()
