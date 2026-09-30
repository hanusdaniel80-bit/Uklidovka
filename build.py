#!/usr/bin/env python3
"""Generates the Úklid Pospíšil website into ./site (static HTML, no dependencies).

    python3 build.py            -> ./site           (the real website, upload as-is)
    python3 build.py artifact   -> ./dist-artifact  (same pages, CSS inlined, for the private preview link)

All texts live in this file. Change a sentence, run the script again, done.
"""
import base64
import html
import json
import math
import os
import re
import shutil
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
MODE = sys.argv[1] if len(sys.argv) > 1 else "site"
OUT = os.path.join(ROOT, "site" if MODE == "site" else "dist-artifact")

# --------------------------------------------------------------------------
# Business facts. Sources are listed in README.md ("Fakta a zdroje").
# --------------------------------------------------------------------------
F = {
    "name": "Úklid Pospíšil",
    "legal": "Michal Pospíšil",
    "ico": "765 24 990",
    "datovka": "dant4jc",
    "since": "2010",
    "phone": "722 285 427",
    "phone_intl": "+420722285427",
    "email": "info@uklid-pospisil.cz",
    "street": "Světí 1",
    "zip_city": "503 12 Všestary",
    "radius": "100 km",
    "domain": "uklid-pospisil.cz",
    "firmy": "https://www.firmy.cz/detail/13697543-uklidove-sluzby-michal-pospisil-sveti.html",
    "rating": "98,5 %",
    "rating_count": "18",
}
F["address"] = f"{F['street']}, {F['zip_city']}"
WA_TEXT = "Dobrý den, posílám fotky k nacenění úklidu. Místo: "
WHATSAPP = "https://wa.me/420722285427?text=" + urllib.parse.quote(WA_TEXT)
TEL = "tel:" + F["phone_intl"]
MAILTO = "mailto:" + F["email"]

SHOW_DRAFT_RIBBON = True

# --------------------------------------------------------------------------
# Icons (24x24 line icons, drawn for this site)
# --------------------------------------------------------------------------
ICONS = {
    "home": '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M10 21v-6h4v6"/>',
    "office": '<rect x="4" y="3" width="16" height="18" rx="1.5"/><path d="M8 7h2M14 7h2M8 11h2M14 11h2M8 15h2M14 15h2"/><path d="M10 21v-3h4v3"/>',
    "roller": '<rect x="3" y="3" width="15" height="6" rx="1.5"/><path d="M18 6h2.5v5.5H11V15"/><rect x="9.5" y="15" width="3" height="6" rx="1"/>',
    "window": '<rect x="4" y="3" width="16" height="18" rx="1.5"/><path d="M12 3v18M4 12h16"/>',
    "sofa": '<path d="M4 11V8a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v3"/><path d="M2 13a2 2 0 0 1 4 0v2h12v-2a2 2 0 0 1 4 0v5H2z"/><path d="M5 18v2M19 18v2"/>',
    "drop": '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/><path d="M9.5 14.5l1.8 1.8 3.4-3.6"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "phone": '<path d="M5 4h3.5l2 5-2.4 1.5a11 11 0 0 0 5.4 5.4L15 13.5l5 2V19a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    "chat": '<path d="M20 11.5a8 8 0 0 1-11.8 7L4 20l1.5-4A8 8 0 1 1 20 11.5z"/><path d="M9 9.5c0 3 2.5 5.5 5.5 5.5l1-1.5-2-1-1 .8a4 4 0 0 1-1.8-1.8l.8-1-1-2z"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="15.5" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    "people": '<circle cx="9" cy="8" r="3.2"/><path d="M3 20c.6-3.5 3-5.5 6-5.5s5.4 2 6 5.5"/><circle cx="17" cy="9" r="2.4"/><path d="M16.5 14.6c2.4.2 4 1.9 4.5 4.6"/>',
    "shield": '<path d="M12 3l7.5 3v5.5c0 4.6-3.2 8.2-7.5 9.5-4.3-1.3-7.5-4.9-7.5-9.5V6z"/><path d="M8.8 12.2l2.2 2.2 4.3-4.4"/>',
    "route": '<circle cx="6" cy="18" r="2.2"/><circle cx="18" cy="6" r="2.2"/><path d="M8.2 18H15a3 3 0 0 0 0-6H9a3 3 0 0 1 0-6h6.8"/>',
    "handshake": '<path d="M3 12l3.5-3.5 3 1 3-2.5 4 1L21 12"/><path d="M6.5 8.5 11 14a1.6 1.6 0 0 0 2.3.1"/><path d="M9 16l1.5 1.5a1.5 1.5 0 0 0 2.1 0L17.5 13"/><path d="M3 12l3 3M21 12l-3.5 3.5"/>',
    "sparkle": '<path d="M12 3c.6 4.4 2.6 6.4 7 7-4.4.6-6.4 2.6-7 7-.6-4.4-2.6-6.4-7-7 4.4-.6 6.4-2.6 7-7z"/><path d="M19 15.5c.2 1.6.9 2.3 2.5 2.5-1.6.2-2.3.9-2.5 2.5-.2-1.6-.9-2.3-2.5-2.5 1.6-.2 2.3-.9 2.5-2.5z"/>',
    "bulb": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.6 10.8c.7.6 1.1 1.3 1.1 2.2h5c0-.9.4-1.6 1.1-2.2A6 6 0 0 0 12 3z"/>',
    "camera": '<path d="M4 8h3l1.5-2h7L17 8h3v11H4z"/><circle cx="12" cy="13.5" r="3.5"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "star": '<path d="M12 3.5l2.6 5.4 5.9.8-4.3 4.1 1 5.8L12 16.9l-5.2 2.7 1-5.8L3.5 9.7l5.9-.8z"/>',
    "user": '<circle cx="12" cy="8.5" r="3.8"/><path d="M4.5 20.5c.8-4 3.8-6.5 7.5-6.5s6.7 2.5 7.5 6.5"/>',
    "doc": '<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4M10 12h5M10 16h5"/>',
    "vacuum": '<circle cx="8" cy="18" r="2.5"/><path d="M10.5 18H18a2 2 0 0 0 2-2v-3a4 4 0 0 0-4-4h-3"/><path d="M13 9V4h-2"/><path d="M11 4 5 13"/>',
    "moon": '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
    "briefcase": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2M3 12h18"/>',
    "lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
}


def ico(name, cls="ico"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


def stars(n=5):
    s = f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICONS["star"]}</svg>'
    return f'<span class="stars" aria-label="{n} z 5 hvězd">{s * n}</span>'


CHECK_LI = "<li>" + ico("check") + "<span>{}</span></li>"

LOGO_MARK = '<span class="logo-mark" aria-hidden="true"></span>'  # Michal's own logo, coloured by CSS
LOGO_TEXT = '<span class="logo-text"><span class="logo-name">Úklid <span>Pospíšil</span></span><span class="logo-sub">Rychle a spolehlivě</span></span>'

# --------------------------------------------------------------------------
# Photos: all of them are Michal's own photos from the old website
# (people at work in "Pospíšilovi" T-shirts, the before/after job in Jaroměř).
# key: (file, alt text, fallback icon, object-position)
# --------------------------------------------------------------------------
PHOTOS = {
    # Hero: AI-generated illustration (Michal's wish), not a real employee -> labelled as such
    "hero": ("hero-ai.jpg", "Ilustrační foto: pracovník úklidové firmy v modré pracovní uniformě v čisté kuchyni", "home", "50% 35%"),
    "domacnosti": ("domacnosti.jpg", "Kolegyně vysává podlahu v bytě", "home", "50% 45%"),
    "firmy": ("firmy.jpg", "Kolegyně omývá dveře na chodbě", "office", "50% 40%"),
    "stavba": ("stavba.jpg", "Úklid nového bytu po řemeslnících, práce ze štaflí", "roller", "50% 40%"),
    "okna": ("okna.jpg", "Kolegyně myje okno na chodbě domu", "window", "50% 30%"),
    "koberce": ("koberce.jpg", "Hloubkové čištění koberce strojem Kärcher Puzzi", "sofa", "50% 50%"),
    "pojistna": ("pojistna.jpg", "Silně znečištěná podlaha před úklidem", "drop", "50% 60%"),
    "spolecne": ("spolecne-prostory.jpg", "Úklid chodby v bytovém domě", "people", "50% 45%"),
    "tricko": ("tricko.jpg", "Firemní tričko Pospíšilovi – úklidové práce", "user", "50% 30%"),
}


def photo(key, extra_cls="", eager=False, label=""):
    file, alt, icon, pos = PHOTOS[key]
    if os.path.exists(os.path.join(ROOT, "site", "img", file)):
        loading = "eager" if eager else "lazy"
        tag = f'<figcaption class="photo-label">{label}</figcaption>' if label else ""
        return (f'<figure class="photo {extra_cls}" style="margin:0">'
                f'<img src="img/{file}" alt="{html.escape(alt)}" loading="{loading}" decoding="async" style="object-position:{pos}">{tag}</figure>')
    return (f'<figure class="photo {extra_cls}" style="margin:0" role="img" aria-label="{html.escape(alt)}">'
            f'<div class="photo-ph">{ico(icon)}</div></figure>')


# Before / after — real photos from one job (panel flat, Jaroměř)
BEFORE_AFTER = [
    ("drez", "Kuchyňský dřez", "Zaschlé usazeniny a vodní kámen"),
    ("okno", "Okno a žaluzie", "Rám, klika i lamely žaluzie"),
    ("podlaha", "Podlaha v pokoji", "Zašlapaná špína u dveří"),
    ("vana", "Vana", "Rez, kámen a zbytky lepidla"),
    ("wc", "Toaleta", "Mísa i podlaha kolem"),
]


def before_after(n=None):
    items = BEFORE_AFTER if n is None else BEFORE_AFTER[:n]
    cards = []
    for key, title, note in items:
        cards.append(f"""<figure class="ba">
  <div class="ba-pics">
    <div class="ba-pic"><img src="img/pred-{key}.jpg" alt="{title} před úklidem" loading="lazy" decoding="async"><span class="ba-label ba-label--before">Před</span></div>
    <div class="ba-pic"><img src="img/po-{key}.jpg" alt="{title} po úklidu" loading="lazy" decoding="async"><span class="ba-label ba-label--after">Po</span></div>
  </div>
  <figcaption><b>{title}</b><span>{note}</span></figcaption>
</figure>""")
    return f'<div class="ba-grid">{"".join(cards)}</div>'


