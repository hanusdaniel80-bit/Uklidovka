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
3. **Prices.** The demo deliberately shows *how* pricing works, not amounts (Daniel's choice). His old ceník *does* have full prices (e.g. 350 Kč/h cleaning, windows from 150 Kč/pc). If he wants them shown, it's one table in `build.py`.
4. **Contradictions on the old site** that the new one had to resolve. He should confirm the chosen wording:
   - drying time "2–4 h" vs. "4–6 h" → new site: 2–4 h for upholstery/carpets, 4–6 h for cars
   - "24/7 without surcharge" vs. "+500 Kč after 18:00" vs. "24/7 only within 20 km" → new site: evenings/weekends with a surcharge agreed in advance; emergencies near HK even at night
   - travel "zones 0 / 300 / 600 Kč" vs. "10 Kč/km" → new site: "free in HK, elsewhere by km, always told in advance"
   - e-mail on firmy.cz is still UklidovkaHK@seznam.cz → update it there to info@
5. **Five reviews on the old /recenze page** (Marek L., Veronika H. …) were not used. They can't be verified and read like template text. Only the real firmy.cz reviews are on the new site.
6. **Services that were dropped as separate pages** but are mentioned inside others: car interiors and the taxi fleet offer (in *koberce*), the hotel express service (in *firmy*), house clearing (in *domácnosti*), blinds (in *okna*).

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

**Before launch:** connect the contact form to e-mail. It's a free form service (Web3Forms or Formspree) delivering to info@uklid-pospisil.cz, a ~10-minute change in `main.js`. In the demo the form only shows what would be sent. Then remove the "Návrh nového webu" ribbon (`SHOW_DRAFT_RIBBON = False` in `build.py`) and submit `sitemap.xml` in Google Search Console.

## Rebuild

```
python3 build.py            # real website into site/
python3 build.py artifact   # self-contained preview copy into dist-artifact/ (not committed)
```
