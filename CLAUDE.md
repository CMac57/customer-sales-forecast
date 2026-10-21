# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Time-series sales forecasting for a customer base, in two notebooks: exploration (`01_eda`) and forecasting (`02_forecast`). No build, lint, or test tooling exists yet.

## Setup and running

Dependencies live in a `.venv` (git-ignored) built from Anaconda's Python (`C:\Users\di_ba\anaconda3\python.exe`; Python is not on PATH). It is registered as the Jupyter kernel `sales-forecast`, which notebooks should use.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\jupyter.exe notebook notebooks/01_eda.ipynb
```

Notebooks load data with paths relative to `notebooks/` (e.g. `../data/raw/customer_master.csv`), so launch the kernel with `notebooks/` as the working directory (the default when opening the notebook in Jupyter or VS Code).

## Data

Two CSVs in `data/raw/`; treat them as read-only source data:

- `customer_master.csv`: 200 customers. Columns are `Customer_ID`, `Region`, `Province`, `Segment`, and `Account_Manager` (all in Canada).
- `customer_transactions.csv`: 1,000 transactions from 2025-02-15 to 2026-02-14. Columns are `Transaction_ID`, `Customer_ID`, `Transaction_Date`, `Product_Category`, `Quantity`, `Unit_Price`, and `Total_Amount`.

They are inner-joined on `Customer_ID`. One customer has no transactions, so the merged frame has 199 unique customers.

## Analysis flow (`notebooks/01_eda.ipynb`)

1. Load and merge, run Data Quality checks (nulls, duplicates, totals, unmatched customers, missing dates), then EDA: boxplots, countplots of the categorical columns, and distributions.
2. Aggregate to two daily series by summing on `Transaction_Date`, reindexed to every calendar day (`all_dates`, defined in the Data Quality section) with 0 for the 30 days that have no sales:
   - `df_Quantity` (units)
   - `df_Sales` (`Total_Amount`)
3. Take a 7-day centered rolling mean, then run STL decomposition (statsmodels) with period=7 and period=30.
4. Flag outliers with an IQR upper bound (Q3 + 1.5·IQR) on daily quantity.

## Forecasting (`notebooks/02_forecast.ipynb`)

Builds the same zero-filled daily series via `src/data.py` (`load_merged`, `daily_series`), imported with `sys.path.append('..')`. Compares a plain average, last-8-weeks average, weekday average and Prophet (with and without capped outliers) on a 28-day holdout and a 6-fold rolling backtest, scored by MAE. Prophet runs with yearly seasonality off (only one year of data), and its `cmdstanpy` logger is disabled to keep outputs clean. Figures are saved to `reports/figures/`.

Key result: no model beats the plain average, daily or weekly. The data shows no trend or reliable weekly pattern. The final forecast is the average weekly total with a 10th–90th percentile range.

## Layout conventions

- `src/`: reusable Python modules. Logic moves here when it gets reused across notebooks; `src/data.py` loads the data and builds the daily series. `01_eda` still has its own inline version.
- `reports/figures/`: saved plot outputs.
- Number new notebooks sequentially (`02_...`, `03_...`).

## Progress

**Finished on 2026-10-12:**
- Set up `.venv` and the `sales-forecast` kernel.
- Fixed the pandas 3 `select_dtypes` deprecation warning.
- Added the Data Quality section. The only issue it found was 30 days with no sales.
- Filled those 30 days with 0 in the daily series.
- The notebook runs cleanly end to end.

**Finished on 2026-10-21:**
- Built `notebooks/02_forecast.ipynb` and `src/data.py`.
- Tested Prophet and simple baselines; none beat the plain average.
- Outliers kept (capping made under 0.5% difference).
- Forecast for the 4 weeks ending 2026-02-21 to 2026-03-14: about 486 units/week (range 314–655) and $1.22M/week (range $726K–$1.68M).

**Possible next steps** (none decided yet):
- Forecast by Segment or Product Category to see if any sub-series has structure.
- Switch `01_eda` to use `src/data.py`.
- Get more history or forward-looking data (e.g. upcoming orders), which is what would actually improve accuracy.
