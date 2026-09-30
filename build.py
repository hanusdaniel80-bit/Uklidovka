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

LOGO_MARK = (
    '<svg class="logo-mark" viewBox="0 0 48 48" aria-hidden="true">'
    '<rect class="lm-bg" x="1" y="1" width="46" height="46" rx="14"/>'
    '<path class="lm-star" d="M22 9c1.1 8 4.6 11.5 12.5 12.6C26.6 22.7 23.1 26.2 22 34.2 20.9 26.2 17.4 22.7 9.5 21.6 17.4 20.5 20.9 17 22 9z"/>'
    '<circle class="lm-dot" cx="34.5" cy="34" r="4"/>'
    "</svg>"
)
LOGO_TEXT = '<span class="logo-text"><span class="logo-name">Úklid <span>Pospíšil</span></span><span class="logo-sub">Rodinná firma z Hradce</span></span>'

# --------------------------------------------------------------------------
# Photos: all of them are Michal's own photos from the old website
# (people at work in "Pospíšilovi" T-shirts, the before/after job in Jaroměř).
# key: (file, alt text, fallback icon, object-position)
# --------------------------------------------------------------------------
PHOTOS = {
    "hero": ("hero.jpg", "Dvě kolegyně z týmu Úklid Pospíšil ve firemních tričkách s čisticím strojem Kärcher", "home", "50% 40%"),
    "domacnosti": ("domacnosti.jpg", "Kolegyně vysává podlahu v bytě", "home", "50% 45%"),
    "firmy": ("firmy.jpg", "Kolegyně omývá dveře na chodbě", "office", "50% 40%"),
    "stavba": ("stavba.jpg", "Úklid nového bytu po řemeslnících, práce ze štaflí", "roller", "50% 40%"),
    "okna": ("okna.jpg", "Kolegyně myje okno na chodbě domu", "window", "50% 30%"),
    "koberce": ("koberce.jpg", "Hloubkové čištění koberce strojem Kärcher Puzzi", "sofa", "50% 50%"),
    "pojistna": ("pojistna.jpg", "Silně znečištěná podlaha před úklidem", "drop", "50% 60%"),
    "spolecne": ("spolecne-prostory.jpg", "Úklid chodby v bytovém domě", "people", "50% 45%"),
    "tricko": ("tricko.jpg", "Firemní tričko Pospíšilovi – úklidové práce", "user", "50% 30%"),
}


def photo(key, extra_cls="", eager=False):
    file, alt, icon, pos = PHOTOS[key]
    if os.path.exists(os.path.join(ROOT, "site", "img", file)):
        loading = "eager" if eager else "lazy"
        return (f'<figure class="photo {extra_cls}" style="margin:0">'
                f'<img src="img/{file}" alt="{html.escape(alt)}" loading="{loading}" decoding="async" style="object-position:{pos}"></figure>')
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
        "slug": "uklid-domacnosti", "key": "domacnosti", "icon": "home",
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
        "slug": "uklid-firem", "key": "firmy", "icon": "office",
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
        "slug": "uklid-po-stavbe", "key": "stavba", "icon": "roller",
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
        "slug": "myti-oken", "key": "okna", "icon": "window",
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
        "slug": "cisteni-kobercu-a-calouneni", "key": "koberce", "icon": "sofa",
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
        "slug": "uklid-po-pojistne-udalosti", "key": "pojistna", "icon": "drop",
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
      <span>© {F['legal']} · IČO {F['ico']} · Nejsme plátci DPH</span>
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
<meta property="og:image" content="https://{F['domain']}/img/hero.jpg">
<meta property="og:locale" content="cs_CZ">
<meta name="theme-color" content="#0e6a5a">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
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
    ("Excelentní provedení služeb a vynikající zákaznický servis i v, řekněme, méně obvyklé časy. Služby této úklidové firmy jistě znovu využiji.", "Tomáš Jirousek", "12. 10. 2024"),
    ("Děkuji za skvěle provedený úklid. Výborná domluva a ochotný přístup. Mohu jen a jen doporučit.", "Ondřej Vlasák", "12. 10. 2024"),
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
      {photo('hero', eager=True)}
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
    <h3>Jak počítáme cenu</h3>
    <p class="muted">{s['pricing']}</p>
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


