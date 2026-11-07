#!/usr/bin/env python3
"""Jayvin management pack builder.

Reads a QuickBooks Online Profit and Loss export (CSV or XLSX, monthly columns), a budget CSV
and a 13-week cash inputs CSV, and writes:

  out/<client-slug>-<YYYY-MM>-management-pack.xlsx   sheets: Summary, Variance notes, Cash, Actuals by month
  out/<client-slug>-<YYYY-MM>-summary.html           one-page summary in house style (Georgia, black text)
  out/<client-slug>-<YYYY-MM>-summary.pdf            the same page as a PDF (if reportlab is installed)

See tools/README.md for the input formats and options.
"""
from __future__ import annotations

import argparse
import csv
import html
import math
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, Side
from openpyxl.utils import get_column_letter

# Sections as QuickBooks Online names them (Canada and US), mapped to a sign for "favourable".
# +1: higher actual than budget is good (income). -1: lower is good (costs).
SECTIONS = {
    "income": ("Income", 1),
    "revenue": ("Income", 1),
    "cost of goods sold": ("Cost of Goods Sold", -1),
    "cost of sales": ("Cost of Goods Sold", -1),
    "expenses": ("Expenses", -1),
    "expense": ("Expenses", -1),
    "other income": ("Other Income", 1),
    "other expenses": ("Other Expenses", -1),
    "other expense": ("Other Expenses", -1),
}
SECTION_ORDER = ["Income", "Cost of Goods Sold", "Expenses", "Other Income", "Other Expenses"]
COMPUTED_LINES = {"gross profit", "net operating income", "net other income", "net income",
                  "net revenue", "net earnings", "net operating revenue"}
MONTH_FORMATS = ["%b %Y", "%B %Y", "%b. %Y", "%b-%y", "%B, %Y", "%Y-%m", "%m/%Y"]

INK = "000000"  # Jayvin: black text, no accent colour
FONT = "Georgia"


# ---------------------------------------------------------------- parsing helpers

def parse_amount(value) -> float | None:
    """Turn a QuickBooks cell into a number. Handles 1,234.56, (1,234.56), -1,234.56, $ and blanks."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return None
        return float(value)
    s = str(value).strip().replace("$", "").replace("\u00a0", "").replace(" ", "")
    if s in ("", "-", "--"):
        return None
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()").replace(",", "")
    if s.endswith("-"):  # 1,234.56- style
        neg, s = True, s[:-1]
    try:
        v = float(s)
    except ValueError:
        return None
    return -v if neg else v


def parse_period(label) -> str | None:
    """Return YYYY-MM for a column header such as 'Oct 2026', 'October 2026' or 'Oct 1 - Oct 31, 2026'."""
    if label is None:
        return None
    if isinstance(label, (datetime, date)):
        return f"{label.year}-{label.month:02d}"
    s = str(label).strip()
    if not s or s.lower().startswith("total"):
        return None
    if " - " in s or "–" in s:  # a date range: take the end date
        s = re.split(r"\s+[-–]\s+", s)[-1]
    s = s.replace(",", "").strip()
    for fmt in MONTH_FORMATS + ["%b %d %Y", "%B %d %Y", "%d %b %Y", "%Y-%m-%d"]:
        try:
            d = datetime.strptime(s, fmt.replace(",", ""))
            return f"{d.year}-{d.month:02d}"
        except ValueError:
            continue
    return None


def read_rows(path: Path) -> list[list]:
    """Read a CSV or XLSX export into a list of rows (lists of cells)."""
    if path.suffix.lower() in (".xlsx", ".xlsm"):
        from openpyxl import load_workbook
        wb = load_workbook(path, data_only=True, read_only=True)
        ws = wb.worksheets[0]
        return [list(r) for r in ws.iter_rows(values_only=True)]
    for enc in ("utf-8-sig", "cp1252"):
        try:
            with open(path, newline="", encoding=enc) as f:
                return [row for row in csv.reader(f)]
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not read {path}")


@dataclass
class PL:
    company: str
    periods: list[str]
    lines: pd.DataFrame          # columns: section, parent, account, then one column per period
    warnings: list[str] = field(default_factory=list)


def parse_qbo_pl(path: Path) -> PL:
    rows = read_rows(path)
    company = ""
    for r in rows:
        if r and r[0] and str(r[0]).strip():
            company = str(r[0]).strip()
            break

    # Header row: the first row with at least two cells that read as months.
    header_idx, col_periods = None, {}
    for i, r in enumerate(rows[:40]):
        found = {j: parse_period(c) for j, c in enumerate(r) if j > 0}
        found = {j: p for j, p in found.items() if p}
        if len(found) >= 2:
            header_idx, col_periods = i, found
            break
    if header_idx is None:
        raise ValueError("Could not find a row of month headings. Run the QuickBooks P&L with "
                         "'Display columns by: Months' and export again.")
    periods = sorted(set(col_periods.values()))
    if len(periods) != len(col_periods):
        raise ValueError("Two columns have the same month heading.")

    warnings = []
    records, section, sign_section = [], None, None
    parents: list[str] = []
    for r in rows[header_idx + 1:]:
        if not r or all(c is None or str(c).strip() == "" for c in r):
            continue
        raw = r[0] if r[0] is not None else ""
        name = str(raw).strip()
        if not name:
            continue
        low = name.lower()
        amounts = {p: parse_amount(r[j]) if j < len(r) else None for j, p in col_periods.items()}
        has_numbers = any(v is not None for v in amounts.values())
        if low in SECTIONS and not has_numbers:
            section, parents = SECTIONS[low][0], []
            continue
        if low.startswith(("accrual basis", "cash basis")):
            break
        if low == "total" or low.startswith("total "):
            target = name[5:].strip()
            if parents and target.lower() == parents[-1].lower():
                parents.pop()
            continue
        if low in COMPUTED_LINES:
            continue
        if not has_numbers:
            if section is None:
                continue  # stray title lines
            parents.append(name)  # a parent account heading
            continue
        if section is None:
            warnings.append(f"Line '{name}' appears before any section heading; treated as Expenses.")
            section = "Expenses"
        rec = {"section": section, "parent": ":".join(parents), "account": name}
        rec.update({p: (amounts[p] or 0.0) for p in periods})
        records.append(rec)

    df = pd.DataFrame(records, columns=["section", "parent", "account"] + periods)
    if df.empty:
        raise ValueError("No account lines found in the P&L export.")
    dupes = df[df.duplicated("account", keep=False)]
    if not dupes.empty:
        # same sub-account name under two parents: qualify with the parent
        mask = df.duplicated("account", keep=False) & (df["parent"] != "")
        df.loc[mask, "account"] = df.loc[mask, "parent"] + ":" + df.loc[mask, "account"]
    return PL(company=company, periods=periods, lines=df, warnings=warnings)


def check_totals(path: Path, pl: PL) -> list[str]:
    """Compare our recalculated Net Income with the export's own Net Income line, month by month."""
    rows = read_rows(path)
    hdr = None
    for i, r in enumerate(rows[:40]):
        if sum(1 for j, c in enumerate(r) if j > 0 and parse_period(c)) >= 2:
            hdr = i
            break
    cols = {j: parse_period(c) for j, c in enumerate(rows[hdr]) if j > 0 and parse_period(c)}
    exported = None
    for r in rows[hdr + 1:]:
        if r and str(r[0] or "").strip().lower() == "net income":
            exported = {p: parse_amount(r[j]) or 0.0 for j, p in cols.items()}
    if exported is None:
        return ["The export has no Net Income line, so totals could not be cross-checked."]
    ours = net_income_by_period(pl.lines, pl.periods)
    out = []
    for p in pl.periods:
        if abs(ours[p] - exported[p]) > 0.05:
            out.append(f"Net income for {p} recalculates to {ours[p]:,.2f} but the export shows "
                       f"{exported[p]:,.2f}. Check for lines the parser skipped.")
    return out


