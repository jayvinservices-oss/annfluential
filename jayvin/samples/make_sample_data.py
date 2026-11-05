#!/usr/bin/env python3
"""Build the fictional Maple Lane Physio Inc. sample files.

Everything here is invented. Maple Lane Physio Inc. is not a real company.

Writes, next to this script:
  maple-lane-physio-pl-2025-11-to-2026-10.csv   QuickBooks Online style P&L export (monthly columns)
  maple-lane-physio-pl-2025-11-to-2026-10.xlsx  the same export as QuickBooks lays it out in Excel
  maple-lane-physio-budget-fy2026.csv           budget: account, month, amount
  maple-lane-physio-cash-inputs.csv             opening bank balance and 13 weeks of receipts and payments

Fiscal year: 1 November 2025 to 31 October 2026. Six staff on payroll, Toronto.
Run:  python3 samples/make_sample_data.py
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
MONTHS = [(2025, 11), (2025, 12)] + [(2026, m) for m in range(1, 11)]
LABELS = [date(y, m, 1).strftime("%b %Y") for y, m in MONTHS]
KEYS = [f"{y}-{m:02d}" for y, m in MONTHS]

# Seasonality for patient visits (1.0 = normal month)
SEASON = [1.00, 0.86, 1.08, 1.02, 1.06, 1.00, 1.03, 0.97, 0.94, 0.88, 1.01, 1.07]

# Budget: what the owner planned at the start of the year.
# (section, parent or None, account, monthly base, seasonal?)
PLAN = [
    ("Income", None, "Physiotherapy Revenue", 78000, True),
    ("Income", None, "Kinesiology and Active Rehab Revenue", 9200, True),
    ("Income", None, "Product Sales", 3100, True),
    ("Income", None, "Discounts and Refunds", -450, False),
    ("Cost of Goods Sold", None, "Contract Physiotherapists", 18500, True),
    ("Cost of Goods Sold", None, "Product Cost", 1650, True),
    ("Cost of Goods Sold", None, "Merchant and Payment Processing Fees", 1900, True),
    ("Expenses", "Payroll Expenses", "Wages and Salaries", 34500, False),
    ("Expenses", "Payroll Expenses", "Employer CPP and EI", 2350, False),
    ("Expenses", "Payroll Expenses", "Employee Benefits", 1850, False),
    ("Expenses", "Payroll Expenses", "WSIB Premiums", 620, False),
    ("Expenses", None, "Accounting and Legal Fees", 1250, False),
    ("Expenses", None, "Advertising and Marketing", 2000, False),
    ("Expenses", None, "Bank Charges", 85, False),
    ("Expenses", None, "Clinical Supplies", 1200, True),
    ("Expenses", None, "Dues and Subscriptions", 300, False),
    ("Expenses", None, "Insurance", 650, False),
    ("Expenses", None, "Interest Expense", 310, False),
    ("Expenses", None, "Office Supplies", 280, False),
    ("Expenses", None, "Rent", 9500, False),
    ("Expenses", None, "Repairs and Maintenance", 400, False),
    ("Expenses", None, "Software and Subscriptions", 860, False),
    ("Expenses", None, "Telephone and Internet", 420, False),
    ("Expenses", None, "Training and Development", 450, False),
    ("Expenses", None, "Utilities", 600, False),
    ("Other Income", None, "Interest Income", 60, False),
    ("Other Expenses", None, "Amortization Expense", 1450, False),
]

# What actually happened (deliberate, explainable differences from budget)
EVENTS = {
    # account: {month_key: multiplier or ("add", amount)}
    "Physiotherapy Revenue": {"2026-09": 0.93, "2026-10": 0.87},       # associate physio on leave from mid-September
    "Contract Physiotherapists": {"2026-09": 1.18, "2026-10": 1.32},   # contract physio covering the leave
    "Wages and Salaries": {"2026-09": 0.95, "2026-10": 0.84},          # leave is unpaid by the clinic (EI maternity)
    "Employer CPP and EI": {"2026-01": 1.45, "2026-02": 1.25, "2026-10": 0.84},  # contribution year resets in January
    "Advertising and Marketing": {"2026-03": 1.6, "2026-10": 2.35},    # fall Google Ads campaign
    "Repairs and Maintenance": {"2026-10": ("add", 3800)},              # HVAC compressor repair
    "Dues and Subscriptions": {"2025-11": ("add", 2350)},               # College of Physiotherapists renewals
    "Training and Development": {"2026-05": ("add", 1900)},             # manual therapy course
    "Insurance": {"2026-04": 1.12, "2026-05": 1.12, "2026-06": 1.12, "2026-07": 1.12,
                  "2026-08": 1.12, "2026-09": 1.12, "2026-10": 1.12},  # renewal increase
    "Product Sales": {"2026-10": 1.22},
    "Product Cost": {"2026-10": 1.22},
}

BUDGET_GROWTH = 1.0  # budget already reflects planned visits


def r2(x):
    return round(x + 1e-9, 2)


def budget_amount(acct, base, seasonal, i):
    return r2(base * (SEASON[i] if seasonal else 1.0) * BUDGET_GROWTH)


def build():
    rng = random.Random(20261105)
    budget, actual = {}, {}
    for section, parent, acct, base, seasonal in PLAN:
        budget[acct] = [budget_amount(acct, base, seasonal, i) for i in range(12)]
        row = []
        for i, k in enumerate(KEYS):
            b = budget[acct][i]
            noise = 1 + rng.uniform(-0.035, 0.035)
            if acct in ("Rent", "Interest Expense", "Amortization Expense", "WSIB Premiums", "Employee Benefits"):
                noise = 1.0
            v = b * noise
            ev = EVENTS.get(acct, {}).get(k)
            if isinstance(ev, tuple):
                v += ev[1]
            elif ev:
                v *= ev
            row.append(r2(v))
        actual[acct] = row
    # Merchant fees follow actual revenue, about 2.1% of physio and product revenue
    actual["Merchant and Payment Processing Fees"] = [
        r2(0.021 * (actual["Physiotherapy Revenue"][i] + actual["Kinesiology and Active Rehab Revenue"][i]
                    + actual["Product Sales"][i])) for i in range(12)]
    return budget, actual


def fmt(v):
    return f"{v:,.2f}"


def pl_rows(actual):
    """Lay out rows the way a QuickBooks Online P&L export does."""
    rows = [["Maple Lane Physio Inc."], ["Profit and Loss"], ["November 2025 - October 2026"], []]
    rows.append([""] + LABELS + ["Total"])

    def line(name, vals, indent):
        return [" " * indent + name] + [fmt(v) for v in vals] + [fmt(sum(vals))]

    sums = {}
    order = ["Income", "Cost of Goods Sold", "Expenses", "Other Income", "Other Expenses"]
    for section in order:
        rows.append([section])
        tot = [0.0] * 12
        current_parent = None
        parent_tot = None
        for sec, parent, acct, *_ in PLAN:
            if sec != section:
                continue
            if parent != current_parent:
                if current_parent:
                    rows.append(line("Total " + current_parent, parent_tot, 3))
                if parent:
                    rows.append(["   " + parent])
                    parent_tot = [0.0] * 12
                current_parent = parent
            vals = actual[acct]
            rows.append(line(acct, vals, 6 if parent else 3))
            if parent:
                parent_tot = [r2(a + b) for a, b in zip(parent_tot, vals)]
            tot = [r2(a + b) for a, b in zip(tot, vals)]
        if current_parent:
            rows.append(line("Total " + current_parent, parent_tot, 3))
        rows.append(line("Total " + section, tot, 0))
        sums[section] = tot
        if section == "Cost of Goods Sold":
            rows.append(line("Gross Profit", [r2(a - b) for a, b in zip(sums["Income"], tot)], 0))
        if section == "Expenses":
            gp = [r2(a - b) for a, b in zip(sums["Income"], sums["Cost of Goods Sold"])]
            sums["NOI"] = [r2(a - b) for a, b in zip(gp, tot)]
            rows.append(line("Net Operating Income", sums["NOI"], 0))
    noi = [r2(a - b) for a, b in zip(sums["Other Income"], sums["Other Expenses"])]
    rows.append(line("Net Other Income", noi, 0))
    rows.append(line("Net Income", [r2(a + b) for a, b in zip(sums["NOI"], noi)], 0))
    rows += [[], [], ["Accrual basis Wednesday, November 4, 2026 09:12 AM GMT-05:00"]]
    return rows, [r2(a + b) for a, b in zip(sums["NOI"], noi)]


def write_xlsx(rows, path):
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Profit and Loss"
    for r in rows:
        out = []
        for j, c in enumerate(r):
            if j > 0 and c not in ("", "Total") and c is not None and not c.startswith(("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")):
                try:
                    out.append(float(c.replace(",", "")))
                    continue
                except ValueError:
                    pass
            out.append(c)
        ws.append(out)
    wb.save(path)


def cash_inputs(actual):
    """13 weeks from Monday 2 November 2026. Receipts and payments include HST where it applies."""
    start = date(2026, 11, 2)
    weeks = [start + timedelta(weeks=w) for w in range(13)]
    rows = [("2026-11-02", "opening_balance", "Operating chequing balance at 31 Oct 2026 (per statement)", 48216.37),
            ("2026-11-02", "minimum_balance", "Minimum cash the owner wants to hold", 25000.00)]
    monthly_rev = (actual["Physiotherapy Revenue"][-1] + actual["Kinesiology and Active Rehab Revenue"][-1])
    for i, wk in enumerate(weeks):
        d = wk.isoformat()
        hol = 0.55 if wk in (date(2026, 12, 21), date(2026, 12, 28)) else 1.0
        rows.append((d, "receipt", "Patient and insurer payments", r2(monthly_rev / 4.33 * hol * (1.04 if i >= 4 else 1.0))))
        rows.append((d, "receipt", "Product sales incl. HST", r2(3100 * 1.13 / 4.33 * hol)))
        if i % 2 == 1:
            rows.append((d, "payment", "Net payroll (biweekly)", 12650.00))
            rows.append((d, "payment", "Contract physiotherapists (biweekly fee split)", 11400.00 if i < 7 else 9800.00))
        # November rent was paid on 30 October, so the forecast picks up December and January
        if any(wk <= m < wk + timedelta(days=7) for m in (date(2026, 12, 1), date(2027, 1, 1))):
            rows.append((d, "payment", "Rent incl. HST", 10735.00))
            rows.append((d, "payment", "Software, phone, internet, utilities", 2210.00))
            rows.append((d, "payment", "Loan payment (principal and interest)", 1850.00))
            rows.append((d, "payment", "Group benefits premium", 1850.00))
        for m in (date(2026, 11, 15), date(2026, 12, 15), date(2027, 1, 15)):
            if wk <= m < wk + timedelta(days=7):
                rows.append((d, "payment", "CRA payroll remittance (CPP, EI, tax)", 9620.00))
        if i in (1, 5, 9):
            rows.append((d, "payment", "Clinical and product suppliers", 3400.00))
            rows.append((d, "payment", "Advertising (Google Ads)", 2100.00 if i == 1 else 1500.00))
        if i == 1:
            rows.append((d, "payment", "HVAC repair invoice (October work)", 4294.00))
        if i == 3:
            rows.append((d, "payment", "Accounting fees", 1412.50))
        if i == 6:
            rows.append((d, "payment", "Year-end staff bonuses (net)", 6000.00))
        if i == 12:
            rows.append((d, "payment", "HST remittance (quarter to 31 Dec)", 1180.00))
        if i in (4, 8, 12):
            rows.append((d, "payment", "WSIB premiums", 620.00))
        if i == 0:
            rows.append((d, "payment", "Insurance (monthly)", 728.00))
        if i in (4, 9):
            rows.append((d, "payment", "Insurance (monthly)", 728.00))
    return rows


def main():
    budget, actual = build()
    rows, net = pl_rows(actual)
    base = "maple-lane-physio-pl-2025-11-to-2026-10"
    with open(HERE / f"{base}.csv", "w", newline="") as f:
        csv.writer(f).writerows(rows)
    write_xlsx(rows, HERE / f"{base}.xlsx")
    with open(HERE / "maple-lane-physio-budget-fy2026.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["account", "month", "amount"])
        for _, _, acct, *_ in PLAN:
            for k, v in zip(KEYS, budget[acct]):
                w.writerow([acct, k, f"{v:.2f}"])
    with open(HERE / "maple-lane-physio-cash-inputs.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["week_start", "type", "line", "amount"])
        w.writerows([(a, b, c, f"{d:.2f}") for a, b, c, d in cash_inputs(actual)])
    print("Net income by month:", [f"{v:,.0f}" for v in net])
    print("Net income for the year:", f"{sum(net):,.2f}")


if __name__ == "__main__":
    main()