def cenik():
    rows = "".join(
        f'<tr><td><a href="{s["slug"]}.html">{s["name"]}</a></td><td>{s["pricing"]}</td></tr>' for s in SERVICES)
    return f"""
<section class="page-hero"><div class="wrap">
  <div class="crumbs"><a href="index.html">Úvod</a> / <span>Ceník</span></div>
  <h1>Ceník a kalkulace</h1>
  <p class="lead">Každý úklid je jiný. Garsonka po malování a dům po zimě se nedají nacenit stejně, proto cenu stanovujeme vždy podle vašeho zadání. Kalkulace je zdarma a cenu znáte dopředu.</p>
</div></section>

<section class="section" style="padding-top:28px"><div class="wrap stack" style="gap:24px">
  <h2>Jak počítáme cenu u&nbsp;jednotlivých služeb</h2>
  <div class="table-wrap"><table>
    <thead><tr><th>Služba</th><th>Jak se cena počítá</th></tr></thead>
    <tbody>{rows}</tbody>
  </table></div>
</div></section>

<section class="section section--tint"><div class="wrap grid-2" style="align-items:start">
  <div class="stack" style="gap:20px">
    <h2>Co ovlivňuje cenu</h2>
    <div class="check-card"><ul class="checks">
      <li>{ico('check')}<span><b>Rozsah práce</b>, tedy počet místností, metrů čtverečních, oken nebo kusů nábytku.</span></li>
      <li>{ico('check')}<span><b>Míra znečištění a přístupnost.</b> Běžný úklid je jiný než úklid po stavbě.</span></li>
      <li>{ico('check')}<span><b>Čas.</b> Večer, o víkendu a ve svátek účtujeme příplatek, vždy předem domluvený.</span></li>
      <li>{ico('check')}<span><b>Vzdálenost.</b> V Hradci Králové je doprava zdarma, jinde podle kilometrů.</span></li>
    </ul></div>
    <h2 style="margin-top:12px">Dobré vědět</h2>
    <div class="check-card"><ul class="checks">
      <li>{ico('check')}<span><b>Nejsme plátci DPH.</b> Cena, kterou vám řekneme, je konečná.</span></li>
      <li>{ico('check')}<span><b>Máme pojištění odpovědnosti</b> za případné škody.</span></li>
      <li>{ico('check')}<span><b>Fakturujeme</b> firmám i OSVČ.</span></li>
      <li>{ico('check')}<span><b>Kalkulace je zdarma</b> a k ničemu vás nezavazuje.</span></li>
    </ul></div>
  </div>
  <div class="side-card">
    <span class="eyebrow">{ico('camera')} Nejrychlejší cesta k ceně</span>
    <h3 style="font-size:1.5rem">Pošlete fotky přes WhatsApp</h3>
    <p class="muted">Nafoťte, co potřebujete uklidit nebo vyčistit, a připište obec a přibližnou velikost. Podle fotek vám obvykle řekneme cenu bez nutnosti prohlídky.</p>
    <a class="btn btn--sun" href="{WHATSAPP}" target="_blank" rel="noopener">{ico('chat')}Poslat fotky na WhatsApp</a>
    <p class="muted" style="font-size:.95rem">Číslo pro WhatsApp i volání: <b class="nobr">{F['phone']}</b></p>
  </div>
</div></section>

<section class="section"><div class="wrap stack" style="gap:20px;max-width:900px">
  <h2>Časté dotazy k&nbsp;ceně</h2>
  <div class="faq">
    <details><summary>Je kalkulace opravdu zdarma?</summary><p>Ano. Nacenění po telefonu, podle fotek i prohlídka u větších zakázek jsou zdarma a k ničemu vás nezavazují.</p></details>
    <details><summary>Může se cena na místě změnit?</summary><p>Jen pokud se na místě ukáže něco, o čem jsme nevěděli, a vždy až po domluvě s vámi. Proto u větších zakázek jezdíme nejdřív na prohlídku.</p></details>
    <details><summary>Proč nemáte ceny přímo na webu?</summary><p>Protože by vás zbytečně mátly. Cena záleží na rozsahu a stavu prostoru a u každé zakázky je jiná. Po krátkém telefonátu nebo pár fotkách vám řekneme přesnou částku.</p></details>
  </div>
</div></section>
{cta_band("Chcete znát cenu?", "Zavolejte nebo vyplňte krátkou poptávku. Na poptávky odpovídáme co nejdřív, obvykle do hodiny.")}
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
    <form class="form" id="poptavka" novalidate>
      <div class="stack" style="gap:6px"><h2 style="font-size:1.7rem">Nezávazná poptávka</h2>
        <p class="muted" style="font-size:1rem">Vyplnění zabere asi minutu. Pole s hvězdičkou jsou povinná.</p></div>
      <div class="form-row">
        <div class="field"><label for="f-jmeno">Jméno *</label><input id="f-jmeno" name="jmeno" autocomplete="name" required></div>
        <div class="field"><label for="f-telefon">Telefon *</label><input id="f-telefon" name="telefon" type="tel" autocomplete="tel" required></div>
      </div>
      <div class="form-row">
        <div class="field"><label for="f-email">E-mail <span class="opt">(nepovinné)</span></label><input id="f-email" name="email" type="email" autocomplete="email"></div>
        <div class="field"><label for="f-sluzba">Služba *</label><select id="f-sluzba" name="sluzba" required><option value="">Vyberte…</option>{opts}<option value="jine">Něco jiného</option></select></div>
      </div>
      <div class="form-row">
        <div class="field"><label for="f-misto">Obec, kde se uklízí *</label><input id="f-misto" name="misto" required placeholder="např. Hradec Králové"></div>
        <div class="field"><label for="f-termin">Kdy by se vám hodilo <span class="opt">(nepovinné)</span></label><input id="f-termin" name="termin" placeholder="např. příští týden"></div>
      </div>
      <div class="field"><label for="f-zprava">Co potřebujete uklidit *</label><textarea id="f-zprava" name="zprava" required placeholder="např. byt 3+1 po malování, asi 75 m², včetně oken"></textarea></div>
      <label class="check-field" for="f-souhlas"><input id="f-souhlas" type="checkbox" name="souhlas" required><span>Beru na vědomí, že mé údaje zpracujete kvůli vyřízení poptávky. Více v&nbsp;<a href="ochrana-udaju.html">zásadách ochrany osobních údajů</a>.</span></label>
      <button class="btn btn--sun" type="submit">Odeslat poptávku {ico('arrow')}</button>
    </form>
    <div class="form-done" id="poptavka-done" hidden>
      <h3>Děkujeme, poptávka je připravená</h3>
      <p class="muted">V ukázce se nic neodesílá. Na hotovém webu přijde tato zpráva e-mailem na {F['email']}:</p>
      <pre></pre>
      <button class="btn btn--ghost btn--small" type="button" id="poptavka-again">Upravit poptávku</button>
    </div>
  </div>
</div></section>

<section class="section section--tint"><div class="wrap">{area_block()}</div></section>
"""


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
  </div>