# --------------------------------------------------------------------------
# Services — each one has ONE page. Nothing is described twice.
# --------------------------------------------------------------------------
SERVICES = [
    {
        "slug": "uklid-domacnosti", "price_from": "od 350 Kč / hod", "price_anchor": "uklid", "key": "domacnosti", "icon": "home",
        "name": "Úklid domácností",
        "short": "Pravidelný úklid bytu či domu, generální úklid, úklid při stěhování i vyklízení.",
        "for": ["Domácnosti"],
        "lead": "Pravidelný úklid bytu nebo rodinného domu, jednorázový generální úklid, úklid při stěhování i vyklízení. Přizpůsobíme se vašemu času a tomu, na čem vám záleží nejvíc.",
        "variants": [
            ("Pravidelný úklid", "Jednou týdně, jednou za 14 dní nebo jednou měsíčně. Chodí k vám stále stejní lidé, kteří vědí, jak to u vás chodí."),
            ("Generální úklid", "Důkladný úklid celé domácnosti od podlahy po okna. Třeba na jaře, před svátky nebo před návštěvou."),
            ("Úklid při stěhování", "Před předáním bytu majiteli nebo nájemníkovi, případně před tím, než se nastěhujete vy."),
            ("Vyklízení bytů a domů", "Vyklidíme byt, dům nebo sklep a nepotřebné věci odvezeme na sběrný dvůr."),
        ],
        "checklist": [
            ("Kuchyň", ["linka, dvířka a pracovní desky", "dřez a baterie", "spotřebiče zvenku", "lednice a trouba uvnitř na přání", "podlaha"]),
            ("Koupelna a WC", ["vana, sprchový kout a obklady", "umyvadlo a WC", "zrcadla a skleněné plochy", "odstranění vodního kamene"]),
            ("Pokoje", ["utření prachu z nábytku a polic", "vysávání a vytírání podlah", "parapety, kliky a vypínače", "dveře a zárubně"]),
        ],
        "tip": ("Chcete mít jistotu, že se nic nepřehlédne?", "Při prvním úklidu s námi projděte byt a ukažte, na čem vám záleží. Domluvený postup si zapíšeme a držíme se ho při každém dalším úklidu."),
        "pricing": "Hodinovou sazbou podle rozsahu. Generální úklid a vyklízení naceníme předem, podle fotek nebo po prohlídce.",
        "faq": [
            ("Musím být při úklidu doma?", "Nemusíte. Když se domluvíme na předání klíčů, uklidíme, zatímco jste v práci."),
            ("Vezmete si vlastní prostředky a vybavení?", "Ano. Vozíme profesionální čisticí prostředky i vlastní stroje Kärcher. Když máte své oblíbené prostředky, rádi je použijeme."),
            ("Uklízíte i večer nebo o víkendu?", "Ano, přizpůsobíme se vám. Úklid večer nebo o víkendu je možný po domluvě."),
        ],
    },
    {
        "slug": "uklid-firem", "price_from": "od 370 Kč / hod", "price_anchor": "uklid", "key": "firmy", "icon": "office",
        "name": "Úklid firem a společných prostor",
        "short": "Kanceláře, ordinace, restaurace, obchody, hotely i chodby bytových domů.",
        "for": ["Firmy", "Bytové domy"],
        "lead": "Kanceláře, ordinace, restaurace, kavárny, obchody i společné prostory bytových domů. U firem a hotelů uklízíme po zavírací době, takže provoz nerušíme.",
        "variants": [
            ("Kanceláře a ordinace", "Pravidelný úklid denně, několikrát týdně nebo jednou týdně. Rozsah i časy nastavíme podle provozu."),
            ("Restaurace, kavárny, obchody", "Prodejní plocha, zázemí i toalety. Uklidíme po zavíračce, ráno můžete rovnou otevřít."),
            ("Společné prostory domů", "Schodiště, chodby, vstupy a výtahy v panelových i cihlových domech. Pravidelně podle dohody se správcem nebo výborem."),
            ("Hotely a penziony", "Expresní čištění matrací a čalounění, když je potřeba pokoj rychle znovu prodat. Po čištění schne 2 až 4 hodiny."),
        ],
        "checklist": [
            ("Pracoviště", ["stoly a pracovní plochy", "vysávání a vytírání podlah", "vynesení odpadu", "prosklené stěny a dveře"]),
            ("Kuchyňka", ["linka a dřez", "mikrovlnná trouba a lednice", "stoly a židle", "podlaha"]),
            ("Toalety", ["WC, pisoáry a umyvadla", "zrcadla a obklady", "doplnění mýdla a papíru", "dezinfekce kontaktních míst"]),
        ],
        "tip": ("Jeden kontakt, jasná dohoda", "Rozsah úklidu sepíšeme do jednoduchého přehledu. Když se ve firmě něco změní, stačí zavolat a upravíme ho."),
        "pricing": "Hodinovou sazbou podle typu provozu. Pravidelný úklid fakturujeme jednou měsíčně.",
        "faq": [
            ("Uklízíte i večer nebo o víkendu?", "Ano. Firmy, restaurace a hotely uklízíme hlavně po zavírací době, aby se nerušil provoz."),
            ("Vystavujete fakturu?", "Ano, fakturujeme firmám i OSVČ. Nejsme plátci DPH, takže cena, na které se domluvíme, je konečná."),
            ("Máte pojištění?", "Ano, máme pojištění odpovědnosti za škodu."),
        ],
    },
    {
        "slug": "uklid-po-stavbe", "price_from": "od 450 Kč / hod", "price_anchor": "uklid", "key": "stavba", "icon": "roller",
        "name": "Úklid po stavbě a malování",
        "short": "Novostavby před kolaudací, rekonstrukce, úklid po malířích a řemeslnících.",
        "for": ["Domácnosti", "Firmy"],
        "lead": "Řemeslníci odešli, ale prach zůstal všude. Odstraníme stavební prach, zbytky omítky, malty, silikonu i barvy, abyste se mohli rovnou nastěhovat.",
        "variants": [
            ("Novostavba", "Úklid domu nebo bytu před kolaudací či nastěhováním, včetně oken a odstranění ochranných fólií."),
            ("Po rekonstrukci", "Po přestavbě koupelny, kuchyně nebo celého bytu. Jemný prach najdeme i uvnitř skříní."),
            ("Po malování a řemeslnících", "Kapky barvy na podlaze a oknech, zbytky pásek a zakrývacích fólií, prach po vrtání a broušení."),
        ],
        "checklist": [
            ("Povrchy", ["stavební prach ze všech ploch", "skříně a police uvnitř i zvenku", "zárubně, dveře a lišty", "vypínače, zásuvky a radiátory"]),
            ("Okna a sklo", ["odstranění fólií a nálepek", "zbytky malty, barvy a silikonu", "rámy, těsnění a parapety", "skla bez šmouh"]),
            ("Podlahy a obklady", ["opakované vytírání proti prachu", "dlažba a obklady od spárovačky", "zbytky lepidla", "vynesení drobného odpadu"]),
        ],
        "tip": ("Kdy úklid objednat?", "Až odejde poslední řemeslník. Jemný prach se usazuje ještě den nebo dva po dokončení prací, proto doporučujeme úklid plánovat s malým odstupem."),
        "pricing": "Hodinovou sazbou podle náročnosti. Okna se zbytky malty nebo barvy myjeme dvakrát a se škrabkou, proto jsou dražší než běžná okna.",
        "faq": [
            ("Odvezete i odpad?", "Drobný odpad a obaly vyneseme. Odvoz většího množství na sběrný dvůr je potřeba domluvit předem."),
            ("Zvládnete i velký dům nebo několik bytů?", "Ano. Na větší zakázky přizveme osvědčené spolupracovníky, se kterými dlouhodobě pracujeme."),
        ],
    },
    {
        "slug": "myti-oken", "price_from": "od 150 Kč / okno", "price_anchor": "okna", "key": "okna", "icon": "window",
        "name": "Mytí oken a žaluzií",
        "short": "Okna všech druhů, výlohy a žaluzie. Rámy, parapety a kliky v ceně.",
        "for": ["Domácnosti", "Firmy"],
        "lead": "Okna všech druhů, balkonové dveře, výlohy i žaluzie. Myjeme v bytech, domech, kancelářích a prodejnách. Rámy, parapety a kliky umyjeme vždy, bez příplatku.",
        "variants": [
            ("Byty a domy", "Jednokřídlá a dvoukřídlá okna, balkonové dveře a francouzská okna, zevnitř i zvenku."),
            ("Výlohy a prodejny", "Výlohy, prosklené vstupy a kanceláře. Pravidelně nebo jednorázově."),
            ("Žaluzie", "Čištění žaluzií přímo na okně, bez demontáže."),
        ],
        "checklist": [
            ("Co je v ceně", ["skla zevnitř i zvenku", "rámy a těsnění", "vnitřní i venkovní parapety", "kliky"]),
            ("Na přání", ["žaluzie bez demontáže", "okna po stavbě se zbytky malty a barvy", "okna ve výšce nad 3 metry ze žebříku nebo lešení", "skleněné dveře a zábradlí"]),
        ],
        "tip": ("Proč nemýt okna na přímém slunci?", "Voda na horkém skle schne příliš rychle a zůstávají šmouhy. Pokud to jde, plánujeme mytí na dopoledne nebo na stinnou stranu domu."),
        "pricing": "Za kus okna podle velikosti. Rámy, parapety a kliky jsou v ceně, v Hradci Králové je doprava zdarma.",
        "faq": [
            ("Myjete i okna ve vyšších patrech?", "Ano, i nad 3 metry ze žebříku nebo z lešení. Práce ve výšce má příplatek, řekneme vám ho předem."),
        ],
    },
    {
        "slug": "cisteni-kobercu-a-calouneni", "price_from": "od 22 Kč / m²", "price_anchor": "koberce", "key": "koberce", "icon": "sofa",
        "name": "Čištění koberců, sedaček a matrací",
        "short": "Hloubkové čištění strojem Kärcher. Koberce, sedačky, matrace i interiér auta.",
        "for": ["Domácnosti", "Firmy", "Hotely"],
        "lead": "Fleky od kávy, vína, od dětí nebo mazlíčků? Koberce, sedačky, matrace i interiér auta čistíme přímo u vás profesionální extrakční metodou. Vše je suché obvykle za 2 až 4 hodiny.",
        "variants": [
            ("Koberce", "Vlněné, syntetické i zátěžové koberce a podlahové krytiny v bytech, kancelářích a hotelech. I koberce na schodech."),
            ("Sedačky a křesla", "Látkové a rohové sedací soupravy, křesla, čalouněné židle a taburety."),
            ("Matrace", "Oboustranně i s boky, s dezinfekcí. Zbaví matraci prachu, roztočů a zápachu."),
            ("Interiér auta", "Sedačky, koberce a kufr osobního auta i SUV. Pro taxislužby nabízíme pravidelné čištění na stanovišti."),
        ],
        "checklist": [
            ("Jak čistíme", ["vysátí nečistot na sucho", "nanesení čisticího roztoku a chvíle na působení", "horkovodní extrakce strojem Kärcher Puzzi", "důkladné odsátí, suché obvykle za 2 až 4 hodiny"]),
        ],
        "tip": ("Pro hotely a firmy: ukázka zdarma", "Nejste si jistí výsledkem? Jedno křeslo nebo jednu matraci vám vyčistíme na ukázku zdarma."),
        "pricing": "Koberce za m² podle znečištění, sedačky, křesla a matrace za kus, auto podle velikosti.",
        "faq": [
            ("Nezničíte mi koberec nebo sedačku?", "Ne. Používáme pH neutrální prostředky a před čištěním vždy zkontrolujeme materiál."),
            ("Dostanete pryč všechny skvrny?", "Běžné skvrny zmizí v 95 % případů. Staré a zažrané skvrny nebo barvu garantovat nemůžeme, ale vždy děláme maximum."),
            ("Kdy můžu sedačku zase používat?", "Obvykle za 2 až 4 hodiny podle materiálu a teploty v místnosti. U auta počítejte se 4 až 6 hodinami."),
        ],
    },
    {
        "slug": "uklid-po-pojistne-udalosti", "price_from": "individuálně", "price_anchor": "uklid", "key": "pojistna", "icon": "drop",
        "name": "Úklid po havárii a škodní události",
        "short": "Vytopení, rozlitá voda, silné znečištění. V okolí Hradce přijedeme i v noci.",
        "for": ["Domácnosti", "Firmy", "Hotely"],
        "lead": "Prasklá trubka, vytopený byt nebo silné znečištění, třeba krví, močí nebo zvratky. Pomůžeme s úklidem, abyste mohli co nejdřív znovu bydlet nebo pracovat.",
        "variants": [
            ("Po vytopení", "Úklid po prasklé trubce nebo zatečení od sousedů, vyčištění podlah, koberců a čalounění."),
            ("Silné znečištění", "Krev, moč, zvratky, rozlité víno. Vyčistíme, vydezinfikujeme parou a odstraníme zápach."),
            ("Po opravě škody", "Závěrečný úklid po řemeslnících, kteří škodu opravovali."),
        ],
        "checklist": [
            ("Co pro vás uděláme", ["úklid a vyčištění zasažených prostor", "čištění koberců, sedaček a matrací", "dezinfekce parou a odstranění zápachu", "doklad o provedené práci pro pojišťovnu"]),
        ],
        "tip": ("Než začnete uklízet", "Vše nafoťte a nahlaste škodu pojišťovně. Pojišťovna obvykle potřebuje vidět stav před úklidem. Pak zavolejte nám."),
        "pricing": "Individuálně podle rozsahu škody. Po prohlídce nebo podle fotek vám řekneme cenu předem.",
        "faq": [
            ("Jak rychle přijedete?", "Při havárii v okolí Hradce Králové přijedeme i v noci nebo o víkendu. Dál po domluvě."),
            ("Zaplatí úklid pojišťovna?", "To záleží na vaší pojistné smlouvě. Vystavíme doklad s popisem provedené práce, který pojišťovně předložíte."),
        ],
    },
]

