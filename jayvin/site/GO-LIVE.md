# Jayvin website: edit and go live on jayvinconsulting.ca (checked 7 Nov 2026)

## What is there today
- Domain jayvinconsulting.ca is registered at GoDaddy (nameservers ns27/ns28.domaincontrol.com).
- www.jayvinconsulting.ca points to the old site on **Zoho Sites**.
- The bare domain (jayvinconsulting.ca) uses GoDaddy forwarding.
- Email is **Zoho Mail** (MX records mx/mx2/mx3.zohocloud.ca, plus SPF and Zoho verification TXT records).
  **Do not touch the MX or TXT records**, or email stops working.
- jayvin.ai is not registered yet (buy it later and forward it to the main site).

## 1. Edit the template (tomorrow)
Files: this folder (`index.html`, `terms.html`, `privacy.html`, `favicon.svg`).
- Photo: save a portrait as `ann-photo.jpg` in this folder (at least 800 x 1000 px, face and shoulders, plain or
  office background). It appears in the hero and the About section; the initials "AJ" show until then.
- Name: "Ann James, MBA" in the hero and About. Search `EDIT:` in index.html for every spot to check.
- Contact: confirm the email address (currently ann@jayvinconsulting.ca) and add a booking link
  (Zoho Bookings or Google Calendar appointment page, both free).
- Before going live: delete line 3 of index.html (`<meta name="robots" content="noindex, nofollow">`) so Google
  can find the site.
Claude can make any of these changes for you: say what to change and it is done in minutes.

## 2. Host it (free): Netlify
1. Go to app.netlify.com, sign up with the Jayvin Google account.
2. "Add new site" > "Deploy manually" > drag this whole folder (or the zip `jayvin-site.zip`) onto the page.
   You get an address like jayvin-xyz.netlify.app. Check it on your phone.
3. Site settings > Domain management > Add custom domain > `www.jayvinconsulting.ca`, and also `jayvinconsulting.ca`.
   Netlify shows the exact records to set; they are normally the two below.

## 3. Point the domain (GoDaddy > My Products > jayvinconsulting.ca > DNS)
| Type | Name | Value | Note |
|---|---|---|---|
| CNAME | www | (your-site).netlify.app | replaces zhs.zohosites.ca |
| A | @ | 75.2.60.5 | Netlify's address; first turn off GoDaddy "Forwarding" for the domain |
Leave every MX and TXT record as it is. Changes take from a few minutes to a few hours.
Netlify then issues the free HTTPS certificate automatically (Domain management > HTTPS).

## 4. After it is live
- Unpublish or cancel the old Zoho Sites site (keep Zoho Mail).
- Google Business Profile and the ProAdvisor listing point to https://www.jayvinconsulting.ca.
- When jayvin.ai is bought: forward it to https://www.jayvinconsulting.ca at the registrar.
