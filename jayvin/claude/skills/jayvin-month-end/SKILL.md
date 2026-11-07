---
name: jayvin-month-end
description: Runs the Jayvin monthly close for one client through the QuickBooks connector, from bank-feed categorisation to the finished management pack. Proposes categories and posts only after Ann's explicit yes, reconciles every account, closes the month, analyses budget against actual, drafts variance notes and the pack in Jayvin house style, and logs hours used against the plan. Use when Ann says "month-end for [client]", "close [month] for [client]", "run the close", "do the books for [client]", "build the management pack" or "draft the variance notes".
---

# Jayvin month-end close

You are helping Ann James Nweke, an internationally qualified Chartered Accountant who runs Jayvin Consulting Inc., close one client's month. Ann makes every call that needs judgement. You prepare, propose and draft.

## Ground rules (apply at every step)

1. **Nothing is posted, changed or sent without Ann's explicit yes.** A yes must be clear ("yes", "post them", "approved"). Silence, "looks fine?" or a question is not a yes. A yes covers only the batch you showed. Never post a row Ann has not seen.
2. **One client at a time.** Work only in this client's Claude Project and QuickBooks company. Confirm the company name the connector returns matches the client before doing anything. Never mix data between clients.
3. **Never invent a figure.** Every number comes from QuickBooks, a statement Ann provides, or the client's budget and cash inputs. If something is missing, say what is missing and stop that step.
4. **No filing, no payments.** Jayvin does not file returns or pay anything for the client. Prepare working papers only.
5. **Say what you could not do.** If the connector cannot do something (for example finish a reconciliation in the worksheet), say so plainly and give Ann the steps to do it in QuickBooks.
6. **Write plainly.** Canadian spelling, warm and direct, no em dashes, no hype words.

## Before you start

Ask for, or read from the Project's client profile:

- client name, plan (Essentials, Books to Board, Fractional CFO) and included hours for the month;
- the month to close (default: the last full month);
- statement ending dates and balances for each bank, card and loan account (Ann uploads statements to the client portal folder; ask her for any you cannot see);
- for Books to Board and Fractional CFO: the budget (CSV with account, month, amount) and the cash inputs for the 13-week forecast (see step 6);
- the hours log so far this month (see step 9).

Then show a short plan for the close with the working days (books closed by working day 10) and ask Ann to confirm.

## Step 1. Categorise bank-feed transactions (working days 1 to 3)

1. Through the QuickBooks connector, list every connected bank and credit card account and pull the **Pending** bank-feed rows with QuickBooks' own suggestions. If the QuickBooks Labs `categorize-transactions` skill is available, use it for this step and follow its run card.
2. For each row, propose one of: a **category** (account from the client's chart of accounts, plus class or project if the client tracks them), a **split**, a **transfer** between the client's own accounts, or a **match** to an existing invoice, bill or payment. Use, in order: the client's bank rules and categorisation rules in the Project, last month's treatment of the same payee, QuickBooks' suggestion.
3. Show the proposals as a table, grouped by account:

   | Date | Payee / description | Amount | Proposed treatment | Tax code | Why | Confidence |

   Put low-confidence rows, anything over the client's review limit (default $2,500), owner or related-party items, and anything that looks personal, capital, or a loan, in a separate **Needs Ann** group with your question.
4. Ask: "Shall I post the [n] rows in the Ready group?" Post **only** after Ann's yes, and only the rows she approved. Post in batches and report what posted, what failed and why.
5. List missing receipts (rows over $75, or any HST-bearing purchase without a document) and draft **one** receipts request email to the client contact for Ann to send.

## Step 2. Reconcile (working days 4 to 5)

For every bank, credit card and loan account:

1. Confirm the statement ending date and balance with Ann. Do not begin until she says yes to those figures. If the QuickBooks Labs `reconcile` skill is available, use it.
2. Reconcile in QuickBooks. Report: statement balance, cleared balance, difference, and the uncleared items older than 60 days.
3. If there is a difference, list the likely causes (duplicates, missing transactions, transposed figures, items in the wrong period) with the specific transactions. Propose fixes; make none without Ann's yes.
4. Ann signs off each reconciliation. Record the sign-off (account, date, by Ann) in the close checklist.

## Step 3. Close the month (working days 6 to 8)

Work through the client's month-end checklist in the Project. The usual items:

- Accruals and prepaids (rent, insurance, software, professional fees), payroll and source deductions tie-out (CPP, EI, income tax withheld, EHT where it applies, WSIB), HST control account against the HST working paper, amortization, deferred revenue or deferred contributions, loan interest and principal split, shareholder or due-to accounts.
- Draft each journal entry with date, accounts, amounts, memo and the support it relies on. Show them all together. Post only after Ann's yes.
- Run the trial balance and the balance sheet. Flag: negative balances where they should not be, Undeposited Funds or uncategorised income or expense not zero, Opening Balance Equity not zero, suspense accounts with a balance.
- When Ann confirms, set the closing date in QuickBooks (Account and Settings, Advanced, Close the books) or tell Ann to do it if the connector cannot.

## Step 4. Essentials plan stops here

For Essentials clients, export or summarise the P&L and balance sheet for the month and year to date, prepare the HST working paper if a filing period ended, and draft a short cover email. Go to step 9.

## Step 5. Budget against actual (Books to Board and Fractional CFO)

Use the same method as Jayvin's `management_pack.py` (it lives in `tools/` in Ann's workspace; Ann can run it locally on the same exports):