def net_income_by_period(lines: pd.DataFrame, periods: list[str]) -> dict[str, float]:
    res = {}
    for p in periods:
        s = lines.groupby("section")[p].sum()
        res[p] = round(s.get("Income", 0) - s.get("Cost of Goods Sold", 0) - s.get("Expenses", 0)
                       + s.get("Other Income", 0) - s.get("Other Expenses", 0), 2)
    return res


def read_budget(path: Path) -> pd.DataFrame:
    b = pd.read_csv(path, dtype=str).rename(columns=lambda c: c.strip().lower())
    missing = {"account", "month", "amount"} - set(b.columns)
    if missing:
        raise ValueError(f"Budget CSV is missing columns: {', '.join(sorted(missing))}")
    b["month"] = b["month"].map(lambda m: parse_period(m) or str(m).strip())
    b["amount"] = b["amount"].map(lambda v: parse_amount(v) or 0.0)
    b["account"] = b["account"].str.strip()
    if "section" not in b.columns:
        b["section"] = ""
    return b


def read_cash(path: Path) -> dict:
    c = pd.read_csv(path, dtype=str).rename(columns=lambda x: x.strip().lower())
    missing = {"week_start", "type", "line", "amount"} - set(c.columns)
    if missing:
        raise ValueError(f"Cash inputs CSV is missing columns: {', '.join(sorted(missing))}")
    c["type"] = c["type"].str.strip().str.lower()
    c["amount"] = c["amount"].map(lambda v: parse_amount(v) or 0.0)
    c["week_start"] = pd.to_datetime(c["week_start"].str.strip()).dt.date
    opening = c.loc[c["type"] == "opening_balance", "amount"]
    if opening.empty:
        raise ValueError("Cash inputs need one row with type 'opening_balance'.")
    minimum = c.loc[c["type"] == "minimum_balance", "amount"]
    flows = c[c["type"].isin(["receipt", "payment"])].copy()
    first = min(c["week_start"])
    weeks = [first + pd.Timedelta(weeks=i).to_pytimedelta() for i in range(13)]
    late = flows[flows["week_start"] > weeks[-1]]
    flows = flows[flows["week_start"] <= weeks[-1]]
    # snap any mid-week dates to the week they fall in
    flows["week"] = flows["week_start"].map(lambda d: max(w for w in weeks if w <= d))
    return {"opening": float(opening.iloc[0]), "minimum": float(minimum.iloc[0]) if not minimum.empty else None,
            "weeks": weeks, "flows": flows, "ignored": len(late)}


# ---------------------------------------------------------------- analysis

