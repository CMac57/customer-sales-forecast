"""Load the raw CSVs and build the daily series used across notebooks."""

from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def load_merged(raw_dir=RAW_DIR):
    """Inner-join customers to transactions on Customer_ID."""
    customers = pd.read_csv(Path(raw_dir) / "customer_master.csv")
    transactions = pd.read_csv(Path(raw_dir) / "customer_transactions.csv",
                               parse_dates=["Transaction_Date"])
    return pd.merge(customers, transactions, how="inner", on="Customer_ID")


def daily_series(df, column):
    """Sum `column` per day, with 0 for calendar days that have no transactions."""
    dates = df["Transaction_Date"]
    all_dates = pd.date_range(dates.min(), dates.max(), freq="D")
    return (df.groupby("Transaction_Date")[column].sum()
              .reindex(all_dates, fill_value=0)
              .rename_axis("Transaction_Date")
              .reset_index())