# Service area — real coordinates, distances computed from Hradec Králové.
HK = (50.2092, 15.8328)
TOWNS = [
    # name, lat, lon, label position (dx, dy, anchor) or None = list only
    ("Pardubice", 50.0343, 15.7812, (10, 4, "start")),
    ("Jičín", 50.4372, 15.3517, (10, 4, "start")),
    ("Náchod", 50.4167, 16.1629, (10, 4, "start")),
    ("Trutnov", 50.5610, 15.9127, (10, 4, "start")),
    ("Rychnov n. Kn.", 50.1628, 16.2750, (10, 4, "start")),
    ("Chrudim", 49.9511, 15.7956, (10, 4, "start")),
    ("Kolín", 50.0281, 15.2006, (-10, 4, "end")),
    ("Kutná Hora", 49.9481, 15.2682, (0, 20, "middle")),
    ("Poděbrady", 50.1424, 15.1188, (0, -12, "middle")),
    ("Mladá Boleslav", 50.4113, 14.9032, (0, -12, "middle")),
    ("Liberec", 50.7671, 15.0562, (10, 4, "start")),
    ("Praha", 50.0755, 14.4378, (12, 4, "start")),
    ("Ústí n. Orl.", 49.9738, 16.3936, (10, 4, "start")),
    ("Litomyšl", 49.8681, 16.3131, (10, 4, "start")),
    ("Jaroměř", 50.3562, 15.9214, None),
    ("Dvůr Králové", 50.4318, 15.8141, None),
    ("Hořice", 50.3661, 15.6318, None),
    ("Nový Bydžov", 50.2415, 15.4908, None),
]


def km(lat, lon):
    x = (lon - HK[1]) * math.cos(math.radians(HK[0])) * 111.32
    y = (lat - HK[0]) * 110.57
    return x, y


def area_map():
    s = 2.05  # px per km
    rows = ['<svg viewBox="-235 -226 470 446" role="img" aria-label="Mapa působnosti: okruh 100 km kolem Hradce Králové, včetně Prahy">']
    rows.append(f'<circle class="map-fill" cx="0" cy="0" r="{100*s:.1f}"/>')
    for r in (25, 50, 75):
        rows.append(f'<circle class="map-ring" cx="0" cy="0" r="{r*s:.1f}"/>')
        rows.append(f'<text class="map-km" x="0" y="{-r*s-5:.1f}" text-anchor="middle">{r} km</text>')
    rows.append(f'<circle class="map-ring map-ring--outer" cx="0" cy="0" r="{100*s:.1f}"/>')
    rows.append(f'<text class="map-km map-km--outer" x="0" y="{-100*s-6:.1f}" text-anchor="middle">100 km</text>')
    for name, lat, lon, label in TOWNS:
        if not label:
            continue
        dx, dy, anchor = label
        x, y = km(lat, lon)
        px, py = x * s, -y * s
        rows.append(f'<circle class="map-dot" cx="{px:.1f}" cy="{py:.1f}" r="4"/>')
        rows.append(f'<text class="map-label" x="{px+dx:.1f}" y="{py+dy:.1f}" text-anchor="{anchor}">{name}</text>')
    rows.append('<circle class="map-home" cx="0" cy="0" r="9"/>')
    rows.append('<text class="map-home-label" x="14" y="-12">Hradec Králové</text>')
    rows.append("</svg>")
    return "".join(rows)


def town_rows():
    bands = [(0, 30, "do 30 km"), (30, 60, "30–60 km"), (60, 105, "60–100 km")]
    dist = {n: math.hypot(*km(la, lo)) for n, la, lo, _ in TOWNS}
    out = []
    for lo, hi, label in bands:
        names = [n for n, d in sorted(dist.items(), key=lambda kv: kv[1]) if lo <= d < hi]
        out.append(f'<div class="town-row"><b>{label}</b><span>{", ".join(names)}</span></div>')
    return "".join(out)


# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------
NAV = [
    ("sluzby.html", "Služby", "sluzby"),
    ("cenik.html", "Ceník", "cenik"),
    ("o-nas.html", "O nás", "onas"),
    ("reference.html", "Reference", "reference"),
    ("kontakt.html", "Kontakt", "kontakt"),
]


def fix_links(s):
    # the preview link serves the home page at "./", the real site at index.html
    return s if MODE == "site" else s.replace('href="index.html"', 'href="./"')


def header(active):
    cur = ' aria-current="page"'
    links = "".join(f'<a href="{h}"{cur if k == active else ""}>{t}</a>' for h, t, k in NAV)
    ribbon = ""
    if SHOW_DRAFT_RIBBON:
        ribbon = ('<div class="ribbon"><strong>Návrh nového webu</strong> · ukázka k odsouhlasení, '
                  'texty a údaje ještě projdeme společně</div>')
    return f"""{ribbon}
<header class="site-header">
  <div class="wrap header-row">
    <a class="logo" href="index.html" aria-label="{F['name']} – úvodní stránka">{LOGO_MARK}{LOGO_TEXT}</a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="hlavni-menu" aria-label="Menu">{ico('menu')}</button>
    <nav class="nav" id="hlavni-menu" aria-label="Hlavní menu">{links}</nav>
    <div class="header-cta">
      <a class="btn btn--ghost btn--small" href="{TEL}">{ico('phone')}<span class="nobr">{F['phone']}</span></a>
      <a class="btn btn--sun btn--small" href="kontakt.html"><span class="btn-label-long">Nezávazná poptávka</span><span class="btn-label-short">Poptávka</span></a>
    </div>
  </div>
</header>"""


def footer():
    svc = "".join(f'<li><a href="{s["slug"]}.html">{s["name"]}</a></li>' for s in SERVICES)
    return f"""
<footer class="site-footer">
  <div class="wrap">
    <div class="foot-grid">
      <div class="stack" style="gap:14px">
        <a class="logo" href="index.html">{LOGO_MARK}{LOGO_TEXT}</a>
        <p>Úklid domácností, firem a staveb, mytí oken a čištění koberců. V Hradci Králové a do {F['radius']} kolem, včetně Prahy.</p>
      </div>
      <div><h4>Služby</h4><ul>{svc}</ul></div>
      <div><h4>Firma</h4><ul>
        <li><a href="o-nas.html">O nás</a></li><li><a href="cenik.html">Ceník</a></li>
        <li><a href="reference.html">Reference</a></li><li><a href="kariera.html">Práce u nás</a></li>
        <li><a href="kontakt.html">Kontakt</a></li><li><a href="ochrana-udaju.html">Ochrana osobních údajů</a></li></ul></div>
      <div><h4>Kontakt</h4><ul>
        <li><a href="{TEL}">{F['phone']}</a></li>
        <li><a href="{MAILTO}">{F['email']}</a></li>
        <li><a href="{WHATSAPP}" target="_blank" rel="noopener">WhatsApp</a></li>
        <li>{F['address']}</li></ul></div>
    </div>
    <div class="foot-bottom">
      <span>© {F['legal']} · IČO {F['ico']} · {F['address']} · zapsán v živnostenském rejstříku · neplátce DPH</span>
      <span>{F['domain']}</span>
    </div>
  </div>
</footer>
<nav class="mobile-bar" aria-label="Rychlý kontakt">
  <a class="btn btn--ghost" href="{TEL}">{ico('phone')}Zavolat</a>
  <a class="btn btn--ghost" href="{WHATSAPP}" target="_blank" rel="noopener">{ico('chat')}WhatsApp</a>
  <a class="btn btn--sun" href="kontakt.html">Poptávka</a>
</nav>"""


LATIN = "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD"
LATIN_EXT = "U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF"


def font_css():
    """Self-hosted fonts (no Google Fonts requests = no GDPR issue). Preview mode embeds them."""
    def src(file):
        if MODE == "site":
            return f"url(fonts/{file}) format('woff2')"
        data = base64.b64encode(open(os.path.join(ROOT, "src", "fonts", file), "rb").read()).decode()
        return f"url(data:font/woff2;base64,{data}) format('woff2')"
    faces = []
    for sub, rng in (("latin-ext", LATIN_EXT), ("latin", LATIN)):
        faces.append(f"@font-face{{font-family:'Bricolage Grotesque';font-style:normal;font-display:swap;font-weight:200 800;src:{src(f'bricolage-grotesque-{sub}-wght-normal.woff2')};unicode-range:{rng}}}")
        for w in (400, 600, 700, 800):
            faces.append(f"@font-face{{font-family:'Figtree';font-style:normal;font-display:swap;font-weight:{w};src:{src(f'figtree-{sub}-{w}-normal.woff2')};unicode-range:{rng}}}")
    mask = base64.b64encode(open(os.path.join(ROOT, "src", "logo", "logo-mask.png"), "rb").read()).decode()
    faces.append(f":root{{--logo-mask:url(data:image/png;base64,{mask})}}")
    return "\n".join(faces)


def czech_typo(s):
    """Czech typography: no line break after one-letter prepositions, or between a number and its unit."""
    parts = re.split(r"(<[^>]+>)", s)
    in_raw = False
    for i, p in enumerate(parts):
        if p.startswith("<"):
            low = p.lower()
            if low.startswith("<style") or low.startswith("<script"):
                in_raw = True
            elif low.startswith("</style") or low.startswith("</script"):
                in_raw = False
            continue
        if in_raw or not p.strip():
            continue
        p = re.sub(r"(?<=[\s(>])([vkszouaiVKSZOUAI]) (?=\S)", r"\1&nbsp;", " " + p)[1:]
        p = re.sub(r"(\d) (km|m²|Kč|let|hodin|metry|%)", r"\1&nbsp;\2", p)
        parts[i] = p
    return "".join(parts)


def page(title, description, active, body, is_home=False):
    css = open(os.path.join(ROOT, "src", "style.css"), encoding="utf-8").read()
    js = open(os.path.join(ROOT, "src", "main.js"), encoding="utf-8").read()
    full_title = title if is_home else f"{title} | {F['name']}"
    if is_home and MODE != "site":
        full_title = F["name"]  # the private preview link is named after the business
    ld = ""
    if is_home:
        ld = json.dumps({
            "@context": "https://schema.org", "@type": "LocalBusiness",
            "name": F["name"], "legalName": F["legal"], "telephone": F["phone_intl"], "email": F["email"],
            "url": "https://" + F["domain"] + "/",
            "address": {"@type": "PostalAddress", "streetAddress": F["street"], "postalCode": "503 12",
                        "addressLocality": "Všestary", "addressCountry": "CZ"},
            "geo": {"@type": "GeoCoordinates", "latitude": 50.2578, "longitude": 15.7757},
            "areaServed": "Hradec Králové a okolí do 100 km, včetně Prahy",
        }, ensure_ascii=False)
        ld = f'<script type="application/ld+json">{ld}</script>'
    content = fix_links(czech_typo(header(active) + f'<main id="obsah">{body}</main>' + footer()))
    if MODE == "site":
        return f"""<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{full_title}</title>
<meta name="description" content="{html.escape(description)}">
<meta property="og:title" content="{html.escape(full_title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:image" content="https://{F['domain']}/img/hero-ai.jpg">
<meta property="og:locale" content="cs_CZ">
<meta name="theme-color" content="#005aab">
<link rel="icon" href="assets/favicon-64.png" type="image/png">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<meta name="apple-mobile-web-app-title" content="Úklid Pospíšil">
<link rel="stylesheet" href="assets/style.css">
{ld}
</head>
<body>
{content}
<script src="assets/main.js"></script>
</body>
</html>
"""
    # Preview variant: the home page is body content only (the host adds the skeleton);
    # other pages are full documents. CSS, fonts and JS inlined so every page stands alone.
    head_bits = f'<title>{full_title}</title>\n<meta name="description" content="{html.escape(description)}">\n<style>{FONT_CSS}\n{css}</style>'
    if is_home:
        return f"{head_bits}\n{content}\n<script>{js}</script>\n"
    return f"""<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{head_bits}
</head>
<body>
{content}
<script>{js}</script>
</body>
</html>
"""


