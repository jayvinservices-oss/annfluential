# Jayvin AI finance system: what each client needs (client setup kit, v1, 5 Nov 2026)

Use with the engagement letter (`engagement-letter-template.md`). Two ways to run a client:

| | **Jayvin-run (default)** | **Client-owned workspace** |
|---|---|---|
| Who runs the AI | Ann, on Jayvin's Claude account | The client's own team, on their Claude account |
| Client needs a Claude account? | **No** | **Yes**: Claude Team (or Enterprise) for the finance staff |
| Fits | Monthly plans (Essentials, Books to Board, Fractional CFO) | Fractional CFO + "Finance Office setup" clients who want to keep the system in-house; the original "AI Finance Operations" setup-and-handover model |
| Data | Client data stays in the client's QuickBooks; Claude reads it through the QuickBooks connector inside Jayvin's account, one Project per client | Everything stays in the client's own accounts; Ann has a seat or guest access during setup only |

Jayvin's own stack (Ann): Claude Team plan for Jayvin (separate Project per client, no client data mixed), QuickBooks Online Accountant (free, holds every client file) + ProAdvisor, the QuickBooks connector for Claude, a practice email on the domain, a password manager with client vaults, e-signature, a client portal folder per client (Google Drive or SharePoint), invoicing/payments (QuickBooks for Jayvin itself).

## 1. Systems questionnaire (client fills in before the health check)
**Organisation:** legal name, type (corporation, sole proprietor, nonprofit, registered charity), fiscal year end, HST number and filing frequency, payroll yes/no and provider, number of staff, annual revenue range, who signs cheques and approves bills.

**Accounting:** software and plan (QuickBooks Online Simple Start / Essentials / Plus / Advanced; Xero; Sage; Wave; spreadsheets), who has admin, how up to date (last reconciled month for each account), accountant/auditor and year-end type (audit, review, compilation, tax only), classes, locations or projects in use.

**Money in and out:** every bank account, credit card, loan and line of credit (bank name and last 4 digits only), payment processors (Stripe, Square, PayPal, Shopify, donation platforms such as CanadaHelps or Zeffy), point of sale, bill pay (Plooto, Wise, Bill.com), expense apps (Dext, Hubdoc, Expensify, Float, Ramp), payroll (Wagepoint, ADP, Ceridian/Dayforce, QuickBooks Payroll), CRM or donor database (Salesforce, Keela, Bloomerang).

**Documents and tools:** email and files platform (Microsoft 365 or Google Workspace), where receipts and invoices live today, e-signature, any current AI tools and the organisation's AI policy (if none, the AI Use Policy template is included in setup).

**Reporting and obligations:** who receives reports (owner, partners, investors, board, funders), report dates, budget (yes/no, format), grants and their reporting dates (IRAP, CanExport, WAGE, IRCC, FedDev Ontario, Ontario Trillium Foundation, others), restricted funds, loan covenants, upcoming deadlines (T2, T3010, HST, T4/T4A, T5018).

**Access contact:** who will grant access and answer questions each month, and how they prefer to be contacted.

## 1a. Documents the client provides, and how we verify them
**Verification documents (required before setup starts):**
- Bank, credit card and loan statements for every account: the last 3 months, plus every month being caught up for a clean-up job, plus the statement at the last fiscal year end.
- The most recent year-end financial statements: audited, review engagement or compiled (Notice to Reader), with the auditor's management letter if there is one. For organisations with none: the year-end trial balance and the last corporate tax return (T2) or charity return (T3010).
- The last filed HST return and notice of assessment, and payroll remittance statements (PD7A) if there is payroll.
- Loan and lease agreements, grant and contribution agreements, and the approved budget for the year.
- Supporting schedules where they exist: fixed assets, deferred revenue or restricted funds, accounts receivable and payable listings.