def build_summary(pl: PL, budget: pd.DataFrame, month: str, pct: float, min_dollars: float):
    if month not in pl.periods:
        raise ValueError(f"Month {month} is not in the P&L export (it has {pl.periods[0]} to {pl.periods[-1]}).")
    ytd = [p for p in pl.periods if p <= month]
    lines = pl.lines.copy()
    bud_month = budget[budget["month"] == month].groupby("account")["amount"].sum()
    bud_ytd = budget[budget["month"].isin(ytd)].groupby("account")["amount"].sum()

    acct_lower = {a.lower(): a for a in lines["account"]}
    warnings = []
    extra = []
    for a in sorted(set(budget["account"])):
        if a.lower() not in acct_lower:
            sec = budget.loc[budget["account"] == a, "section"].iloc[0]
            sec = SECTIONS.get(str(sec).strip().lower(), (None,))[0] or "Expenses"
            extra.append({"section": sec, "parent": "", "account": a, **{p: 0.0 for p in pl.periods}})
            warnings.append(f"Budget line '{a}' has no actuals in the export; shown with zero actuals "
                            f"under {sec}. Check the account name matches QuickBooks.")
    if extra:
        lines = pd.concat([lines, pd.DataFrame(extra)], ignore_index=True)
    bm = {k.lower(): v for k, v in bud_month.items()}
    by = {k.lower(): v for k, v in bud_ytd.items()}
    out = []
    for _, r in lines.iterrows():
        key = r["account"].lower()
        sign = dict((v[0], v[1]) for v in SECTIONS.values())[r["section"]]
        rec = {
            "section": r["section"], "parent": r["parent"], "account": r["account"], "sign": sign,
            "m_act": round(r[month], 2), "m_bud": round(bm.get(key, 0.0), 2),
            "y_act": round(sum(r[p] for p in ytd), 2), "y_bud": round(by.get(key, 0.0), 2),
        }
        out.append(rec)
    df = pd.DataFrame(out)
    for k in ("m", "y"):
        df[f"{k}_var"] = (df[f"{k}_act"] - df[f"{k}_bud"]).round(2)
        df[f"{k}_pct"] = df.apply(lambda x: (x[f"{k}_var"] / abs(x[f"{k}_bud"])) if x[f"{k}_bud"] else None, axis=1)
        df[f"{k}_fav"] = df.apply(lambda x: "" if abs(x[f"{k}_var"]) < 0.005 else
                                  ("Favourable" if x[f"{k}_var"] * x["sign"] > 0 else "Unfavourable"), axis=1)
        df[f"{k}_flag"] = df.apply(lambda x: abs(x[f"{k}_var"]) >= min_dollars and
                                   (x[f"{k}_pct"] is None or pd.isna(x[f"{k}_pct"]) or abs(x[f"{k}_pct"]) >= pct),
                                   axis=1)
    df["section_rank"] = df["section"].map(SECTION_ORDER.index)
    df = df.sort_values(["section_rank"], kind="stable").reset_index(drop=True)
    return df, ytd, warnings


def totals(df: pd.DataFrame) -> dict:
    cols = ["m_act", "m_bud", "y_act", "y_bud"]
    s = {sec: {c: df.loc[df["section"] == sec, c].sum() for c in cols} for sec in SECTION_ORDER}
    t = {}
    for c in cols:
        t.setdefault("Total Income", {})[c] = s["Income"][c]
        t.setdefault("Total Cost of Goods Sold", {})[c] = s["Cost of Goods Sold"][c]
        t.setdefault("Gross Profit", {})[c] = s["Income"][c] - s["Cost of Goods Sold"][c]
        t.setdefault("Total Expenses", {})[c] = s["Expenses"][c]
        t.setdefault("Net Operating Income", {})[c] = t["Gross Profit"][c] - s["Expenses"][c]
        t.setdefault("Net Other Income", {})[c] = s["Other Income"][c] - s["Other Expenses"][c]
        t.setdefault("Net Income", {})[c] = t["Net Operating Income"][c] + t["Net Other Income"][c]
        t.setdefault("_sections", s)
    return t


def cash_table(cash: dict):
    weeks, flows = cash["weeks"], cash["flows"]
    table = {}
    for kind in ("receipt", "payment"):
        sub = flows[flows["type"] == kind]
        order = list(dict.fromkeys(sub["line"]))
        table[kind] = [(ln, [round(sub[(sub["line"] == ln) & (sub["week"] == w)]["amount"].sum(), 2) for w in weeks])
                       for ln in order]
    opening, closing, rec_t, pay_t = [], [], [], []
    bal = cash["opening"]
    for i in range(13):
        rt = sum(v[i] for _, v in table["receipt"])
        pt = sum(v[i] for _, v in table["payment"])
        opening.append(round(bal, 2))
        bal = bal + rt - pt
        rec_t.append(round(rt, 2)); pay_t.append(round(pt, 2)); closing.append(round(bal, 2))
    return {"weeks": weeks, "receipts": table["receipt"], "payments": table["payment"], "opening": opening,
            "rec_total": rec_t, "pay_total": pay_t, "net": [round(a - b, 2) for a, b in zip(rec_t, pay_t)],
            "closing": closing, "minimum": cash["minimum"]}


# ---------------------------------------------------------------- Excel output

def month_name(p: str) -> str:
    y, m = p.split("-")
    return date(int(y), int(m), 1).strftime("%B %Y")


