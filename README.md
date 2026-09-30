# Úklid Pospíšil: new website (demo)

A complete new website for **Michal Pospíšil – úklidové práce** (uklid-pospisil.cz), built as a demo to show him over coffee.
14 pages in Czech, all links working, phone-first, his own photos, no WordPress.

| Folder / file | What it is |
|---|---|
| `site/` | **The finished website.** These files get uploaded to the web hosting as they are. |
| `build.py` | Generates every page. All texts, services, reviews and contact details live here. Change a sentence, run `python3 build.py`, done. |
| `src/` | Design (`style.css`), small script (`main.js`), fonts (self-hosted, so no Google Fonts and no GDPR issue). |
| `site/img/` | Michal's own photos from the old site, resized and stripped of GPS/EXIF data. |
| `site/.htaccess`, `site/_redirects` | Old addresses → new pages, so Google results and old links keep working. |

## Pages

Úvod · Služby · 6 service pages (domácnosti · firmy a společné prostory · po stavbě a malování · okna a žaluzie · koberce, sedačky, matrace · havárie a škodní události) · Ceník · O nás · Reference (real reviews + before/after gallery) · Kontakt (form, WhatsApp, service-area map) · Práce u nás · Ochrana osobních údajů.

## Facts and sources (checked 30 Sep 2026)

| Fact | Value | Source |
|---|---|---|
| Business | Michal Pospíšil – úklidové práce, IČO 765 24 990 | old website /kontakt, /gdpr; business register via podnikatel.cz |
| Address | Světí 1, 503 12 Všestary | old website /gdpr |
| Phone / e-mail | 722 285 427 · info@uklid-pospisil.cz | old website (every page) |
| Datová schránka | dant4jc | old website /kontakt |
| VAT | not a VAT payer | old website /cenik-sluzeb |
| Insurance | liability insurance: yes | old website /cenik-sluzeb |
| Equipment | Kärcher, incl. Puzzi 10/1 | old website |
| Area | up to 100 km from Hradec Králové (Praha included) | old website + Daniel |
| Rating | 98.5 % from 18 ratings | firmy.cz listing |
| Reviews | 3 texts quoted word for word, with names and dates | firmy.cz listing |
| Domain | registrar Webglobe, registered 25 Sep 2025, expires 24 Sep 2027; hosting + e-mail also Webglobe | CZ.NIC RDAP, DNS |

## To confirm with Michal before going live

