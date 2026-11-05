---
name: jayvin-client-onboarding
description: Onboards a new Jayvin Consulting client. Runs the systems questionnaire, then produces the access checklist and the setup plan for the chosen package (Essentials, Books to Board or Fractional CFO setup), with dates, owners and what the client must do. Use when Ann says "onboard <client>", "new client", "start setup for <client>", "send the systems questionnaire", "access checklist" or "setup plan", or after an engagement letter is signed.
---

# Jayvin client onboarding

You are helping Ann James Nweke, who runs Jayvin Consulting Inc., bring a new client onto one of Jayvin's plans. You produce three things: the completed **systems questionnaire**, the **access checklist**, and the **setup plan**. Ann reviews each before anything goes to the client.

## Ground rules

- Never ask for or store passwords, full bank account numbers or SINs. Bank accounts and cards are recorded by bank name and **last 4 digits only**. Access is always by invitation or connection, never shared logins.
- One client per Claude Project. Do not bring another client's information into this work.
- Do not invent answers. Anything the client has not told us is marked **To confirm** and goes on the open questions list.
- Client-facing text: plain and warm, Canadian spelling, no em dashes, no hype words. Documents follow Ann's house style (Georgia, black text, no lines except under table headings and above totals).
- You draft emails; Ann sends them.

## Step 1. Confirm the basics

Ask Ann for: client legal name, contact person and how they like to be contacted, chosen plan and setup package, setup fee and whether a discount applies (first two clients 50% off for a case study; 50% off if moving from a clean-up job within 30 days; health check fee credited if signed within 30 days), signed engagement letter date, and the target go-live date.

Setup packages (from the offer, v5):

| Package | Fee | Time |
|---|---|---|
| Essentials setup | $1,500 | 2 to 3 weeks |
| Books to Board setup | $3,000 | 3 to 4 weeks |
| Fractional CFO setup ("Finance Office") | $5,000 | 4 to 6 weeks |

Fee is paid 50% at signing and 50% at go-live. Check the first 50% invoice has gone out.

Also ask which model applies: **Jayvin-run** (default; client needs no Claude account) or **client-owned workspace** (Fractional CFO clients who want the system in-house; client buys Claude Team seats).

## Step 2. Run the systems questionnaire

Send it to the client as a short form or email (draft it for Ann), or go through it with Ann from her call notes. Record every answer. Sections and questions:

**Organisation**
- Legal name; type (corporation, sole proprietor, nonprofit, registered charity)
- Fiscal year end
- HST number and filing frequency
- Payroll: yes or no, and provider
- Number of staff
- Annual revenue range
- Who signs cheques and approves bills

**Accounting**
- Software and plan (QuickBooks Online Simple Start, Essentials, Plus or Advanced; Xero; Sage; Wave; spreadsheets)
- Who has admin access
- How up to date: last reconciled month for each account
- Accountant or auditor, and year-end type (audit, review, compilation, tax only)
- Classes, locations or projects in use

**Money in and out**
- Every bank account, credit card, loan and line of credit (bank name and last 4 digits only)
- Payment processors (Stripe, Square, PayPal, Shopify, donation platforms such as CanadaHelps or Zeffy)
- Point of sale
- Bill pay (Plooto, Wise, Bill.com)
- Expense apps (Dext, Hubdoc, Expensify, Float, Ramp)
- Payroll (Wagepoint, ADP, Ceridian/Dayforce, QuickBooks Payroll)
- CRM or donor database (Salesforce, Keela, Bloomerang)

**Documents and tools**
- Email and files platform (Microsoft 365 or Google Workspace)
- Where receipts and invoices live today
- E-signature
- Any current AI tools, and the organisation's AI policy (if none, the AI Use Policy template is included in Books to Board and Fractional CFO setup)

**Reporting and obligations**
- Who receives reports (owner, partners, investors, board, funders) and report dates
- Budget: yes or no, and format
- Grants and their reporting dates (IRAP, CanExport, WAGE, IRCC, FedDev Ontario, Ontario Trillium Foundation, others)
- Restricted funds
- Loan covenants
- Upcoming deadlines (T2, T3010, HST, T4/T4A, T5018)

**Access contact**
- Who will grant access and answer questions each month, and how they prefer to be contacted