def write_xlsx(path: Path, client: str, month: str, ytd: list[str], df: pd.DataFrame, t: dict, ct: dict,
               pl: PL, pct: float, min_dollars: float, notes_text: list[str]):
    wb = Workbook()
    f_body = Font(name=FONT, size=10, color=INK)
    f_bold = Font(name=FONT, size=10, bold=True, color=INK)
    f_title = Font(name=FONT, size=14, bold=True, color=INK)
    f_small = Font(name=FONT, size=9, color=INK, italic=True)
    thin = Side(style="thin", color="808080")
    money = '#,##0;(#,##0);"-"'
    money2 = '#,##0.00;(#,##0.00);"-"'
    pctf = '0.0%;(0.0%);"-"'

    def style_sheet(ws):
        ws.sheet_view.showGridLines = False
        for row in ws.iter_rows():
            for c in row:
                if c.font is None or c.font.name != FONT:
                    c.font = f_body

    def fit_wide(ws):
        ws.page_setup.orientation = "landscape"
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0

    def title(ws, text, sub):
        ws["A1"] = text; ws["A1"].font = f_title
        ws["A2"] = sub; ws["A2"].font = f_body
        ws["A3"] = "Prepared with the assistance of Jayvin Consulting Inc. Draft for review."
        ws["A3"].font = f_small

    # Summary --------------------------------------------------------------------
    ws = wb.active
    ws.title = "Summary"
    title(ws, f"{client}: management summary",
          f"{month_name(month)} and year to date ({month_name(ytd[0])} to {month_name(month)})")
    hdr = ["Account", "Month actual", "Month budget", "Variance $", "Variance %", "",
           "YTD actual", "YTD budget", "Variance $", "Variance %", "Flag"]
    r0 = 5
    for j, h in enumerate(hdr, 1):
        c = ws.cell(row=r0, column=j, value=h)
        c.font = f_bold; c.border = Border(bottom=thin)
        c.alignment = Alignment(horizontal="left" if j == 1 else "right", wrap_text=True)
    row = r0 + 1

    def put_line(label, ma, mb, ya, yb, sign, bold=False, flag="", indent=1, total=False):
        nonlocal row
        mv, yv = ma - mb, ya - yb
        vals = [label, ma, mb, mv, (mv / abs(mb)) if mb else None, None, ya, yb, yv, (yv / abs(yb)) if yb else None, flag]
        for j, v in enumerate(vals, 1):
            c = ws.cell(row=row, column=j, value=v)
            c.font = f_bold if bold else f_body
            if j in (2, 3, 4, 7, 8, 9):
                c.number_format = money
            if j in (5, 10):
                c.number_format = pctf
            if total:
                c.border = Border(top=thin)
        ws.cell(row=row, column=1).alignment = Alignment(indent=indent)
        row += 1

    for sec in SECTION_ORDER:
        sub = df[df["section"] == sec]
        if sub.empty:
            continue
        ws.cell(row=row, column=1, value=sec).font = f_bold
        row += 1
        for _, x in sub.iterrows():
            flag = []
            if x["m_flag"]:
                flag.append("Month")
            if x["y_flag"]:
                flag.append("YTD")
            label = (x["parent"] + ": " if x["parent"] else "") + x["account"]
            put_line(label, x["m_act"], x["m_bud"], x["y_act"], x["y_bud"], x["sign"],
                     flag=" and ".join(flag), indent=2)
        s = t["_sections"][sec]
        put_line(f"Total {sec}", s["m_act"], s["m_bud"], s["y_act"], s["y_bud"], 1, bold=True, total=True)
        if sec == "Cost of Goods Sold":
            g = t["Gross Profit"]
            put_line("Gross Profit", g["m_act"], g["m_bud"], g["y_act"], g["y_bud"], 1, bold=True)
        if sec == "Expenses":
            g = t["Net Operating Income"]
            put_line("Net Operating Income", g["m_act"], g["m_bud"], g["y_act"], g["y_bud"], 1, bold=True)
        row += 1
    g = t["Net Income"]
    put_line("Net Income", g["m_act"], g["m_bud"], g["y_act"], g["y_bud"], 1, bold=True, total=True)
    row += 1
    ws.cell(row=row, column=1, value=(
        f"Flag rule: variance of at least ${min_dollars:,.0f} and at least {pct:.0%} of budget "
        f"(or any variance of ${min_dollars:,.0f} or more where there is no budget). "
        "Variance is actual less budget; for income a positive variance is favourable, for costs a negative "
        "variance is favourable.")).font = f_small
    row += 1
    ws.cell(row=row, column=1, value=f"Cash: opening balance ${ct['opening'][0]:,.2f}; lowest forecast week-end "
            f"balance ${min(ct['closing']):,.2f} (see the Cash sheet).").font = f_small
    for msg in notes_text:
        row += 1
        ws.cell(row=row, column=1, value=msg).font = f_small
    widths = [44, 13, 13, 12, 10, 2, 13, 13, 12, 10, 12]
    for j, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = ws.cell(row=r0 + 1, column=2)
    fit_wide(ws)
    style_sheet(ws)

    # Variance notes -------------------------------------------------------------
    wn = wb.create_sheet("Variance notes")
    title(wn, f"{client}: variance notes", f"{month_name(month)}. One row per flagged line. "
          "Fill in the note column, then copy the agreed wording into the pack.")
    hdr = ["Account", "Section", "Period", "Actual", "Budget", "Variance $", "Variance %", "Direction",
           "Note (driver, one-off or ongoing, action)", "Status"]
    for j, h in enumerate(hdr, 1):
        c = wn.cell(row=5, column=j, value=h); c.font = f_bold; c.border = Border(bottom=thin)
    rr = 6
    flagged = 0
    for _, x in df.iterrows():
        for k, label in (("m", f"Month ({month})"), ("y", f"YTD to {month}")):
            if not x[f"{k}_flag"]:
                continue
            vals = [(x["parent"] + ": " if x["parent"] else "") + x["account"], x["section"], label,
                    x[f"{k}_act"], x[f"{k}_bud"], x[f"{k}_var"], x[f"{k}_pct"], x[f"{k}_fav"],
                    "[To draft: what drove this, is it one-off or ongoing, and what (if anything) we do about it]",
                    "Draft"]
            for j, v in enumerate(vals, 1):
                c = wn.cell(row=rr, column=j, value=None if (isinstance(v, float) and pd.isna(v)) else v)
                c.font = f_body
                if j in (4, 5, 6):
                    c.number_format = money2
                if j == 7:
                    c.number_format = pctf
                if j == 9:
                    c.alignment = Alignment(wrap_text=True, vertical="top")
            rr += 1; flagged += 1
    if not flagged:
        wn.cell(row=rr, column=1, value="No lines met the flag rule this month.").font = f_body
    for j, w in enumerate([40, 18, 16, 13, 13, 13, 11, 13, 60, 10], 1):
        wn.column_dimensions[get_column_letter(j)].width = w
    fit_wide(wn)
    style_sheet(wn)

    # Cash ---------------------------------------------------------------------
    wc = wb.create_sheet("Cash")
    title(wc, f"{client}: 13-week cash forecast",
          f"Weeks starting {ct['weeks'][0]:%d %B %Y}. Receipts and payments include HST where it applies.")
    wc.cell(row=5, column=1, value="Week starting").font = f_bold
    wc.cell(row=5, column=1).border = Border(bottom=thin)
    for i, w in enumerate(ct["weeks"]):
        c = wc.cell(row=5, column=2 + i, value=w.strftime("%d %b")); c.font = f_bold
        c.border = Border(bottom=thin); c.alignment = Alignment(horizontal="right")
    c = wc.cell(row=5, column=15, value="13 weeks"); c.font = f_bold; c.border = Border(bottom=thin)
    c.alignment = Alignment(horizontal="right")
    r = 6

    def cash_row(label, vals, bold=False, total=None, top=False, indent=1):
        nonlocal r
        c = wc.cell(row=r, column=1, value=label); c.font = f_bold if bold else f_body
        c.alignment = Alignment(indent=indent)
        if top:
            c.border = Border(top=thin)
        for i, v in enumerate(vals):
            c = wc.cell(row=r, column=2 + i, value=v); c.number_format = money
            c.font = f_bold if bold else f_body
            if top:
                c.border = Border(top=thin)
        if total is not None:
            c = wc.cell(row=r, column=15, value=total); c.number_format = money
            c.font = f_bold if bold else f_body
            if top:
                c.border = Border(top=thin)
        r += 1

    cash_row("Opening balance", ct["opening"], bold=True, indent=0)
    wc.cell(row=r, column=1, value="Receipts").font = f_bold; r += 1
    for ln, vals in ct["receipts"]:
        cash_row(ln, vals, total=sum(vals), indent=2)
    cash_row("Total receipts", ct["rec_total"], bold=True, total=sum(ct["rec_total"]), top=True)
    wc.cell(row=r, column=1, value="Payments").font = f_bold; r += 1
    for ln, vals in ct["payments"]:
        cash_row(ln, vals, total=sum(vals), indent=2)
    cash_row("Total payments", ct["pay_total"], bold=True, total=sum(ct["pay_total"]), top=True)
    cash_row("Net cash flow", ct["net"], bold=True, total=sum(ct["net"]))
    cash_row("Closing balance", ct["closing"], bold=True, indent=0, top=True)
    if ct["minimum"] is not None:
        cash_row("Minimum balance wanted", [ct["minimum"]] * 13)
        cash_row("Headroom", [round(c - ct["minimum"], 2) for c in ct["closing"]], bold=True)
        lows = [ct["weeks"][i].strftime("%d %b") for i, c in enumerate(ct["closing"]) if c < ct["minimum"]]
        r += 1
        wc.cell(row=r, column=1, value=("Below the minimum in the weeks starting " + ", ".join(lows) + "."
                                        if lows else "The balance stays above the minimum in every week.")).font = f_bold
    wc.column_dimensions["A"].width = 46
    for j in range(2, 16):
        wc.column_dimensions[get_column_letter(j)].width = 11
    wc.freeze_panes = "B6"
    fit_wide(wc)
    style_sheet(wc)

    # Actuals by month -------------------------------------------------------------
    wa = wb.create_sheet("Actuals by month")
    title(wa, f"{client}: actuals by month", "As exported from QuickBooks Online (parsed lines only).")
    hdr = ["Section", "Account"] + [date(int(p[:4]), int(p[5:]), 1).strftime("%b %Y") for p in pl.periods] + ["Total"]
    for j, h in enumerate(hdr, 1):
        c = wa.cell(row=5, column=j, value=h); c.font = f_bold; c.border = Border(bottom=thin)
    rr = 6
    for _, x in pl.lines.iterrows():
        vals = [x["section"], (x["parent"] + ": " if x["parent"] else "") + x["account"]] + \
               [x[p] for p in pl.periods] + [sum(x[p] for p in pl.periods)]
        for j, v in enumerate(vals, 1):
            c = wa.cell(row=rr, column=j, value=v)
            if j > 2:
                c.number_format = money2
        rr += 1
    ni = net_income_by_period(pl.lines, pl.periods)
    vals = ["", "Net Income"] + [ni[p] for p in pl.periods] + [round(sum(ni.values()), 2)]
    for j, v in enumerate(vals, 1):
        c = wa.cell(row=rr, column=j, value=v); c.font = f_bold; c.border = Border(top=thin)
        if j > 2:
            c.number_format = money2
    wa.column_dimensions["A"].width = 18; wa.column_dimensions["B"].width = 44
    for j in range(3, len(hdr) + 1):
        wa.column_dimensions[get_column_letter(j)].width = 12
    fit_wide(wa)
    style_sheet(wa)
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