1. **The wife.** The site says he runs the firm with his wife (Daniel's information). The old site only says "Jmenuji se Michal". Add her name and a real photo of the two of them (there is a marked slot on the O nás page).
2. **Hero photo.** It shows two colleagues in "Pospíšilovi" T-shirts. He needs their OK to use it, which he presumably already has since it's on the old site.
3. **Prices.** The Ceník page now shows his full price list (every figure copied from his old ceník and regrouped; data lives in `PRICES` in `build.py`). He should check it once, especially: minimum order is 600 Kč on his site but 1 000 Kč on firmy.cz; the car promo ("od 2 290 Kč, běžně 3 000 Kč") is shown as a range 2 290–3 000 Kč; the "20+ matrací" price was a pre-winter promo on his site and is shown as a standing volume price.
4. **Contradictions on the old site** that the new one had to resolve. He should confirm the chosen wording:
   - drying time "2–4 h" vs. "4–6 h" → new site: 2–4 h for upholstery/carpets, 4–6 h for cars
   - "24/7 without surcharge" vs. "+500 Kč after 18:00" vs. "24/7 only within 20 km" → new site: evenings/weekends with a surcharge agreed in advance; emergencies near HK even at night
   - travel "zones 0 / 300 / 600 Kč" vs. "10 Kč/km" → new site: "free in HK, elsewhere by km, always told in advance"
   - e-mail on firmy.cz is still UklidovkaHK@seznam.cz → update it there to info@
5. **Five reviews on the old /recenze page** (Marek L., Veronika H. …) were not used. They can't be verified and read like template text. Only the real firmy.cz reviews are on the new site.
6. **Services that were dropped as separate pages** but are mentioned inside others: car interiors and the taxi fleet offer (in *koberce*), the hotel express service (in *firmy*), house clearing (in *domácnosti*), blinds (in *okna*).

## Branding

Blue palette matched to his logo (#005AAB). The logo is his header icon from the old site (bucket, broom and sparkles), used as a CSS mask so it switches colour in dark mode; it is also the favicon and the iPhone home-screen icon (`src/logo/`).
**Check:** the icon looks like it may come from an online icon library. If so, confirm the licence allows logo use (some free icons require attribution or forbid use as a logo).

## GDPR and legal checklist (not legal advice)

What the website already does:
- **Privacy notice** (`ochrana-udaju.html`): controller, what data and why, legal basis, retention, recipients, rights, ÚOOÚ. Linked from the footer, the contact form and the jobs page.
- **No cookies, no analytics, fonts self-hosted** → no cookie banner is needed. If he ever adds Google Analytics, Meta Pixel or embedded Google Maps, a consent banner becomes mandatory.
- **Business identification** required by the Civil Code (§ 435): name, IČO, registered address, trade-register note, VAT status. In the footer of every page.
- **Consumer disputes (ADR):** Česká obchodní inspekce named, as the consumer protection act requires.
- **Reviews** shown with first name + initial only.
- The form uses "beru na vědomí" (acknowledgement), not consent: correct, because answering an enquiry is pre-contract processing.

What Michal must do himself:
1. **Written consent from the colleagues in the photos** (a signed line per person is enough). This is the biggest real risk.
2. **Pick how the form sends e-mail.** Best: a small PHP mail script on his Webglobe hosting, so data stays in the EU with a processor he already has. A US form service (Formspree, Web3Forms) would need adding to the privacy notice.
3. **Fill in the "Platné od" date** in the privacy notice at launch.
4. **Delete old enquiries/CVs after one year**, as the notice promises.
5. Webglobe's terms include the data-processing agreement; no extra contract is needed for hosting and e-mail.

## Switching from the old site to the new one (the part Michal worries about)

The domain and e-mail stay exactly where they are. Only the website files change, and the old site can be put back within minutes.

**Option A: stay on Webglobe (simplest, no new accounts)**
1. In the Webglobe admin, make a full backup of the current WordPress site (files + database). This is the "undo" button.
2. Test the new site first on a sub-address, e.g. `novy.uklid-pospisil.cz` (upload the `site/` folder there).
3. When he's happy: move WordPress into a subfolder (or delete it after the backup) and upload the contents of `site/` into the web root.
4. `.htaccess` redirects the old addresses (/nase-sluzby, /cenik-sluzeb, /rychla-poptavka …) to the new pages automatically.
5. E-mail (info@) is untouched because it runs on separate mail servers (MX records).

**Option B: free static hosting (Netlify or Cloudflare Pages)**
Upload `site/`, then in Webglobe DNS change only the website record (A / CNAME). **Do not touch MX records**, so e-mail keeps working. `_redirects` handles the old addresses. Afterwards the WordPress hosting plan can be cancelled, which is a small yearly saving.

**Demo link:** the coffee demo runs on Vercel (project `uklid-pospisil-demo`). `site/vercel.json` tells search engines not to index it. Delete the Vercel project after the meeting, and remove `vercel.json` if the real site is ever hosted on Vercel.

**Before launch:** remove the "Návrh nového webu" ribbon (`SHOW_DRAFT_RIBBON = False` in `build.py`) and submit `sitemap.xml` in Google Search Console.

## Contact form (Webglobe)

The form posts to `site/poptavka.php`, which emails each enquiry to info@uklid-pospisil.cz straight from his Webglobe hosting. There's no third-party service, and data stays with Webglobe.
- **Spam protection:** a hidden trap field, a "sent faster than 3 seconds" check, and max 5 enquiries per IP per hour. Header-injection attempts are neutralised.
- **Where it works:** only on `uklid-pospisil.cz` (and its subdomains). On the demo links the form just shows a preview.
- **Tested here** end to end: PHP 8.4, both sending methods, a real browser, wrong password, spam and injection attempts.

**Setup on Webglobe (about 10 minutes):**
1. Upload the whole `site/` folder, including `poptavka.php` and `.htaccess`.
2. In the Webglobe admin, make sure the hosting runs **PHP 8.1 or newer**.
3. Recommended by Webglobe (less spam): copy `poptavka-config.example.php` to **`poptavka-config.php` one folder above the web root** (or next to `poptavka.php`; `.htaccess` blocks access to it), and fill in the password of the info@ mailbox. It then sends via `mail.webglobe.cz:465` with a login.
   Without that file it falls back to PHP `mail()`, which Webglobe allows (max 10 emails/min) but which lands in spam more often.
4. Send a test enquiry, then check the inbox **and the spam folder**. Webglobe suggests testing deliverability at mail-tester.com.
5. The domain already has SPF, DKIM (`default._domainkey`) and DMARC (`p=none`) records at Webglobe, so SMTP-sent mail should pass the checks.

Sources: [Webglobe: Odesílání e-mailu z webu](https://www.webglobe.cz/poradna/odesilani-emailu-z-webu), [Webglobe: formuláře a spam](https://www.webglobe.cz/poradna/jak-neodesilat-email-z-webovych-formularu-do-spamu).

## Rebuild

```
python3 build.py            # real website into site/
python3 build.py artifact   # self-contained preview copy into dist-artifact/ (not committed)
```