# --------------------------------------------------------------------------
# Reusable blocks
# --------------------------------------------------------------------------
def service_card(s):
    return f"""<a class="card service-card" href="{s['slug']}.html">
  {photo(s['key'])}
  <div class="body">
    <span class="icon-chip">{ico(s['icon'])}</span>
    <h3>{s['name']}</h3>
    <p>{s['short']}</p>
    <span class="more">Více o službě {ico('arrow')}</span>
  </div>
</a>"""


def cta_band(title="Řekněte nám, co potřebujete uklidit",
             text="Kalkulaci připravíme zdarma a nezávazně. Nejrychleji to jde po telefonu nebo přes fotky na WhatsApp."):
    return f"""<section class="section"><div class="wrap">
  <div class="cta-band">
    <div><h2>{title}</h2><p>{text}</p></div>
    <div class="btn-row">
      <a class="btn btn--sun" href="kontakt.html">Nezávazná poptávka {ico('arrow')}</a>
      <a class="btn btn--ghost" href="{TEL}">{ico('phone')}<span class="nobr">{F['phone']}</span></a>
    </div>
  </div>
</div></section>"""


# Real reviews, copied word for word from Firmy.cz (checked 30. 9. 2026)
REVIEWS = [
    ("Doporučuji si zavolat firmu na čištění sedaček a koberců, nízké ceny, hezký přístup a rychlé jednání. Děkuji", "Marketa", "28. 8. 2026"),
    ("Excelentní provedení služeb a vynikající zákaznický servis i v, řekněme, méně obvyklé časy. Služby této úklidové firmy jistě znovu využiji.", "Tomáš J.", "12. 10. 2024"),
    ("Děkuji za skvěle provedený úklid. Výborná domluva a ochotný přístup. Mohu jen a jen doporučit.", "Ondřej V.", "12. 10. 2024"),
]


def reviews_block():
    cards = "".join(
        f'<figure class="quote">{stars()}<blockquote>{t}</blockquote><figcaption><b>{a}</b> · Firmy.cz, {d}</figcaption></figure>'
        for t, a, d in REVIEWS)
    return f'<div class="grid-3">{cards}</div>'


def rating_badge():
    return f"""<a class="rating-pill" href="{F['firmy']}" target="_blank" rel="noopener">
  {stars()}<b>{F['rating']}</b><span>spokojenost z {F['rating_count']} hodnocení na Firmy.cz</span></a>"""


def area_block():
    return f"""<div class="area">
  <div class="map-card">{area_map()}</div>
  <div class="stack" style="gap:20px">
    <span class="eyebrow">{ico('route')} Kde uklízíme</span>
    <h2>Hradec Králové a až {F['radius']} kolem</h2>
    <p class="lead">Sídlíme ve Světí u Hradce Králové. Jezdíme po celém Královéhradeckém a Pardubickém kraji, na Liberecko i do Středočeského kraje. Větší zakázky bereme i v Praze.</p>
    <div class="town-list">{town_rows()}</div>
    <p class="muted" style="font-size:1rem">V Hradci Králové je doprava zdarma. U vzdálenějších míst vám cenu dopravy řekneme předem.</p>
  </div>
</div>"""


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
def home():
    cards = "".join(service_card(s) for s in SERVICES)
    return f"""
<section class="hero">
  <div class="wrap grid-2">
    <div class="hero-text">
      <span class="eyebrow">{ico('sparkle')} Rodinná úklidová firma z Hradce Králové</span>
      <h1>Uklízíme, jako by šlo o&nbsp;náš <em>vlastní domov</em></h1>
      <p class="lead">Byty, domy, kanceláře, stavby po rekonstrukci i hloubkové čištění koberců a sedaček. Uklízíme v Hradci Králové a až {F['radius']} kolem, včetně Prahy.</p>
      <div class="btn-row">
        <a class="btn btn--sun" href="kontakt.html">Nezávazná poptávka {ico('arrow')}</a>
        <a class="btn btn--ghost" href="{TEL}">{ico('phone')}<span class="nobr">{F['phone']}</span></a>
      </div>
      <ul class="trust">
        <li>{ico('shield')} Pojištění odpovědnosti</li>
        <li>{ico('vacuum')} Vlastní stroje Kärcher</li>
        <li>{ico('route')} Do {F['radius']} od Hradce</li>
      </ul>
    </div>
    <div class="hero-media">
      {photo('hero', eager=True, label='Ilustrační foto')}
      <a class="badge-float" href="{F['firmy']}" target="_blank" rel="noopener">{stars()}<b>{F['rating']}</b><span>spokojenost · {F['rating_count']} hodnocení na Firmy.cz</span></a>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">{ico('sparkle')} Služby</span>
      <h2>S čím vám pomůžeme</h2>
      <p class="lead">Od pravidelného úklidu bytu po čištění matrací v hotelu. Každou službu můžete objednat jednorázově i pravidelně.</p>
    </div>
    <div class="grid-3">{cards}</div>
  </div>
</section>

<section class="section section--tint">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">{ico('camera')} Před a po</span>
      <h2>Tak vypadá naše práce</h2>
      <p class="lead">Skutečné fotky z jedné zakázky v Jaroměři. Byt po dlouholetém nájemníkovi, připravený k dalšímu pronájmu.</p>
    </div>
    {before_after(3)}
    <p style="margin-top:24px"><a href="reference.html#pred-a-po">Další fotky před a po {ico('arrow')}</a></p>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head section-head--center">
      <span class="eyebrow">{ico('clock')} Jak to probíhá</span>
      <h2>Od telefonátu k&nbsp;čistému domovu</h2>
    </div>
    <ol class="steps">
      <li><h3>Ozvete se</h3><p>Zavoláte, vyplníte krátkou poptávku, nebo pošlete pár fotek přes WhatsApp. Stačí popsat, co a kde je potřeba uklidit.</p></li>
      <li><h3>Domluvíme cenu a termín</h3><p>Kalkulace je zdarma a cenu znáte předem. Nejsme plátci DPH, takže je konečná.</p></li>
      <li><h3>Uklidíme a předáme</h3><p>Přijedeme ve smluvený čas s vlastními prostředky a stroji. Na konci spolu výsledek projdeme.</p></li>
    </ol>
  </div>
</section>

<section class="section section--tint">
  <div class="wrap grid-2">
    <div class="stack" style="gap:28px">
      <div class="section-head" style="margin:0">
        <span class="eyebrow">{ico('handshake')} Proč rodinná firma</span>
        <h2>Víte, kdo k vám přijde</h2>
        <p class="lead">Nejsme agentura, která pokaždé pošle někoho jiného. Jednáte přímo s majitelem a za prací stojíme osobně.</p>
      </div>
      <div class="reasons">
        <div class="reason"><span class="icon-chip">{ico('user')}</span><div><h3>Jednáte přímo s námi</h3><p>Telefon zvedá Michal, ne dispečink.</p></div></div>
        <div class="reason"><span class="icon-chip">{ico('vacuum')}</span><div><h3>Profesionální technika</h3><p>Vlastní stroje Kärcher a šetrné pH neutrální prostředky.</p></div></div>
        <div class="reason"><span class="icon-chip">{ico('doc')}</span><div><h3>Pojištění a faktura</h3><p>Máme pojištění odpovědnosti, firmám i OSVČ fakturujeme.</p></div></div>
        <div class="reason"><span class="icon-chip">{ico('moon')}</span><div><h3>Večer i o víkendu</h3><p>Přizpůsobíme se vám. Firmy uklízíme po zavíračce.</p></div></div>
      </div>
    </div>
    {photo('domacnosti')}
  </div>
</section>

<section class="section">
  <div class="wrap">{area_block()}</div>
</section>

<section class="section section--tint">
  <div class="wrap">
    <div class="section-head section-head--center">
      <span class="eyebrow">{ico('star')} Reference</span>
      <h2>Co o nás říkají zákazníci</h2>
      {rating_badge()}
    </div>
    {reviews_block()}
  </div>
</section>
{cta_band()}
"""


def sluzby():
    rows = "".join(
        f"""<tr><td><a href="{s['slug']}.html">{s['name']}</a></td><td>{s['short']}</td><td><div class="tags">{''.join(f'<span class="tag">{t}</span>' for t in s['for'])}</div></td></tr>"""
        for s in SERVICES)
    cards = "".join(service_card(s) for s in SERVICES)
    return f"""
<section class="page-hero"><div class="wrap">
  <div class="crumbs"><a href="index.html">Úvod</a> / <span>Služby</span></div>
  <h1>Úklidové služby</h1>
  <p class="lead">Uklízíme domácnosti, firmy, bytové domy i stavby a čistíme koberce, sedačky a matrace. Všechno na jednom místě, nemusíte shánět čtyři různé firmy.</p>
</div></section>
<section class="section" style="padding-top:24px"><div class="wrap">
  <div class="grid-3">{cards}</div>
</div></section>
<section class="section section--tint"><div class="wrap stack" style="gap:24px">
  <h2>Přehled na jednom místě</h2>
  <div class="table-wrap"><table>
    <thead><tr><th>Služba</th><th>Co zahrnuje</th><th>Pro koho</th></tr></thead>
    <tbody>{rows}</tbody>
  </table></div>
</div></section>
{cta_band("Nevidíte tu, co hledáte?", "Uklízíme i věci, které se do kategorií nevejdou: sklep, garáž, byt po nájemníkovi. Zavolejte a domluvíme se.")}
"""


def service_page(s):
    variants = "".join(f'<div class="variant"><h3>{t}</h3><p>{d}</p></div>' for t, d in s["variants"])
    checks = "".join(
        f'<div class="check-card"><h3>{room}</h3><ul class="checks">{"".join(CHECK_LI.format(i) for i in items)}</ul></div>'
        for room, items in s["checklist"])
    faq = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in s["faq"])
    related = "".join(
        f'<a href="{o["slug"]}.html">{ico(o["icon"])}<span>{o["name"]}</span></a>' for o in SERVICES if o is not s)
    tip_t, tip_d = s["tip"]
    return f"""
<section class="page-hero"><div class="wrap">
  <div class="grid-2">
    <div class="stack" style="gap:18px;min-width:0">
      <div class="crumbs"><a href="index.html">Úvod</a> / <a href="sluzby.html">Služby</a> / <span>{s['name']}</span></div>
      <span class="icon-chip">{ico(s['icon'])}</span>
      <h1>{s['name']}</h1>
      <p class="lead">{s['lead']}</p>
      <div class="btn-row">
        <a class="btn btn--sun" href="kontakt.html#{s['slug']}">Poptat tuto službu {ico('arrow')}</a>
        <a class="btn btn--ghost" href="{TEL}">{ico('phone')}<span class="nobr">{F['phone']}</span></a>
      </div>
    </div>
    {photo(s['key'], extra_cls='photo--tall', eager=True)}
  </div>
</div></section>

<section class="section"><div class="wrap detail-layout">
  <div class="stack">
    <div class="stack"><h2>Co pro vás můžeme udělat</h2><div class="variants{' variants--2' if len(s['variants']) == 4 else ''}">{variants}</div></div>
    <div class="stack"><h2>Co je v&nbsp;úklidu zahrnuto</h2><div class="checklist-grid">{checks}</div>
      <p class="muted" style="font-size:1rem">Rozsah vždy upravíme podle vás. Co potřebujete navíc, stačí říct předem.</p></div>
    <div class="tip">{ico('bulb')}<div><h3>{tip_t}</h3><p>{tip_d}</p></div></div>
    <div class="stack"><h2>Časté dotazy</h2><div class="faq">{faq}</div></div>
  </div>
  <aside class="side-card">
    <span class="eyebrow">Cena</span>
    <p class="price-from">{s['price_from']}</p>
    <p class="muted">{s['pricing']}</p>
    <a href="cenik.html#{s['price_anchor']}">Celý ceník {ico('arrow')}</a>
    <a class="btn btn--sun" href="kontakt.html#{s['slug']}">Chci kalkulaci zdarma</a>
    <a class="btn btn--ghost" href="{WHATSAPP}" target="_blank" rel="noopener">{ico('camera')}Poslat fotky</a>
    <p class="muted" style="font-size:.95rem">Nebo volejte <a href="{TEL}" class="nobr">{F['phone']}</a>. Když nezvedneme, jsme zrovna na zakázce a zavoláme vám zpět.</p>
  </aside>
</div></section>

<section class="section section--tint"><div class="wrap stack" style="gap:20px">
  <h2>Další služby</h2>
  <div class="related">{related}</div>
</div></section>
{cta_band()}
"""