# ---------------------------------------------------------------- one-page summary

def fmt0(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return f"({abs(v):,.0f})" if v < -0.5 else f"{v:,.0f}"


def fmtp(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return f"({abs(v) * 100:.1f}%)" if v < 0 else f"{v * 100:.1f}%"


def describe_flags(x) -> list[str]:
    """Plain words for a flagged line, for example '$11,073 below budget in the month (13.3%, unfavourable)'."""
    parts = []
    for k, label in (("m", "in the month"), ("y", "year to date")):
        if not x[f"{k}_flag"]:
            continue
        v, pc = x[f"{k}_var"], x[f"{k}_pct"]
        pct_txt = "" if pc is None or pd.isna(pc) else f"{abs(pc) * 100:.1f}%, "
        parts.append(f"${abs(v):,.0f} {'above' if v > 0 else 'below'} budget {label} "
                     f"({pct_txt}{x[f'{k}_fav'].lower()})")
    return parts


def headline_rows(t):
    keys = ["Total Income", "Gross Profit", "Total Expenses", "Net Income"]
    out = []
    for k in keys:
        x = t[k]
        out.append((k.replace("Total ", ""), x["m_act"], x["m_bud"], x["m_act"] - x["m_bud"],
                    x["y_act"], x["y_bud"], x["y_act"] - x["y_bud"]))
    return out


def top_flags(df, n=6):
    f = df[df["m_flag"] | df["y_flag"]].copy()
    f["size"] = f[["m_var", "y_var"]].abs().max(axis=1)
    return f.sort_values("size", ascending=False).head(n)


def write_html(path: Path, client: str, month: str, ytd, t, df, ct):
    css = """
    @page { size: Letter; margin: 0.6in; }
    body { font-family: Georgia; color: #000; font-size: 10.5pt; line-height: 1.25; margin: 0 auto; max-width: 7.3in; padding: 16px; background: #fff; }
    h1 { font-size: 16pt; font-weight: bold; margin: 0 0 2pt 0; }
    h2 { font-size: 11.5pt; font-weight: bold; margin: 16pt 0 4pt 0; }
    .sub { margin: 0 0 4pt 0; }
    .small { font-size: 9.5pt; }
    table { border-collapse: collapse; width: 100%; font-size: 9.5pt; }
    th { text-align: right; font-weight: bold; padding: 2pt 4pt; border-bottom: 0.5pt solid #808080; }
    th:first-child, td:first-child { text-align: left; }
    td { text-align: right; padding: 2pt 4pt; }
    tr.total td { font-weight: bold; border-top: 0.5pt solid #808080; }
    ul { margin: 4pt 0 0 0; padding-left: 16pt; }
    li { margin-bottom: 3pt; }
    """
    hr = headline_rows(t)
    total_cls = ' class="total"'
    rows_html = "".join(
        f"<tr{total_cls if name == 'Net Income' else ''}><td>{html.escape(name)}</td>"
        f"<td>{fmt0(ma)}</td><td>{fmt0(mb)}</td><td>{fmt0(mv)}</td>"
        f"<td>{fmt0(ya)}</td><td>{fmt0(yb)}</td><td>{fmt0(yv)}</td></tr>"
        for name, ma, mb, mv, ya, yb, yv in hr)
    flags = top_flags(df)
    items = []
    for _, x in flags.iterrows():
        parts = describe_flags(x)
        items.append(f"<li><strong>{html.escape(x['account'])}</strong>: {'; '.join(parts)}. "
                     f"<em>[Note to draft]</em></li>")
    flags_html = "<ul>" + "".join(items) + "</ul>" if items else "<p>No lines met the flag rule this month.</p>"
    low_i = min(range(13), key=lambda i: ct["closing"][i])
    minimum = ct["minimum"]
    cash_line = (f"Bank balance at the start of the forecast: <strong>${ct['opening'][0]:,.0f}</strong>. "
                 f"Forecast balance after 13 weeks: <strong>${ct['closing'][-1]:,.0f}</strong>. "
                 f"Lowest point: ${ct['closing'][low_i]:,.0f} in the week starting {ct['weeks'][low_i]:%d %B}.")
    if minimum is not None:
        lows = [ct["weeks"][i].strftime("%d %B") for i, c in enumerate(ct["closing"]) if c < minimum]
        cash_line += (f" The owner's minimum is ${minimum:,.0f}; the forecast falls below it in the week"
                      f"{'s' if len(lows) > 1 else ''} starting {', '.join(lows)}." if lows else
                      f" The balance stays above the ${minimum:,.0f} minimum throughout.")
    cash_rows = "".join(
        f"<tr><td>{w:%d %b}</td><td>{fmt0(o)}</td><td>{fmt0(a)}</td><td>{fmt0(b)}</td><td>{fmt0(c)}</td></tr>"
        for w, o, a, b, c in zip(ct["weeks"], ct["opening"], ct["rec_total"], ct["pay_total"], ct["closing"]))
    doc = f"""<!doctype html>
<html lang="en-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(client)} {month} summary</title><style>{css}</style></head>
<body>
<h1>{html.escape(client)}</h1>
<p class="sub">Management summary for {month_name(month)}, with the year to date from {month_name(ytd[0])}</p>
<p class="small">Draft for review. Prepared with the assistance of Jayvin Consulting Inc.</p>
<h2>Results against budget (CA$)</h2>
<table><thead><tr><th></th><th>Month actual</th><th>Month budget</th><th>Variance</th>
<th>YTD actual</th><th>YTD budget</th><th>Variance</th></tr></thead><tbody>{rows_html}</tbody></table>
<p class="small">Variance is actual less budget. Figures in brackets are negative.</p>
<h2>What moved</h2>
{flags_html}
<h2>Cash</h2>
<p>{cash_line}</p>
<table><thead><tr><th>Week starting</th><th>Opening</th><th>Receipts</th><th>Payments</th><th>Closing</th></tr></thead>
<tbody>{cash_rows}</tbody></table>
</body></html>
"""
    path.write_text(doc, encoding="utf-8")


def find_georgia():
    for d in ("/usr/share/fonts", "/usr/local/share/fonts", str(Path.home() / ".fonts"),
              "/Library/Fonts", "/System/Library/Fonts/Supplemental", "C:/Windows/Fonts"):
        p = Path(d)
        if not p.exists():
            continue
        reg = next(iter(p.rglob("[Gg]eorgia.ttf")), None)
        bold = next(iter(p.rglob("[Gg]eorgia[Bb]*.ttf")), None) or next(iter(p.rglob("georgiab.ttf")), None)
        if reg:
            return reg, bold or reg
    return None, None


def write_pdf(path: Path, client: str, month: str, ytd, t, df, ct) -> str | None:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfgen import canvas
    except ImportError:
        return "reportlab is not installed, so no PDF was made (the HTML summary prints to PDF from a browser)."
    reg, bold = find_georgia()
    note = None
    if reg:
        pdfmetrics.registerFont(TTFont("Georgia", str(reg)))
        pdfmetrics.registerFont(TTFont("Georgia-Bold", str(bold)))
        F, FB = "Georgia", "Georgia-Bold"
    else:
        F, FB = "Times-Roman", "Times-Bold"
        note = ("Georgia is not installed on this machine, so the PDF uses Times. For the house-style PDF, "
                "open the HTML summary in a browser and print to PDF, or install Georgia and rerun.")
    c = canvas.Canvas(str(path), pagesize=letter)
    W, H = letter
    x0, y = 0.7 * inch, H - 0.7 * inch
    c.setFillColorRGB(0, 0, 0)
    c.setFont(FB, 16); c.drawString(x0, y, client); y -= 16
    c.setFont(F, 10.5)
    c.drawString(x0, y, f"Management summary for {month_name(month)}, with the year to date from {month_name(ytd[0])}")
    y -= 13
    c.setFont(F, 9); c.drawString(x0, y, "Draft for review. Prepared with the assistance of Jayvin Consulting Inc.")
    y -= 24
    c.setFont(FB, 11.5); c.drawString(x0, y, "Results against budget (CA$)"); y -= 15
    cols = [x0, x0 + 2.0 * inch, x0 + 2.85 * inch, x0 + 3.7 * inch, x0 + 4.55 * inch, x0 + 5.4 * inch, x0 + 6.25 * inch]
    right = [c_ + 0.8 * inch for c_ in cols]
    heads = ["", "Month actual", "Month budget", "Variance", "YTD actual", "YTD budget", "Variance"]
    c.setFont(FB, 9)
    for i, h in enumerate(heads):
        if i:
            c.drawRightString(right[i], y, h)
    c.setStrokeColorRGB(0.5, 0.5, 0.5); c.setLineWidth(0.5)
    c.line(x0, y - 3, right[-1], y - 3)  # table header rule (allowed)
    y -= 14
    for name, *vals in headline_rows(t):
        if name == "Net Income":
            c.line(x0, y + 10, right[-1], y + 10)  # total rule (allowed)
            c.setFont(FB, 9.5)
        else:
            c.setFont(F, 9.5)
        c.drawString(x0, y, name)
        for i, v in enumerate(vals, 1):
            c.drawRightString(right[i], y, fmt0(v))
        y -= 13
    c.setFont(F, 9); c.drawString(x0, y, "Variance is actual less budget. Figures in brackets are negative."); y -= 22
    c.setFont(FB, 11.5); c.drawString(x0, y, "What moved"); y -= 15
    from reportlab.lib.utils import simpleSplit
    flags = top_flags(df)
    if flags.empty:
        c.setFont(F, 10); c.drawString(x0, y, "No lines met the flag rule this month."); y -= 14
    for _, x in flags.iterrows():
        parts = describe_flags(x)
        text = f"{x['account']}: {'; '.join(parts)}. [Note to draft]"
        for k, ln in enumerate(simpleSplit(text, F, 10, right[-1] - x0 - 12)):
            c.setFont(F, 10)
            if k == 0:
                c.drawString(x0, y, "\u2022")
            c.drawString(x0 + 12, y, ln); y -= 13
        y -= 2
    y -= 10
    c.setFont(FB, 11.5); c.drawString(x0, y, "Cash"); y -= 15
    low_i = min(range(13), key=lambda i: ct["closing"][i])
    txt = (f"Bank balance at the start of the forecast: ${ct['opening'][0]:,.0f}. Forecast balance after 13 weeks: "
           f"${ct['closing'][-1]:,.0f}. Lowest point: ${ct['closing'][low_i]:,.0f} in the week starting "
           f"{ct['weeks'][low_i]:%d %B}.")
    if ct["minimum"] is not None:
        lows = [ct["weeks"][i].strftime("%d %B") for i, v in enumerate(ct["closing"]) if v < ct["minimum"]]
        txt += (f" The owner's minimum is ${ct['minimum']:,.0f}; the forecast falls below it in the week"
                f"{'s' if len(lows) > 1 else ''} starting {', '.join(lows)}." if lows else
                f" The balance stays above the ${ct['minimum']:,.0f} minimum throughout.")
    c.setFont(F, 10)
    for ln in simpleSplit(txt, F, 10, right[-1] - x0):
        c.drawString(x0, y, ln); y -= 13
    y -= 6
    ccols = [x0, x0 + 2.4 * inch, x0 + 3.6 * inch, x0 + 4.8 * inch, x0 + 6.0 * inch]
    c.setFont(FB, 9)
    c.drawString(x0, y, "Week starting")
    for i, h in enumerate(["Opening", "Receipts", "Payments", "Closing"], 1):
        c.drawRightString(ccols[i] + 0.9 * inch, y, h)
    c.line(x0, y - 3, ccols[-1] + 0.9 * inch, y - 3)
    y -= 13
    c.setFont(F, 9)
    for w, o, a, b, cl in zip(ct["weeks"], ct["opening"], ct["rec_total"], ct["pay_total"], ct["closing"]):
        c.drawString(x0, y, w.strftime("%d %b %Y"))
        for i, v in enumerate([o, a, b, cl], 1):
            c.drawRightString(ccols[i] + 0.9 * inch, y, fmt0(v))
        y -= 11.5
    c.showPage(); c.save()
    return note


# ---------------------------------------------------------------- main

def slugify(s: str) -> str:
    s = re.sub(r"\b(inc|ltd|limited|corp|corporation|incorporated)\b\.?", "", s, flags=re.I)
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build a Jayvin management pack from QuickBooks Online exports.")
    ap.add_argument("--pl", required=True, type=Path, help="QuickBooks Online P&L export, months as columns (CSV or XLSX)")
    ap.add_argument("--budget", required=True, type=Path, help="Budget CSV with columns account, month, amount")
    ap.add_argument("--cash", required=True, type=Path, help="Cash inputs CSV with columns week_start, type, line, amount")
    ap.add_argument("--client", help="Client name for titles and the file name (default: company name in the export)")
    ap.add_argument("--month", help="Reporting month YYYY-MM (default: the last month in the export)")
    ap.add_argument("--threshold-pct", type=float, default=10.0, help="Flag variances at or above this %% of budget (default 10)")
    ap.add_argument("--threshold-dollars", type=float, default=500.0, help="and at or above this many dollars (default 500)")
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent.parent / "out", help="Output folder")
    ap.add_argument("--no-pdf", action="store_true", help="Skip the PDF summary")
    a = ap.parse_args(argv)

    pl = parse_qbo_pl(a.pl)
    client = a.client or pl.company or "Client"
    month = a.month or pl.periods[-1]
    if not re.fullmatch(r"\d{4}-\d{2}", month):
        ap.error("--month must look like 2026-10")
    budget = read_budget(a.budget)
    cash = read_cash(a.cash)
    msgs = list(pl.warnings) + check_totals(a.pl, pl)
    df, ytd, w = build_summary(pl, budget, month, a.threshold_pct / 100, a.threshold_dollars)
    msgs += w
    if cash["ignored"]:
        msgs.append(f"{cash['ignored']} cash lines dated after week 13 were left out.")
    t = totals(df)
    ct = cash_table(cash)

    stem = f"{slugify(client)}-{month}"
    xlsx = a.out / f"{stem}-management-pack.xlsx"
    write_xlsx(xlsx, client, month, ytd, df, t, ct, pl, a.threshold_pct / 100, a.threshold_dollars, msgs)
    htmlp = a.out / f"{stem}-summary.html"
    write_html(htmlp, client, month, ytd, t, df, ct)
    made = [xlsx, htmlp]
    if not a.no_pdf:
        pdfp = a.out / f"{stem}-summary.pdf"
        note = write_pdf(pdfp, client, month, ytd, t, df, ct)
        if pdfp.exists():
            made.append(pdfp)
        if note:
            msgs.append(note)

    n_flags = int(df["m_flag"].sum() + df["y_flag"].sum())
    ni = t["Net Income"]
    print(f"{client}, {month}: net income {ni['m_act']:,.2f} for the month (budget {ni['m_bud']:,.2f}), "
          f"{ni['y_act']:,.2f} year to date (budget {ni['y_bud']:,.2f}). {n_flags} variance flags.")
    print(f"Cash: opening {ct['opening'][0]:,.2f}, lowest week-end {min(ct['closing']):,.2f}, "
          f"week 13 close {ct['closing'][-1]:,.2f}.")
    for m in msgs:
        print("Note:", m)
    for p in made:
        print("Wrote", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
