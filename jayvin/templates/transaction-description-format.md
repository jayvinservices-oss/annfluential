# Jayvin transaction description format (all clients, from 7 Nov 2026)

Every transaction Jayvin posts gets a memo in this order, separated by " · ":

    Payee · Type · What it was · Period or event · Source

- **Payee:** the real person or company as on the receipt, not the bank code.
- **Type:** one fixed word (below), so reports and searches group cleanly.
- **What it was:** plain words a board member understands.
- **Period or event:** the month(s) or event the cost belongs to.
- **Source:** where the evidence is ("Receipt in client Drive", "PayPal receipt", "Bank statement",
  "Per [name] [date]" when the answer came from the client).

Fixed type words. Money out: Purchase, Subscription, Software, Reimbursement, Contractor fee, Salary, Contributor fee,
Artist fee, Merch purchase, Printing, Postage, Insurance, Bank fee, PayPal fee, Loan repayment, Advance, Grant spend,
Tax payment. Money in: Sale, Event income, Donation, Sponsorship, Grant, Loan received, Refund, Interest.
Between accounts: Transfer.

Examples (generic):
- Jane Doe · Reimbursement · Website hosting · May 2026 · Receipt in client Drive, per Executive Director 16 Oct 2026
- Jane Doe · Loan repayment · Repays $500 lent to the organisation on 1 Sep 2025 · May 2026 · Per Treasurer 16 Oct 2026
- Interac · Bank fee · E-transfer fee · Oct 2026 · Bank statement
- Savings to Chequing · Transfer · Move funds for payroll · Nov 2026 · Bank statement

Rules that go with it:
- Always set the Payee field too (vendor reports and T4A slips depend on it).
- Staff reimbursements go to the expense the receipt shows, never to salary or contractor fees.
- Money lent by or advanced to staff goes to a "Due to-from Staff" account (create it at setup).
- Grants name the grant and claim period.
- Auto-posting bank rules use the same memo format.
- Under about 150 characters; no account or card numbers.