# --------------------------------------------------------------------------
# Price list — every figure taken from Michal's old ceník (uklid-pospisil.cz/cenik-sluzeb,
# read 30. 9. 2026), regrouped. Rows: (item, price, note)
# --------------------------------------------------------------------------
PRICES = [
    ("uklid", "Úklid", "home", [
        ("Běžný úklid domácnosti", "350 Kč / hod", ""),
        ("Restaurace, kavárna, obchod", "370 Kč / hod", "cena za 1 pracovníka"),
        ("Kancelář, provozovna", "od 400 Kč / hod", ""),
        ("Úklid po řemeslnících, malování, stavbě", "od 450 Kč / hod", ""),
        ("Odstranění stavební nečistoty", "150–300 Kč / ks", "omítka, malta, silikon, barva"),
        ("Práce ve výšce nad 3 m", "+80–200 Kč / ks", "ze žebříku nebo lešení"),
        ("Generální úklid", "individuálně", "od podlahy po okna"),
        ("Úklid po havárii a škodní události", "individuálně", "podle rozsahu, po prohlídce nebo podle fotek"),
    ], ""),
    ("okna", "Mytí oken", "window", [
        ("Okno jednokřídlé", "150 Kč / ks", ""),
        ("Okno dvoukřídlé, balkonové dveře", "350 Kč / ks", ""),
        ("Francouzské okno", "450 Kč / ks", ""),
        ("Výloha do 3 m²", "400 Kč / ks", ""),
        ("Okna po stavbě", "+50 %", "malta, barva, silikon; myjeme dvakrát a se škrabkou"),
    ], "Rámy, parapety a kliky jsou v ceně."),
    ("koberce", "Koberce", "sofa", [
        ("Luxování", "10 Kč / m²", ""),
        ("Hloubkové čištění extraktorem", "22–50 Kč / m²", "podle znečištění"),
        ("Koberec na schodech", "25 Kč / schod", ""),
        ("Impregnace", "80 Kč / m²", "ochrana látky na 12 měsíců"),
    ], ""),
    ("calouneni", "Sedačky a čalounění", "sofa", [
        ("Křeslo", "400–600 Kč", ""),
        ("Sedačka dvoumístná", "650–1 000 Kč", ""),
        ("Sedačka třímístná", "900–1 500 Kč", ""),
        ("Rohová sedací souprava", "1 500–3 500 Kč", ""),
        ("Čalouněná židle", "250–350 Kč / ks", ""),
        ("Sada 4 jídelních židlí", "600–900 Kč", ""),
        ("Rozkládací gauč s úložným prostorem", "+250 Kč", ""),
    ], "Čistíme extraktorem Kärcher Puzzi. Suché obvykle za 2 až 4 hodiny."),
    ("auto", "Interiér auta", "route", [
        ("Malé auto", "2 290–3 000 Kč", "2 sedačky, zadní lavice, koberce"),
        ("SUV, kombi", "3 200–4 000 Kč", "vše včetně kufru"),
        ("Taxi a firemní flotily", "990 Kč / týden", "pravidelné udržovací čištění na stanovišti, první čištění o 20 % levněji"),
    ], "Suché obvykle za 4 až 6 hodin podle počasí. V Hradci Králové doprava zdarma."),
    ("doplnky", "Doplňkové služby a příplatky", "sparkle", [
        ("Domácí mazlíček", "+300 Kč", "chlupy a dezinfekce; u auta +500 Kč"),
        ("Extrémní znečištění", "+30 %", "krev, víno, mastnota"),
        ("Odstranění zápachu", "+400 Kč", "kouř, zvířata, zvratky"),
        ("Dezinfekce parou", "+300 Kč", ""),
    ], ""),
    ("doprava", "Čas a doprava", "clock", [
        ("Pracovní den 18–22 h", "+500 Kč", "mimo Hradec Králové +1 000 Kč"),
        ("Víkend a svátek", "+30 %", ""),
        ("Po 22. hodině", "po domluvě", ""),
        ("Doprava v Hradci Králové", "zdarma", ""),
        ("Doprava mimo Hradec Králové", "10 Kč / km", ""),
        ("Minimální cena zakázky", "600 Kč", ""),
    ], "Platí pro domácnosti. Pro hotely a firmy platí podmínky expresního výjezdu níže."),
]
MATTRESSES = [("90 × 200", "600", "500", "350"), ("140 × 200", "750", "600", "550"), ("160 × 200", "900", "700", "650"),
              ("180 × 200", "1 000", "800", "750"), ("200 × 200", "1 100", "900", "850")]
ZONES = [("Zóna 1", "do 30 km", "Hradec Králové, Pardubice, Chrudim", "do 90 min", "bez příplatku"),
         ("Zóna 2", "30–60 km", "Jičín, Náchod, Dvůr Králové", "do 180 min", "+300 Kč"),
         ("Zóna 3", "60–100 km", "Poděbrady, Litomyšl", "do 240 min", "+600 Kč")]


WIDE_PRICE_CARDS = {"doprava"}


def price_card(key, title, icon, rows, note):
    items = "".join(
        f'<div class="price-row"><div class="pr-name">{n}{f"<small>{d}</small>" if d else ""}</div><div class="pr-price">{pr}</div></div>'
        for n, pr, d in rows)
    foot = f'<p class="price-note">{note}</p>' if note else ""
    wide = " price-card--wide price-card--cols" if key in WIDE_PRICE_CARDS else ""
    return f'<section class="price-card{wide}" id="{key}"><h3>{ico(icon)}{title}</h3><div class="price-rows">{items}</div>{foot}</section>'


def cenik():
    chips = [(k, t) for k, t, *_ in PRICES]
    chips.insert(6, ("matrace", "Matrace"))
    chips.append(("hotely", "Hotely a firmy"))
    nav = "".join(f'<a href="#{k}">{t}</a>' for k, t in chips)
    cards = [price_card(*p) for p in PRICES]
    mat_rows = "".join(f"<tr><th scope=\"row\">{a}</th><td>{b} Kč</td><td>{c} Kč</td><td>{d} Kč</td></tr>" for a, b, c, d in MATTRESSES)
    mattress = f"""<section class="price-card price-card--wide" id="matrace"><h3>{ico('sofa')}Matrace</h3>
  <div class="table-wrap table-wrap--plain"><table class="price-table">
    <thead><tr><th>Rozměr (cm)</th><th>Domácnost</th><th>Hotel 5–19 ks</th><th>Hotel 20 a více ks</th></tr></thead>
    <tbody>{mat_rows}</tbody></table></div>
  <p class="price-note">Cena za kus. Čistíme obě strany i boky, s dezinfekcí Sanytol, suché do 2 hodin. Minimální zakázka pro domácnosti 600 Kč. Hotely mají nižší cenu, protože čistíme mnoho matrací na jednom místě.</p>
</section>"""
    cards.insert(6, mattress)
    zone_rows = "".join(f"<tr><th scope=\"row\">{z}<small>{km}</small></th><td>{ex}</td><td>{t}</td><td>{fee}</td></tr>" for z, km, ex, t, fee in ZONES)
    hotels = f"""<section class="price-card price-card--wide price-card--accent" id="hotely"><h3>{ico('moon')}Hotely a firmy: expresní výjezd nonstop</h3>
  <p class="muted">Krev, moč, zvratky, rozlité víno, voda nebo zápach. Přijedeme rychle, vyčistíme matrace i čalounění a pokoj můžete znovu prodat. Schnutí 2 až 4 hodiny.</p>
  <div class="table-wrap table-wrap--plain"><table class="price-table">
    <thead><tr><th>Vzdálenost od HK</th><th>Například</th><th>Příjezd</th><th>Příplatek</th></tr></thead>
    <tbody>{zone_rows}</tbody></table></div>
  <ul class="checks" style="margin-top:14px">
    {CHECK_LI.format('nonstop včetně nocí, víkendů a svátků bez příplatku')}
    {CHECK_LI.format('minimální fakturace výjezdu 1 800 Kč')}
    {CHECK_LI.format('jedno křeslo nebo jednu matraci vyčistíme na ukázku zdarma')}
  </ul>
</section>"""
    return f"""
<section class="page-hero"><div class="wrap">
  <div class="crumbs"><a href="index.html">Úvod</a> / <span>Ceník</span></div>
  <h1>Ceník</h1>
  <p class="lead">Ceny jsou konečné, nejsme plátci DPH. U rozpětí záleží na velikosti a míře znečištění, přesnou cenu vám řekneme předem. Kalkulace je zdarma.</p>
  <nav class="chips" aria-label="Části ceníku">{nav}</nav>
</div></section>

<section class="section" style="padding-top:28px"><div class="wrap">
  <div class="price-grid">{''.join(cards)}{hotels}</div>
</div></section>

<section class="section section--tint"><div class="wrap grid-2" style="align-items:start">
  <div class="stack" style="gap:20px">
    <h2>Dobré vědět</h2>
    <div class="check-card"><ul class="checks">
      <li>{ico('check')}<span><b>Nejsme plátci DPH.</b> Uvedené ceny jsou konečné.</span></li>
      <li>{ico('check')}<span><b>Cena se odvíjí</b> od míry znečištění a přístupnosti. Vždy ji znáte předem.</span></li>
      <li>{ico('check')}<span><b>Máme pojištění odpovědnosti</b> za případné škody.</span></li>
      <li>{ico('check')}<span><b>Fakturujeme</b> firmám i OSVČ, u firem i na základě smlouvy.</span></li>
      <li>{ico('check')}<span><b>Vlastní technika a chemie:</b> profesionální stroje a prostředky Kärcher.</span></li>
    </ul></div>
  </div>
  <div class="side-card">
    <span class="eyebrow">{ico('camera')} Nejrychlejší cesta k ceně</span>
    <h3 style="font-size:1.5rem">Pošlete fotky přes WhatsApp</h3>
    <p class="muted">Nafoťte, co potřebujete uklidit nebo vyčistit, a připište obec a přibližnou velikost. Podle fotek vám obvykle řekneme přesnou cenu bez nutnosti prohlídky.</p>
    <a class="btn btn--sun" href="{WHATSAPP}" target="_blank" rel="noopener">{ico('chat')}Poslat fotky na WhatsApp</a>
    <p class="muted" style="font-size:.95rem">Číslo pro WhatsApp i volání: <b class="nobr">{F['phone']}</b></p>
  </div>
</div></section>
{cta_band("Chcete přesnou cenu?", "Zavolejte nebo vyplňte krátkou poptávku. Na poptávky odpovídáme co nejdřív, obvykle do hodiny.")}
"""


