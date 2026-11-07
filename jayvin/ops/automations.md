# Jayvin automations (what runs on its own, and how to change it)

## 1. Website enquiries check (set up 7 Nov 2026, Ann's request)
- **What:** reads new contact-form messages from the Jayvin website on Netlify, adds each one to the Jayvin Leads
  CRM (https://claude.ai/artifact/C2QtujxqG8jfP4ZciVZnRp, stage New, source "Website form", doc id "web-<submission id>"),
  and alerts Ann.
- **Why:** Netlify's own form email alerts and webhooks need the paid Pro plan (US$20/month). This is free.
- **When:** twice a day, 7:47 am and 5:47 pm Toronto.
- **How Ann is alerted:** the run's own completion notification (phone push + email) carries the enquiry details.
  Routine "no new enquiries" runs say only that.
- **Scheduled task:** "Jayvin website enquiries check", id trig_018Lyth1wEPnsdxQUSiEN78f, starts a fresh cloud session
  each time in the Default environment.
- **Depends on:** the Netlify access token saved in the cloud environment for api.netlify.com (7 Nov 2026), and the
  Netlify project "jayvinconsulting" (site id e19ac296-be2e-484e-b1f7-c8a43d4f7d0c), form name "contact".
- **If it breaks:** the run ends with "ACTION NEEDED ... could not reach Netlify". Usually the token expired: create a
  new one (Netlify > User settings > OAuth > Personal access tokens) and ask Claude to open the secure form again.
- **To pause or change it:** ask Claude (update or disable the scheduled task), or the claude.ai routines page.
- **Never:** it does not email or reply to the person who filled in the form. Ann (or Claude, with Ann's yes)
  replies from info@ within one business day.
- **First run to watch:** 7 Nov 2026, 5:47 pm Toronto. Claude checks after the first real enquiry that the lead lands
  in the CRM correctly.