</div></section>
"""


def gdpr():
    return f"""
<section class="page-hero"><div class="wrap">
  <div class="crumbs"><a href="index.html">Úvod</a> / <span>Ochrana osobních údajů</span></div>
  <h1>Ochrana osobních údajů</h1>
  <p class="lead">Stručně a srozumitelně: jaké údaje od vás potřebujeme, proč a jak s nimi zacházíme. V souladu s nařízením GDPR a zákonem č. 110/2019 Sb.</p>
</div></section>

<section class="section" style="padding-top:24px"><div class="wrap prose">
  <h2>Kdo vaše údaje zpracovává</h2>
  <p>{F['legal']}, IČO {F['ico']}, {F['address']}. E-mail {F['email']}, telefon {F['phone']}.</p>
  <h2>Jaké údaje a proč</h2>
  <p>Jméno, telefon, e-mail a adresu místa úklidu, abychom mohli vyřídit vaši poptávku, domluvit a provést úklid a vystavit doklad. Právním základem je jednání o smlouvě a její plnění a u dokladů naše zákonná povinnost.</p>
  <h2>Jak dlouho je uchováváme</h2>
  <p>Po dobu spolupráce a poté jen tak dlouho, jak ukládá zákon, například účetní doklady 10 let. Poptávky, ze kterých nevznikla zakázka, mažeme nejpozději do jednoho roku.</p>
  <h2>Komu je předáváme</h2>
  <p>Nikomu je neprodáváme. Přístup k nim mají jen naši dodavatelé účetních, IT a webhostingových služeb a orgány veřejné moci, pokud to stanoví zákon.</p>
  <h2>Cookies</h2>
  <p>Tento web nepoužívá reklamní ani sledovací cookies a písma načítá z vlastního serveru.</p>
  <h2>Vaše práva</h2>
  <p>Máte právo na přístup ke svým údajům, jejich opravu nebo výmaz, omezení zpracování, přenositelnost a vznesení námitky. Stačí napsat na {F['email']}. Stížnost můžete podat u Úřadu pro ochranu osobních údajů, <a href="https://uoou.gov.cz" target="_blank" rel="noopener">uoou.gov.cz</a>.</p>