def onas():
    return f"""
<section class="page-hero"><div class="wrap">
  <div class="crumbs"><a href="index.html">Úvod</a> / <span>O nás</span></div>
  <h1>Malá rodinná firma, která za svou prací stojí</h1>
</div></section>

<section class="section" style="padding-top:24px"><div class="wrap grid-2" style="align-items:start">
  <div class="prose">
    <p class="lead" style="color:var(--ink)">Jmenuji se Michal Pospíšil a úklidu se věnuji profesionálně. Firmu vedu společně s manželkou, sami telefonujeme, sami jezdíme na zakázky a sami ručíme za výsledek.</p>
    <p>Uklízíme byty, domy, kanceláře, ordinace, kavárny, hotely i chodby bytových domů. Čistíme koberce, sedačky a matrace. Ať potřebujete cokoli od matrace po výlohu, nemusíte shánět čtyři různé firmy.</p>
    <p>Na velké zakázky přizveme osvědčené spolupracovníky, se kterými dlouhodobě pracujeme. Poznáte je podle našich triček s nápisem Pospíšilovi. Za jejich práci ručíme stejně jako za vlastní.</p>
    <p>Na každé zakázce nám záleží, jako by byla u nás doma. Proto nabízíme férové ceny, jasnou domluvu a práci bez výmluv.</p>
  </div>
  <div class="owner-slot">
    <div class="inner">{ico('camera')}
      <h3>Tady bude vaše společná fotka</h3>
      <p class="muted" style="font-size:1rem">Skutečná fotka Michala s manželkou, třeba u firemního auta. Pro rodinnou firmu je to nejsilnější prvek celého webu.</p>
    </div>
  </div>
</div></section>

<section class="section section--tint"><div class="wrap">
  <div class="section-head"><h2>Na čem si zakládáme</h2></div>
  <div class="reasons">
    <div class="reason"><span class="icon-chip">{ico('clock')}</span><div><h3>Spolehlivost</h3><p>Přijedeme, kdy jsme slíbili. Když se něco změní, ozveme se včas.</p></div></div>
    <div class="reason"><span class="icon-chip">{ico('sparkle')}</span><div><h3>Pečlivost</h3><p>Uklízíme i tam, kam se běžně nekouká: za dveřmi, na lištách, pod linkou.</p></div></div>
    <div class="reason"><span class="icon-chip">{ico('shield')}</span><div><h3>Diskrétnost</h3><p>Chováme se u vás jako hosté. Co uvidíme, zůstane mezi námi.</p></div></div>
    <div class="reason"><span class="icon-chip">{ico('handshake')}</span><div><h3>Férové jednání</h3><p>Cenu znáte předem, bez skrytých poplatků.</p></div></div>
  </div>
</div></section>

<section class="section"><div class="wrap grid-2" style="align-items:start">
  <div class="stack" style="gap:18px">
    <h2>Základní údaje</h2>
    <dl class="facts">
      <div><dt>Podnikatel</dt><dd>{F['legal']} – úklidové práce</dd></div>
      <div><dt>IČO</dt><dd>{F['ico']}</dd></div>
      <div><dt>Sídlo</dt><dd>{F['address']}</dd></div>
      <div><dt>Datová schránka</dt><dd>{F['datovka']}</dd></div>
      <div><dt>DPH</dt><dd>nejsme plátci DPH</dd></div>
      <div><dt>Pojištění</dt><dd>pojištění odpovědnosti za škodu</dd></div>
      <div><dt>Technika</dt><dd>vlastní stroje Kärcher, mimo jiné Puzzi 10/1</dd></div>
      <div><dt>Působnost</dt><dd>do {F['radius']} od Hradce Králové, včetně Prahy</dd></div>
    </dl>
  </div>
  {photo('spolecne')}
</div></section>
{cta_band()}
"""


def reference():
    their = ["Domácnosti", "Hotely a penziony", "Kanceláře", "Ordinace", "Restaurace a kavárny", "Obchody", "Bytové domy", "Stavebníci a majitelé bytů"]
    tags = "".join(f'<span class="tag tag--big">{t}</span>' for t in their)
    return f"""
<section class="page-hero"><div class="wrap">
  <div class="crumbs"><a href="index.html">Úvod</a> / <span>Reference</span></div>
  <h1>Reference a hodnocení</h1>
  <p class="lead">Co o nás píšou zákazníci a jak vypadá naše práce. Všechny fotky jsou naše vlastní, z opravdových zakázek.</p>
  {rating_badge()}
</div></section>

<section class="section" style="padding-top:24px"><div class="wrap stack" style="gap:28px">
  {reviews_block()}
  <div class="tip" style="background:var(--surface);border-color:var(--line)">{ico('star')}<div>
    <h3>Všechna hodnocení najdete na Firmy.cz</h3>
    <p class="muted">Hodnocení píší zákazníci sami a nemůžeme je upravovat. Pokud jste s námi byli spokojení, budeme rádi za pár slov.</p>
    <p style="margin-top:6px"><a href="{F['firmy']}" target="_blank" rel="noopener">Otevřít hodnocení na Firmy.cz {ico('arrow')}</a></p>
  </div></div>
</div></section>

<section class="section section--tint" id="pred-a-po"><div class="wrap">
  <div class="section-head">
    <span class="eyebrow">{ico('camera')} Před a po</span>
    <h2>Byt v&nbsp;Jaroměři</h2>
    <p class="lead">Byt po dlouholetém nájemníkovi. Uklidili jsme kuchyň, koupelnu, okna i podlahy, aby se dal znovu pronajmout.</p>
  </div>
  {before_after()}
</div></section>

<section class="section"><div class="wrap stack" style="gap:20px">
  <h2>Pro koho uklízíme</h2>
  <div class="tags">{tags}</div>
</div></section>
{cta_band()}
"""


def kontakt():
    opts = "".join(f'<option value="{s["slug"]}">{s["name"]}</option>' for s in SERVICES)
    return f"""
<section class="page-hero"><div class="wrap">
  <div class="crumbs"><a href="index.html">Úvod</a> / <span>Kontakt</span></div>
  <h1>Kontakt a poptávka</h1>
  <p class="lead">Zavolejte, napište nebo vyplňte krátkou poptávku. Odpovídáme co nejdřív, obvykle do hodiny.</p>
</div></section>

<section class="section" style="padding-top:24px"><div class="wrap contact-grid">
  <div class="stack" style="gap:6px">
    <div class="contact-line"><span class="icon-chip">{ico('phone')}</span><div><small>Telefon (i WhatsApp)</small>
      <a href="{TEL}" id="c-phone">{F['phone']}</a><button class="copy-btn" type="button" data-copy="{F['phone']}" aria-controls="c-phone">Kopírovat</button></div></div>
    <div class="contact-line"><span class="icon-chip">{ico('mail')}</span><div><small>E-mail</small>
      <a href="{MAILTO}" id="c-mail">{F['email']}</a><button class="copy-btn" type="button" data-copy="{F['email']}" aria-controls="c-mail">Kopírovat</button></div></div>
    <div class="contact-line"><span class="icon-chip">{ico('chat')}</span><div><small>Fotky k nacenění</small>
      <a href="{WHATSAPP}" target="_blank" rel="noopener">Napsat na WhatsApp</a></div></div>
    <div class="contact-line"><span class="icon-chip">{ico('pin')}</span><div><small>Sídlo</small>
      <span class="val">{F['address']}</span></div></div>
    <div class="contact-line"><span class="icon-chip">{ico('moon')}</span><div><small>Kdy pracujeme</small>
      <span class="val">i večer a o víkendech</span></div></div>
    <p class="muted" style="font-size:1rem;margin-top:14px">Při havárii v okolí Hradce Králové přijedeme i v noci. Když nezvedneme telefon, jsme nejspíš na zakázce. Zavoláme vám zpět, jakmile to půjde.</p>
    <dl class="facts" style="margin-top:14px">
      <div><dt>Podnikatel</dt><dd>{F['legal']}</dd></div>
      <div><dt>IČO</dt><dd>{F['ico']}</dd></div>
      <div><dt>Datová schránka</dt><dd>{F['datovka']}</dd></div>
    </dl>
  </div>

  <div>
    <form class="form" id="poptavka" action="poptavka.php" method="post" accept-charset="UTF-8" novalidate>
      <div class="stack" style="gap:6px"><h2 style="font-size:1.7rem">Nezávazná poptávka</h2>
        <p class="muted" style="font-size:1rem">Vyplnění zabere asi minutu. Pole s hvězdičkou jsou povinná.</p></div>
      <div class="form-row">
        <div class="field"><label for="f-jmeno">Jméno *</label><input id="f-jmeno" name="jmeno" autocomplete="name" maxlength="100" required></div>
        <div class="field"><label for="f-telefon">Telefon *</label><input id="f-telefon" name="telefon" type="tel" autocomplete="tel" maxlength="30" required></div>
      </div>
      <div class="form-row">
        <div class="field"><label for="f-email">E-mail <span class="opt">(nepovinné)</span></label><input id="f-email" name="email" type="email" autocomplete="email" maxlength="120"></div>
        <div class="field"><label for="f-sluzba">Služba *</label><select id="f-sluzba" name="sluzba" required><option value="">Vyberte…</option>{opts}<option value="jine">Něco jiného</option></select></div>
      </div>
      <div class="form-row">
        <div class="field"><label for="f-misto">Obec, kde se uklízí *</label><input id="f-misto" name="misto" maxlength="100" required placeholder="např. Hradec Králové"></div>
        <div class="field"><label for="f-termin">Kdy by se vám hodilo <span class="opt">(nepovinné)</span></label><input id="f-termin" name="termin" maxlength="100" placeholder="např. příští týden"></div>
      </div>
      <div class="field"><label for="f-zprava">Co potřebujete uklidit *</label><textarea id="f-zprava" name="zprava" maxlength="3000" required placeholder="např. byt 3+1 po malování, asi 75 m², včetně oken"></textarea></div>
      <label class="check-field" for="f-souhlas"><input id="f-souhlas" type="checkbox" name="souhlas" required><span>Beru na vědomí, že mé údaje zpracujete kvůli vyřízení poptávky. Více v&nbsp;<a href="ochrana-udaju.html">zásadách ochrany osobních údajů</a>.</span></label>
      <div class="hp" aria-hidden="true"><label for="f-web">Nevyplňujte</label><input id="f-web" name="web" tabindex="-1" autocomplete="off"></div>
      <input type="hidden" name="t" id="f-t" value="">
      <button class="btn btn--sun" type="submit" id="poptavka-submit">Odeslat poptávku {ico('arrow')}</button>
      <p class="form-error" id="poptavka-error" role="alert" hidden>Poptávku se nepodařilo odeslat. Zkuste to prosím znovu, nebo nám rovnou zavolejte na <a href="{TEL}" class="nobr">{F['phone']}</a>.</p>
    </form>
    <div class="form-done" id="poptavka-sent" hidden role="status">
      <h3>Děkujeme, poptávka je odeslaná</h3>
      <p>Ozveme se vám co nejdřív, obvykle do hodiny. Pokud spěcháte, zavolejte na <a href="{TEL}" class="nobr">{F['phone']}</a>.</p>
    </div>
    <div class="form-done" id="poptavka-done" hidden>
      <h3>Děkujeme, poptávka je připravená</h3>
      <p class="muted">Tohle je ukázka, nic se neodeslalo. Na webu uklid-pospisil.cz přijde tato zpráva e-mailem na {F['email']}:</p>
      <pre></pre>
      <button class="btn btn--ghost btn--small" type="button" id="poptavka-again">Upravit poptávku</button>
    </div>
  </div>
</div></section>

<section class="section section--tint"><div class="wrap">{area_block()}</div></section>
"""


def dekujeme():
    return f"""
<section class="page-hero"><div class="wrap" style="padding-block:clamp(56px,9vw,110px)">
  <span class="eyebrow">{ico('check')} Poptávka odeslána</span>
  <h1>Děkujeme, ozveme se vám</h1>
  <p class="lead">Poptávku jsme přijali. Ozveme se co nejdřív, obvykle do hodiny. Pokud spěcháte, zavolejte na <a href="{TEL}" class="nobr">{F['phone']}</a>.</p>
  <div class="btn-row"><a class="btn btn--sun" href="index.html">Zpět na úvod</a><a class="btn btn--ghost" href="sluzby.html">Naše služby</a></div>
</div></section>
"""