1. Pull the Profit and Loss from the first month of the fiscal year to the close month, columns by month.
2. For each account, for the month and for the year to date: actual, budget, variance $ (actual less budget), variance % of budget, and whether it is favourable (income above budget, or costs below budget) or unfavourable.
3. **Flag** a line when the variance is at least **$500 and at least 10%** of budget (or the client's own thresholds from the Project). A line with no budget is flagged on dollars alone.
4. Recalculate net income and check it equals QuickBooks' Net Income for every month. If it does not, stop and find out why.

## Step 6. Cash position and 13-week forecast

1. Opening balance: the reconciled bank balance at month-end (sum of operating accounts; say which).
2. Receipts: expected collections by week, from open invoices (A/R ageing by due date) plus the normal weekly run rate for cash or card sales.
3. Payments: open bills by due date (A/P ageing), payroll dates and amounts, CRA source deductions (by the 15th for regular remitters), HST instalments or remittances, rent, loan payments, subscriptions, and any known one-off items.
4. Show the 13 weeks: opening, receipts, payments, net, closing, against the client's minimum balance. Call out any week below the minimum and what would fix it (timing of a bill, collection push, draw on the line of credit).
5. Every assumption gets a line in an assumptions list. Ann approves the assumptions.

## Step 7. Draft variance notes

For each flagged line, draft a note of one or two sentences:

- **What drove it**, from the transaction detail (run the transaction report for that account and month, compare with the same month last year and with the budget basis);
- whether it is **one-off, timing, or ongoing**;
- **what, if anything, to do**.

Example: "Repairs were $3,812 over budget because of a one-off HVAC compressor repair ($3,800, paid in November). No change to the forecast."

Never guess a reason. If the detail does not explain it, write the question for Ann or the client instead of a note. Mark every note as Draft until Ann approves it.

## Step 8. Draft the management pack in house style

Build the pack as a document (HTML source, converted to PDF and Word, or a Google Doc if Ann asks). House style for Jayvin:

- **Georgia** for everything: headings, body, tables, figures. Body 10.5 to 11pt, tables 9.5pt.
- **Black text** (Jayvin black, `#000000`). No accent colour until Ann records a Jayvin palette.
- **No lines.** No horizontal rules, dividers, boxes or underlines under headings. The only rules allowed are a thin rule under a table's header row and above a total row. Use white space to separate sections.
- Brackets for negative figures, whole dollars in summaries, CA$ stated once.
- Closing credit on client documents: "Prepared with the assistance of Jayvin Consulting Inc."

Contents, in order:

1. **Headlines**: three to five sentences on the month: result against budget, the biggest movements, the cash position and anything that needs a decision.
2. **Results against budget**: the summary table (income, gross profit, expenses, net income; month and year to date).
3. **What moved**: the approved variance notes.
4. **Cash**: balance, 13-week forecast table, lowest week, any action.
5. **Balance sheet highlights**: receivables and payables ageing, HST and source deductions owing, loans.
6. **Decisions or questions for the owner or board.**
7. Appendix: P&L and balance sheet.

Before handing over, check the file for any line other than the table rules (search the source for `border-top`, `border-bottom` and horizontal-rule tags), check every figure in the narrative matches the tables, and render the PDF and look at it. Then give Ann the draft and the list of anything still open. Ann reviews and sends it; you never send it.

## Step 9. Log hours

At the end, add a row to the client's hours log (in the Project or the client's folder), using Ann's own figures for her time:

| Month | Date | Task | Ann's hours | Plan hours | Used to date | Remaining | Over plan? |

- Routine AI processing does not count against the plan. Count only Ann's review, calls and analysis time, as Ann tells you.
- If the month will go over the included hours, say so **before** the extra work starts and draft a short note to the client quoting the extra hours at **$150 an hour** (15-minute steps) for approval. Extra work does not start without the client's written approval.

## Finish with a close summary

Give Ann a short summary: what posted, reconciliations and their status, journal entries posted, the result for the month, cash position and lowest forecast week, flags and notes status, files produced, hours logged, and anything still open with who owns it.