</div></section>
"""


FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect x="1" y="1" width="46" height="46" rx="14" fill="#0e6a5a"/>'
           '<path fill="#fff" d="M22 9c1.1 8 4.6 11.5 12.5 12.6C26.6 22.7 23.1 26.2 22 34.2 20.9 26.2 17.4 22.7 9.5 21.6 17.4 20.5 20.9 17 22 9z"/>'
           '<circle fill="#f6b93b" cx="34.5" cy="34" r="4"/></svg>')

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
        with open(os.path.join(OUT, "assets", "favicon.svg"), "w", encoding="utf-8") as fh:
            fh.write(FAVICON)
        # Netlify / Cloudflare Pages format; Apache (.htaccess) version for classic Czech webhosting
        with open(os.path.join(OUT, "_redirects"), "w", encoding="utf-8") as fh:
            fh.write("".join(f"{a}  {b}  301\n" for a, b in REDIRECTS.items()))
        with open(os.path.join(OUT, ".htaccess"), "w", encoding="utf-8") as fh:
            fh.write("RewriteEngine On\n" + "".join(
                f"RewriteRule ^{re.escape(a.strip('/'))}/?$ {b.split('#')[0]} [R=301,L{',NE' if '#' in b else ''}]\n"
                for a, b in REDIRECTS.items() if not a.endswith('/') or a.rstrip('/') not in REDIRECTS))
        with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as fh:
            fh.write(f"User-agent: *\nAllow: /\nSitemap: https://{F['domain']}/sitemap.xml\n")
        with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as fh:
            urls = "".join(f"<url><loc>https://{F['domain']}/{'' if p[0] == 'index.html' else p[0]}</loc></url>" for p in pages)
            fh.write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    else:
        shutil.copytree(os.path.join(ROOT, "site", "img"), os.path.join(OUT, "img"), dirs_exist_ok=True)
    print(f"Built {len(pages)} pages into {OUT}")


if __name__ == "__main__":
    build()