PHP_TEMPLATE = r'''<?php
/**
 * Poptávkový formulář -> e-mail do schránky firmy.
 * Běží na běžném webhostingu s PHP (Webglobe). Nic neukládá do databáze,
 * data neodcházejí k žádné třetí straně. Generováno z build.py.
 */
declare(strict_types=1);
date_default_timezone_set('Europe/Prague');

const TO_EMAIL   = '__EMAIL__';        // kam poptávky chodí
const FROM_EMAIL = '__EMAIL__';        // odesílatel: existující schránka na vlastní doméně
const SITE_NAME  = 'Úklid Pospíšil';
const THANKS_URL = 'dekujeme.html';
const MAX_PER_HOUR = 5;                // ochrana proti spamu: max. poptávek z jedné IP za hodinu

// Přihlášení do schránky pro odesílání přes SMTP (doporučuje Webglobe, méně spamu).
// Heslo NEPATŘÍ sem ani do gitu: zkopírujte poptavka-config.example.php jako
// poptavka-config.php (ideálně o složku výš, mimo web) a vyplňte ho tam.
// Bez konfigurace se použije PHP mail().
foreach ([__DIR__ . '/../poptavka-config.php', __DIR__ . '/poptavka-config.php'] as $cfg) {
    if (is_file($cfg)) { require $cfg; break; }
}

$SERVICES = __SERVICES__;

$wantsJson = str_contains($_SERVER['HTTP_ACCEPT'] ?? '', 'application/json');

function finish(bool $ok, string $msg, bool $json, int $code = 200): never {
    if ($json) {
        http_response_code($code);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode(['ok' => $ok, 'message' => $msg], JSON_UNESCAPED_UNICODE);
    } elseif ($ok) {
        header('Location: ' . THANKS_URL, true, 303);
    } else {
        http_response_code($code);
        header('Content-Type: text/html; charset=utf-8');
        echo '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
           . '<p style="font:18px system-ui;max-width:40em;margin:3em auto;padding:0 1em">'
           . htmlspecialchars($msg) . '<br><br><a href="kontakt.html">Zpět na formulář</a></p>';
    }
    exit;
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Location: kontakt.html', true, 303);
    exit;
}

// Hodnoty z formuláře: ořezat, omezit délku, odstranit řídicí znaky
function field(string $name, int $max, bool $oneLine = true): string {
    $v = trim((string)($_POST[$name] ?? ''));
    $v = $oneLine ? preg_replace('/[\r\n\t]+/', ' ', $v) : preg_replace('/\r\n?/', "\n", $v);
    $v = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', (string)$v);
    return mb_substr((string)$v, 0, $max);
}

// 1) Past na roboty: skryté pole musí zůstat prázdné, formulář nesmí být odeslán okamžitě
$sentAt = (int)($_POST['t'] ?? 0);
if (field('web', 200) !== '' || ($sentAt > 0 && time() - $sentAt < 3)) {
    finish(true, 'OK', $wantsJson);   // robotovi tváříme, že prošel
}

// 2) Limit na IP adresu (ukládá se jen otisk IP na 1 hodinu)
$bucket = sys_get_temp_dir() . '/poptavka_' . hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? '') . __FILE__);
$hits = array_filter(array_map('intval', @file($bucket, FILE_IGNORE_NEW_LINES) ?: []), fn($t) => $t > time() - 3600);
if (count($hits) >= MAX_PER_HOUR) {
    finish(false, 'Odeslali jste už několik poptávek. Zkuste to prosím později, nebo zavolejte.', $wantsJson, 429);
}

// 3) Kontrola povinných polí
$d = [
    'jmeno'   => field('jmeno', 100),
    'telefon' => field('telefon', 30),
    'email'   => field('email', 120),
    'sluzba'  => field('sluzba', 60),
    'misto'   => field('misto', 100),
    'termin'  => field('termin', 100),
    'zprava'  => field('zprava', 3000, false),
];
if ($d['jmeno'] === '' || $d['telefon'] === '' || $d['misto'] === '' || $d['zprava'] === '' || empty($_POST['souhlas'])) {
    finish(false, 'Vyplňte prosím všechna povinná pole.', $wantsJson, 422);
}
if (!preg_match('/^[0-9+ ()\/-]{6,30}$/', $d['telefon'])) {
    finish(false, 'Zkontrolujte prosím telefonní číslo.', $wantsJson, 422);
}
if ($d['email'] !== '' && !filter_var($d['email'], FILTER_VALIDATE_EMAIL)) {
    finish(false, 'Zkontrolujte prosím e-mailovou adresu.', $wantsJson, 422);
}
$service = $SERVICES[$d['sluzba']] ?? 'Neuvedeno';

// 4) Sestavení e-mailu
$body = "Nová poptávka z webu " . SITE_NAME . "\n"
      . str_repeat('-', 40) . "\n"
      . "Jméno:    {$d['jmeno']}\n"
      . "Telefon:  {$d['telefon']}\n"
      . "E-mail:   " . ($d['email'] ?: '(neuvedeno)') . "\n"
      . "Služba:   {$service}\n"
      . "Místo:    {$d['misto']}\n"
      . "Termín:   " . ($d['termin'] ?: 'dle domluvy') . "\n"
      . str_repeat('-', 40) . "\n"
      . $d['zprava'] . "\n\n"
      . "Odesláno: " . date('j. n. Y H:i') . "\n"
      . "Zákazník potvrdil, že bere na vědomí zásady ochrany osobních údajů.\n";

$subject = 'Poptávka z webu: ' . $service . ' – ' . $d['misto'];
$headers = [
    'From: ' . mb_encode_mimeheader(SITE_NAME . ' – web', 'UTF-8', 'B') . ' <' . FROM_EMAIL . '>',
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
    'X-Mailer: uklid-pospisil-web',
];
if ($d['email'] !== '') {
    $headers[] = 'Reply-To: =?UTF-8?B?' . base64_encode($d['jmeno']) . '?= <' . $d['email'] . '>';
}

/** Minimal SMTP client (SSL 465 nebo STARTTLS 587) s přihlášením AUTH LOGIN. */
function smtp_send(string $to, string $subject, string $body, array $headers): bool {
    $secure = defined('SMTP_SECURE') ? SMTP_SECURE : 'ssl';
    $host = ($secure === 'ssl' ? 'ssl://' : '') . SMTP_HOST;
    $fp = @stream_socket_client($host . ':' . SMTP_PORT, $errno, $errstr, 15);
    if (!$fp) { error_log("poptavka smtp connect: $errstr"); return false; }
    stream_set_timeout($fp, 15);
    $read = function () use ($fp): string {
        $out = '';
        while (($line = fgets($fp, 515)) !== false) { $out .= $line; if (isset($line[3]) && $line[3] === ' ') break; }
        return $out;
    };
    $cmd = function (string $c, array $expect) use ($fp, $read): bool {
        if ($c !== '') fwrite($fp, $c . "\r\n");
        $r = $read();
        if (!in_array((int)substr($r, 0, 3), $expect, true)) { error_log('poptavka smtp: ' . trim($r)); return false; }
        return true;
    };
    $ehlo = 'EHLO ' . ($_SERVER['SERVER_NAME'] ?? 'localhost');
    $ok = $cmd('', [220]) && $cmd($ehlo, [250]);
    if ($ok && $secure === 'tls') {
        $ok = $cmd('STARTTLS', [220]) && stream_socket_enable_crypto($fp, true, STREAM_CRYPTO_METHOD_TLS_CLIENT) && $cmd($ehlo, [250]);
    }
    $ok = $ok && $cmd('AUTH LOGIN', [334]) && $cmd(base64_encode(SMTP_USER), [334]) && $cmd(base64_encode(SMTP_PASS), [235])
        && $cmd('MAIL FROM:<' . FROM_EMAIL . '>', [250]) && $cmd('RCPT TO:<' . $to . '>', [250, 251]) && $cmd('DATA', [354]);
    if ($ok) {
        $msg = 'Date: ' . date('r') . "\r\n"
             . 'Message-ID: <' . bin2hex(random_bytes(12)) . '@' . substr(strrchr(FROM_EMAIL, '@'), 1) . ">\r\n"
             . 'To: <' . $to . ">\r\n"
             . 'Subject: ' . $subject . "\r\n"
             . implode("\r\n", str_replace('Content-Transfer-Encoding: 8bit', 'Content-Transfer-Encoding: base64', $headers)) . "\r\n\r\n"
             . chunk_split(base64_encode($body));
        $ok = $cmd($msg . "\r\n.", [250]);   // base64 body never contains a lone '.' line
    }
    @fwrite($fp, "QUIT\r\n");
    fclose($fp);
    return $ok;
}

$encSubject = mb_encode_mimeheader($subject, 'UTF-8', 'B');
if (defined('SMTP_HOST') && defined('SMTP_USER') && defined('SMTP_PASS')) {
    $ok = smtp_send(TO_EMAIL, $encSubject, $body, $headers);
} else {
    $ok = mail(TO_EMAIL, $encSubject, $body, implode("\r\n", $headers), '-f' . FROM_EMAIL);
}
if (!$ok) {
    finish(false, 'Poptávku se nepodařilo odeslat. Zavolejte nám prosím.', $wantsJson, 500);
}
$hits[] = time();
@file_put_contents($bucket, implode("\n", $hits));
finish(true, 'Děkujeme, poptávka je odeslaná.', $wantsJson);
'''


PHP_CONFIG_EXAMPLE = """<?php
// Zkopírujte jako poptavka-config.php (nejlépe o složku výš, mimo veřejný web)
// a vyplňte heslo ke schránce. Tento soubor s heslem nikdy nedávejte do gitu.
const SMTP_HOST   = 'mail.webglobe.cz';
const SMTP_PORT   = 465;          // 465 = SSL/TLS, 587 = STARTTLS
const SMTP_SECURE = 'ssl';        // 'ssl' pro 465, 'tls' pro 587
const SMTP_USER   = '__EMAIL__';
const SMTP_PASS   = 'SEM-HESLO-KE-SCHRANCE';
"""


def php_handler():
    services = {s["slug"]: s["name"] for s in SERVICES}
    services["jine"] = "Něco jiného"
    arr = "[\n" + "".join(f"    '{k}' => '{v}',\n" for k, v in services.items()) + "]"
    return PHP_TEMPLATE.replace("__EMAIL__", F["email"]).replace("__SERVICES__", arr)


def kariera():
    return f"""
<section class="page-hero"><div class="wrap">
  <div class="crumbs"><a href="index.html">Úvod</a> / <span>Práce u nás</span></div>
  <h1>Hledáme posily do týmu</h1>
  <p class="lead">Rozšiřujeme tým a hledáme spolehlivé a pečlivé lidi na úklid v Hradci Králové a okolí. Hodí se jako brigáda při studiu, přivýdělek ke stálé práci i k důchodu.</p>
</div></section>

<section class="section" style="padding-top:24px"><div class="wrap grid-2" style="align-items:start">
  <div class="stack" style="gap:24px">
    <div class="check-card"><h3>Co budete dělat</h3><ul class="checks">
      {CHECK_LI.format('běžný úklid domácností a kanceláří')}
      {CHECK_LI.format('luxování, vytírání, utírání prachu, mytí oken')}
      {CHECK_LI.format('úklid kuchyní a koupelen')}
      {CHECK_LI.format('čištění matrací, sedaček a koberců strojem Kärcher, vše vás naučíme')}
    </ul></div>
    <div class="check-card"><h3>Co nabízíme</h3><ul class="checks">
      {CHECK_LI.format('práci na DPP s nástupem ihned')}
      {CHECK_LI.format('odměnu 140 až 160 Kč za hodinu podle zkušeností')}
      {CHECK_LI.format('pracovní dobu podle vašich možností')}
      {CHECK_LI.format('prostředky, pomůcky i odvoz na zakázky')}
      {CHECK_LI.format('zaškolení a férové jednání')}
    </ul></div>
    <div class="check-card"><h3>Co od vás čekáme</h3><ul class="checks">
      {CHECK_LI.format('spolehlivost, pečlivost a chuť pracovat')}
      {CHECK_LI.format('časovou flexibilitu, úklidy bývají i večer a o víkendu')}
      {CHECK_LI.format('výpis z rejstříku trestů')}
      {CHECK_LI.format('řidičský průkaz je výhodou, ale není podmínkou')}
    </ul></div>
  </div>
  <div class="side-card">
    <span class="eyebrow">{ico('briefcase')} Máte zájem?</span>
    <h3 style="font-size:1.5rem">Ozvěte se Michalovi</h3>
    <p class="muted">Zavolejte nebo pošlete krátký životopis e-mailem. Napište, jestli hledáte brigádu, přivýdělek ke stálé práci nebo k důchodu.</p>
    <a class="btn btn--sun" href="{TEL}">{ico('phone')}<span class="nobr">{F['phone']}</span></a>
    <a class="btn btn--ghost" href="{MAILTO}?subject=Z%C3%A1jem%20o%20pr%C3%A1ci">{ico('mail')}{F['email']}</a>
    <p class="muted" style="font-size:.95rem">Životopisy použijeme jen pro výběr spolupracovníků a nejpozději po roce je smažeme. Více v&nbsp;<a href="ochrana-udaju.html">zásadách ochrany osobních údajů</a>.</p>
  </div>
</div></section>
"""


