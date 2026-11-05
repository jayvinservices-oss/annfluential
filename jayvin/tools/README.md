# Jayvin tools

## management_pack.py

Builds the monthly management pack for a Books to Board or Fractional CFO client from three files:

1. a QuickBooks Online **Profit and Loss** export with months as columns (CSV or XLSX);
2. a **budget** CSV; and
3. a **cash inputs** CSV for the 13-week forecast.

It writes to `out/`:

| File | What it is |
|---|---|
| `<client>-<YYYY-MM>-management-pack.xlsx` | Sheets: **Summary** (month and year to date, budget against actual, variance $ and %, flags), **Variance notes** (one row per flagged line, with a note to fill in), **Cash** (13-week forecast), **Actuals by month** (what the parser read, for checking) |
| `<client>-<YYYY-MM>-summary.html` | One-page summary in house style (Georgia, black text, no lines except under table headings and above totals). Print to PDF from a browser |
| `<client>-<YYYY-MM>-summary.pdf` | The same page as a PDF. Uses Georgia if the font is installed, otherwise Times (the script says so) |

### Requirements

Python 3.9 or later with `pandas` and `openpyxl`. `reportlab` is optional (for the PDF). If they are missing:

```bash
python3 -m venv tools/.venv
tools/.venv/bin/pip install pandas openpyxl reportlab
tools/.venv/bin/python tools/management_pack.py ...
```

### Run it

From the `jayvin` folder:

```bash
python3 tools/management_pack.py \
  --pl samples/maple-lane-physio-pl-2025-11-to-2026-10.csv \
  --budget samples/maple-lane-physio-budget-fy2026.csv \
  --cash samples/maple-lane-physio-cash-inputs.csv
```

Options:

| Option | Default | Meaning |
|---|---|---|
| `--client "Name Inc."` | company name on the export | Name used in titles and the file name |
| `--month 2026-10` | last month in the export | Reporting month; year to date runs from the first month in the export |
| `--threshold-pct 10` | 10 | Flag a variance at or above this % of budget... |
| `--threshold-dollars 500` | 500 | ...and at or above this many dollars. Both must be met. A line with no budget is flagged on dollars alone |
| `--out folder` | `out/` | Where the files go |
| `--no-pdf` | off | Skip the PDF |

The script prints net income for the month and year, the number of flags, the cash position, and any notes (for example a budget line with no matching account).

### Getting the P&L out of QuickBooks Online

Reports > Profit and Loss. Report period: the fiscal year to date (start the export at the first month of the fiscal year, because year to date is counted from the first month in the file). Display columns by: **Months**. Run report, then Export to Excel or CSV. Accrual basis unless the client reports on cash.

The parser copes with what QuickBooks puts in the file: the company name, report title and date lines at the top; headings such as `Oct 2026`, `October 2026` or `Oct 1 - Oct 31, 2026`; the `Total` column; section headings (Income, Cost of Goods Sold, Expenses, Other Income, Other Expenses); parent accounts with sub-accounts and their `Total ...` lines; computed lines (Gross Profit, Net Operating Income, Net Other Income, Net Income); amounts like `1,234.56`, `(1,234.56)`, `-1,234.56` and `$1,234.56`; blank cells; and the "Accrual basis ..." footer.

It then recalculates net income for every month and compares it with the export's own Net Income line. If they differ by more than 5 cents it says so, which usually means a line was skipped.

### Budget CSV

One row per account per month. Account names must match QuickBooks (case does not matter). For a sub-account, use the sub-account's own name.

```csv
account,month,amount
Physiotherapy Revenue,2026-10,82140.00
Rent,2026-10,9500.00
```

`month` can be `2026-10` or `Oct 2026`. Enter every amount as a positive number, the way it shows on the P&L (Discounts and Refunds, which is negative on the P&L, is negative in the budget too). An optional `section` column (Income, Cost of Goods Sold, Expenses, Other Income, Other Expenses) places budget lines that have no actuals yet; without it they go under Expenses.

You can export the budget from QuickBooks (Budgets > run the Budget Overview report) and reshape it to these three columns.

### Cash inputs CSV

```csv
week_start,type,line,amount
2026-11-02,opening_balance,Operating chequing balance at 31 Oct 2026 (per statement),48216.37
2026-11-02,minimum_balance,Minimum cash the owner wants to hold,25000.00
2026-11-02,receipt,Patient and insurer payments,19044.18
2026-11-09,payment,Net payroll (biweekly),12650.00
```

- `opening_balance` (required, one row): the bank balance at the start of week 1, tied to the statement. The earliest date in the file is week 1, and the forecast runs 13 weeks from there.
- `minimum_balance` (optional): the cushion the owner wants. Weeks that close below it are called out.
- `receipt` and `payment`: positive amounts, including HST where it applies. A date in the middle of a week is put into that week. Lines dated after week 13 are left out and counted in the notes.

### Variance sign convention

Variance = actual less budget. For income lines a positive variance is favourable. For cost lines (Cost of Goods Sold, Expenses, Other Expenses) a positive variance is unfavourable. The Direction column says which.

### After the run

1. Open the Variance notes sheet. For each flagged row, write the driver, whether it is one-off or ongoing, and any action. Claude drafts these from the transaction detail; Ann edits and approves.
2. Copy the agreed notes into the summary or the client's pack.
3. Check the Actuals by month sheet ties to the P&L in QuickBooks before anything goes to the client.

## Sample data

`samples/` holds a fictional clinic, Maple Lane Physio Inc. (6 staff, Toronto, fiscal year 1 November 2025 to 31 October 2026). All figures are invented. `python3 samples/make_sample_data.py` rebuilds the sample files; the October 2026 pack built from them is in `out/`.