**How we verify (before we rely on any balance):**
1. Opening balances: agree the QuickBooks balances at the last year end to the year-end financial statements; list and resolve every difference before the first close.
2. Cash: agree every bank, card and loan balance to its statement at year end and at each month end since; every reconciliation is tied to a statement, never to a balance someone typed in.
3. Liabilities and assets: agree HST, payroll remittances, loans and leases to the statements and agreements; fixed assets and deferred or restricted amounts to their schedules.
4. Income: match grants and contracts to their agreements (amount, period, conditions); check that restricted money is tracked as restricted.
5. Spending: sample bills and expenses back to invoices and receipts; anything without support goes on the open-items list.
6. Report: a short verification note to the client listing what was checked, differences found and what was adjusted, with the client's sign-off before monthly work begins.
This is verification for bookkeeping and reporting, not an audit or review.

## 2. Access the client grants (never share passwords; invite or connect only)
1. **QuickBooks Online:** invite Jayvin's QuickBooks Online Accountant as "accountant user" (or a standard admin user if needed). If on another system: read-only export access, and a quote to move to QuickBooks.
2. **Bank and card feeds:** the client connects their banks inside QuickBooks themselves (Ann never holds bank logins). Statements: monthly PDF statements to the client portal folder, or read-only online banking access where the bank offers an accountant/delegate role.
3. **Payroll, payment processors, bill pay, expense apps:** accountant or read-only user invites.
4. **Documents:** a shared client portal folder (receipts, statements, contracts, grant agreements); a receipts email address forwarded to the document inbox.
5. **Claude:** nothing for Jayvin-run clients. For client-owned workspaces: the client buys Claude Team seats; Ann is added during setup, builds the Project, skills and connectors, then hands over (handover pack) and is removed at the end unless on a Care/monthly plan.

## 3. Setup steps by plan (what the implementation fee buys)
**Essentials setup ($1,500, 2 to 3 weeks)**
- Health check of the QuickBooks file; chart of accounts cleaned up (template: `templates/chart-of-accounts-small-business.csv` or `-nonprofit.csv`).
- Bank and card feeds confirmed; bank rules created; opening balances tied to statements.
- Claude Project for the client in Jayvin's account: client profile, chart of accounts, vendor list, categorisation rules, month-end checklist.
- Document inbox and receipt process; month-end calendar agreed (books closed by working day 10).

**Books to Board setup ($3,000, 3 to 4 weeks)**: Essentials setup, plus
- Management pack template built on the client's numbers (budget vs actual with notes, cash position, 13-week cash forecast).
- Budget loaded into QuickBooks; classes or projects (or restricted funds) set up.
- AI Use Policy adopted (template, questionnaire, disclosures).

**Fractional CFO setup ($5,000, 4 to 6 weeks)**: Books to Board setup, plus
- Three AI workflows built and documented (typical: bills and approvals, receipts and expenses, monthly reporting).
- Controls review (segregation of duties, approval limits, bank access), finance policies.
- 7-template handover pack completed (so the system survives staff changes).
- Client-owned workspace option: Claude Team configured for the client's finance staff, with training.

## 4. Monthly operating rhythm (what Claude does, what Ann does)
| Working day | Claude (QuickBooks connector, client Project) | Ann |
|---|---|---|
| 1 to 3 | Pull bank-feed transactions with QuickBooks' suggestions; propose a category, split, transfer or match for each; list missing receipts | Approve the proposals in batches; send one receipts request |
| 4 to 5 | Reconcile every bank, card and loan account to its statement; flag differences | Review and sign off each reconciliation |
| 6 to 8 | Close the month; draft budget vs actual with variance notes; update the 13-week cash forecast | Edit the notes; decide anything that needs judgement |
| 9 to 10 | Draft the management or board pack in house style | Review, send, take questions; log hours used against the plan |
Every posting is approved by Ann before it goes into QuickBooks. Hours beyond the plan are quoted before work starts ($150/hour).

## 5. What the client is responsible for (goes in the engagement letter)
Providing the verification documents (bank statements, last year-end financial statements and the other items in 1a) before setup; giving access and documents on time; answering open questions within 5 working days; approving payments; filing and paying their own returns and remittances; telling Jayvin about new accounts, grants or major transactions; keeping their QuickBooks subscription active.