def gdpr():
    def block(title, body):
        return f'<div class="legal-block"><h2>{title}</h2>{body}</div>'
    table = """<div class="table-wrap"><table>
      <thead><tr><th>Kdy údaje získáme</th><th>Jaké údaje</th><th>Proč a na jakém základě</th><th>Jak dlouho</th></tr></thead>
      <tbody>
        <tr><td>Poptávka (formulář, telefon, e-mail, WhatsApp)</td><td>jméno, telefon, e-mail, místo úklidu, popis a fotky prostoru</td><td>odpověď na poptávku a příprava nabídky; jednání o smlouvě (čl. 6 odst. 1 písm. b GDPR)</td><td>nejvýše 1 rok, pokud nevznikne zakázka</td></tr>
        <tr><td>Zakázka a fakturace</td><td>jméno, adresa, kontakt, fakturační údaje, případně klíče od prostor</td><td>provedení úklidu a vystavení dokladu; plnění smlouvy a zákonné povinnosti (písm. b a c)</td><td>po dobu spolupráce, účetní doklady 10 let</td></tr>
        <tr><td>Zájem o práci</td><td>jméno, telefon, e-mail, životopis</td><td>výběr spolupracovníků; jednání o smlouvě (písm. b), případně váš souhlas (písm. a)</td><td>nejvýše 1 rok</td></tr>
        <tr><td>Hodnocení na webu</td><td>křestní jméno a iniciála, text hodnocení</td><td>zveřejnění veřejně dostupných hodnocení z Firmy.cz; oprávněný zájem (písm. f)</td><td>dokud hodnocení nesmažete nebo nevznesete námitku</td></tr>
      </tbody></table></div>
      <p>Poptávkový formulář odešle zprávu přímo z našeho webhostingu do naší e-mailové schránky. Nikde jinde se neukládá a nepoužívá žádnou službu třetí strany. Kvůli ochraně proti spamu si server na jednu hodinu ukládá nevratný otisk (hash) vaší IP adresy.</p>"""
    b0 = block("Správce údajů", f"<p>{F['legal']}, IČO {F['ico']}, se sídlem {F['address']}. Kontakt pro otázky k osobním údajům: <a href=\"{MAILTO}\">{F['email']}</a>, telefon {F['phone']}, datová schránka {F['datovka']}.</p><p class=\"muted\">Pověřence pro ochranu osobních údajů jmenovat nemusíme, zpracováváme jen běžné údaje v malém rozsahu.</p>")
    b1 = block("Jaké údaje zpracováváme a proč", table)
    b2 = block("Komu údaje předáváme", "<p>Údaje neprodáváme a nepředáváme k marketingu. Přístup k nim mají jen naši zpracovatelé, a to poskytovatel webhostingu a e-mailu (Webglobe), účetní a případně spolupracovníci, kteří pro vás úklid provádějí. Dále orgány veřejné moci, pokud to stanoví zákon.</p>")
    b3 = block("Cookies a měření návštěvnosti", "<p>Tento web <b>nepoužívá cookies</b> ani nástroje pro měření návštěvnosti či reklamu. Písma načítá z vlastního serveru, takže o vaší návštěvě nedáváme vědět žádné třetí straně. Proto se vás na nic neptáme žádnou lištou.</p>")
    b4 = block("Vaše práva", f"<p>Máte právo na přístup ke svým údajům, na jejich opravu nebo výmaz, na omezení zpracování, na přenositelnost a právo vznést námitku. Pokud údaje zpracováváme na základě souhlasu, můžete ho kdykoli odvolat. Stačí napsat na <a href=\"{MAILTO}\">{F['email']}</a>, odpovíme do 30 dnů.</p><p>Stížnost můžete podat u Úřadu pro ochranu osobních údajů, Pplk. Sochora 27, 170 00 Praha 7, <a href=\"https://uoou.gov.cz\" target=\"_blank\" rel=\"noopener\">uoou.gov.cz</a>.</p>")
    b5 = block("Spotřebitelské spory", "<p>Pokud jste spotřebitel a nedohodneme se, můžete se obrátit na subjekt mimosoudního řešení spotřebitelských sporů, kterým je Česká obchodní inspekce, <a href=\"https://adr.coi.cz\" target=\"_blank\" rel=\"noopener\">adr.coi.cz</a>.</p>")
    b6 = block("Údaje o podnikateli", f"<p>{F['legal']}, IČO {F['ico']}, {F['address']}. Fyzická osoba podnikající podle živnostenského zákona, zapsaná v živnostenském rejstříku. Nejsme plátci DPH.</p>")
    return f"""
<section class="page-hero"><div class="wrap">
  <div class="crumbs"><a href="index.html">Úvod</a> / <span>Ochrana osobních údajů</span></div>
  <h1>Ochrana osobních údajů</h1>
  <p class="lead">Srozumitelně: jaké údaje od vás potřebujeme, proč a jak s nimi zacházíme. Podle nařízení (EU) 2016/679 (GDPR) a zákona č. 110/2019 Sb. Platné od [datum spuštění webu].</p>
</div></section>

<section class="section" style="padding-top:24px"><div class="wrap stack" style="gap:36px;max-width:980px">
  {b0}
  {b1}
  {b2}
  {b3}
  {b4}
  {b5}
  {b6}
</div></section>
"""


# Old URLs -> new pages, so links from Google and old flyers keep working (see README)
REDIRECTS = {
    "/nase-sluzby": "/sluzby.html", "/nase-sluzby/": "/sluzby.html",
    "/cenik-sluzeb": "/cenik.html", "/cenik-sluzeb/": "/cenik.html",
    "/neco-o-nas": "/o-nas.html", "/neco-o-nas/": "/o-nas.html",
    "/cisteni-kobercu-a-sedacek/": "/cisteni-kobercu-a-calouneni.html",
    "/foto/": "/reference.html#pred-a-po", "/fotogalerie/": "/reference.html#pred-a-po",
    "/recenze/": "/reference.html",
    "/kontakt/": "/kontakt.html",
    "/rychla-poptavka/": "/kontakt.html", "/rychla-poptavka-cisteni/": "/kontakt.html",
    "/kariera/": "/kariera.html", "/nabidka-brigady/": "/kariera.html", "/nabidka-prace/": "/kariera.html",
    "/gdpr/": "/ochrana-udaju.html", "/zasady-cookies-eu/": "/ochrana-udaju.html",
}


def build():
    global FONT_CSS
    FONT_CSS = font_css() if MODE != "site" else ""
    os.makedirs(OUT, exist_ok=True)
    pages = [
        ("index.html", "Úklid Pospíšil – úklidová firma Hradec Králové a okolí",
         "Rodinná úklidová firma z Hradce Králové. Úklid domácností, firem a staveb, mytí oken, čištění koberců, sedaček a matrací. Do 100 km včetně Prahy.",
         "", home(), True),
        ("sluzby.html", "Úklidové služby Hradec Králové", "Úklid domácností, firem a společných prostor, úklid po stavbě, mytí oken, čištění koberců a matrací, úklid po havárii.", "sluzby", sluzby(), False),
        ("cenik.html", "Ceník a kalkulace", "Jak počítáme cenu úklidu a čištění. Kalkulace zdarma, nejrychleji podle fotek přes WhatsApp. Nejsme plátci DPH.", "cenik", cenik(), False),
        ("o-nas.html", "O nás", "Rodinná úklidová firma Michala Pospíšila ze Světí u Hradce Králové. Pojištění, faktura, vlastní stroje Kärcher.", "onas", onas(), False),
        ("reference.html", "Reference a fotky před a po", "Hodnocení zákazníků a skutečné fotky před a po úklidu.", "reference", reference(), False),
        ("kontakt.html", "Kontakt a poptávka", f"Telefon {F['phone']}, e-mail {F['email']}. Nezávazná poptávka úklidu.", "kontakt", kontakt(), False),
        ("kariera.html", "Práce u nás", "Hledáme spolehlivé lidi na úklid v Hradci Králové a okolí. DPP, flexibilní pracovní doba.", "", kariera(), False),
        ("dekujeme.html", "Děkujeme", "Poptávka byla odeslána.", "", dekujeme(), False),
        ("ochrana-udaju.html", "Ochrana osobních údajů", "Jak Úklid Pospíšil zpracovává osobní údaje.", "", gdpr(), False),
    ]
    for s in SERVICES:
        pages.append((f"{s['slug']}.html", f"{s['name']} Hradec Králové", s["lead"], "sluzby", service_page(s), False))

    for fn, title, desc, active, body, is_home in pages:
        with open(os.path.join(OUT, fn), "w", encoding="utf-8") as fh:
            fh.write(page(title, desc, active, body, is_home))

    if MODE == "site":
        os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
        with open(os.path.join(OUT, "assets", "style.css"), "w", encoding="utf-8") as fh:
            fh.write(font_css() + "\n" + open(os.path.join(ROOT, "src", "style.css"), encoding="utf-8").read())
        shutil.copy(os.path.join(ROOT, "src", "main.js"), os.path.join(OUT, "assets", "main.js"))
        shutil.copytree(os.path.join(ROOT, "src", "fonts"), os.path.join(OUT, "assets", "fonts"), dirs_exist_ok=True)
        for f in ("favicon-64.png", "apple-touch-icon.png", "logo-original.png"):
            shutil.copy(os.path.join(ROOT, "src", "logo", f), os.path.join(OUT, "assets", f))
        # Netlify / Cloudflare Pages format; Apache (.htaccess) version for classic Czech webhosting
        with open(os.path.join(OUT, "_redirects"), "w", encoding="utf-8") as fh:
            fh.write("".join(f"{a}  {b}  301\n" for a, b in REDIRECTS.items()))
        with open(os.path.join(OUT, ".htaccess"), "w", encoding="utf-8") as fh:
            fh.write('<FilesMatch "^poptavka-config">\n  Require all denied\n</FilesMatch>\n'
                     "RewriteEngine On\n" + "".join(
                f"RewriteRule ^{re.escape(a.strip('/'))}/?$ {b.split('#')[0]} [R=301,L{',NE' if '#' in b else ''}]\n"
                for a, b in REDIRECTS.items() if not a.endswith('/') or a.rstrip('/') not in REDIRECTS))
        with open(os.path.join(OUT, "poptavka.php"), "w", encoding="utf-8") as fh:
            fh.write(php_handler())
        with open(os.path.join(OUT, "poptavka-config.example.php"), "w", encoding="utf-8") as fh:
            fh.write(PHP_CONFIG_EXAMPLE.replace("__EMAIL__", F["email"]))
        # the Vercel demo cannot run PHP; keep the handler out of it
        with open(os.path.join(OUT, ".vercelignore"), "w", encoding="utf-8") as fh:
            fh.write("poptavka.php\npoptavka-config.example.php\n")
        with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as fh:
            fh.write(f"User-agent: *\nAllow: /\nSitemap: https://{F['domain']}/sitemap.xml\n")
        with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as fh:
            urls = "".join(f"<url><loc>https://{F['domain']}/{'' if p[0] == 'index.html' else p[0]}</loc></url>" for p in pages if p[0] != "dekujeme.html")
            fh.write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    else:
        shutil.copytree(os.path.join(ROOT, "site", "img"), os.path.join(OUT, "img"), dirs_exist_ok=True)
    print(f"Built {len(pages)} pages into {OUT}")


if __name__ == "__main__":
    build()