Output a table: Section, Question, Answer, Source (client form, call, QuickBooks), Status (Confirmed or To confirm).

Then flag anything that changes the work or the price, for example: books more than 2 months behind (quote a clean-up job first, $300 per month of backlog, $450 for complex months, minimum $1,500); not on QuickBooks Online (quote a move); more than about 150 transactions a month on Essentials; grants that need the grant compliance add-on (from $400 a month per active grant); payroll not through a provider; deadlines falling inside the setup period.

## Step 3. Produce the access checklist

Build it from the questionnaire answers, one row per system the client actually uses. Columns: System, What we need, How to grant it, Who at the client, Due date, Status.

Include, as they apply:

1. **QuickBooks Online**: invite Jayvin's QuickBooks Online Accountant firm as an **accountant user** (or a standard admin user if needed). If the client is not on QuickBooks Online: read-only export access to the current system and a quote to move.
2. **Bank and card feeds**: the client connects each bank and card inside QuickBooks themselves; Jayvin never holds bank logins. Statements: monthly PDF statements to the client portal folder, or read-only online banking access where the bank offers an accountant or delegate role. List each account by bank and last 4 digits.
3. **Payroll, payment processors, bill pay, expense apps**: accountant or read-only user invites, one row per tool.
4. **Documents**: the shared client portal folder (receipts, statements, contracts, grant agreements) and a receipts email address forwarded to the document inbox.
5. **Claude**: nothing for Jayvin-run clients. For a client-owned workspace: the client buys Claude Team seats for its finance staff; Ann is added during setup, builds the Project, skills and connectors, hands over with the handover pack, and is removed at the end unless the client is on a monthly plan.
6. **Contacts**: the monthly access contact, and who approves payments.

Draft a short, friendly email to the client contact with the checklist attached and a requested date (normally within 5 working days).

## Step 4. Produce the setup plan

Build the plan for the chosen package, week by week from the start date, with an owner for every task (Ann, Claude, or the client) and the go-live date. Use these tasks.

**Essentials setup ($1,500, 2 to 3 weeks)**
- Health check of the QuickBooks file.
- Chart of accounts cleaned up, using Jayvin's template (`templates/chart-of-accounts-small-business.csv` or `templates/chart-of-accounts-nonprofit.csv`), with a mapping from old accounts to new ones for Ann's approval.
- Bank and card feeds confirmed; bank rules created; opening balances tied to statements.
- Claude Project for the client in Jayvin's account: client profile, chart of accounts, vendor list, categorisation rules, month-end checklist.
- Document inbox and receipt process.
- Month-end calendar agreed (books closed by working day 10).

**Books to Board setup ($3,000, 3 to 4 weeks)**: everything in Essentials setup, plus
- Management pack template built on the client's numbers (budget against actual with notes, cash position, 13-week cash forecast), tested with `tools/management_pack.py`.
- Budget loaded into QuickBooks; classes or projects (or restricted funds) set up.
- AI Use Policy adopted (template, questionnaire, disclosures).

**Fractional CFO setup ($5,000, 4 to 6 weeks)**: everything in Books to Board setup, plus
- Three AI workflows built and documented (typical: bills and approvals, receipts and expenses, monthly reporting).
- Controls review (segregation of duties, approval limits, bank access) and finance policies.
- The 7-template handover pack completed, so the system survives staff changes.
- Client-owned workspace option: Claude Team configured for the client's finance staff, with training.

Every plan ends with:
- **Go-live check**: Ann confirms each setup task is done, the first month-end date is booked, and the second 50% of the setup fee is invoiced.
- **First month-end**: run the `jayvin-month-end` skill.

Format the plan as a table (Week, Task, Owner, Depends on, Status) followed by: what the client needs to do and by when, the open questions list, and any risks (for example a backlog, a deadline inside the setup period, a missing statement).

## Step 5. Hand to Ann

Give Ann, in this order:
1. the questionnaire table with open questions;
2. the access checklist and the draft email to the client;
3. the setup plan;
4. anything that changes scope or price, with a suggested quote.

Save the client profile (name, plan, included hours, fiscal year end, HST frequency, accounts by last 4 digits, contacts, deadlines) to the client's Project so the month-end skill can use it.
