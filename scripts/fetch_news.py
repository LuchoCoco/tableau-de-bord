#!/usr/bin/env python3
"""
Robot d'actus du tableau de bord.

Lit sources-actus.json, télécharge chaque flux RSS/Atom et écrit news.json.
On ne garde QUE le titre, la source, le lien et l'heure (jamais le texte des articles).
N'utilise que la bibliothèque standard de Python : rien à installer.

Lancement à la main (depuis le dossier du projet) :  python3 scripts/fetch_news.py
"""
import html
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FICHIER_SOURCES = os.path.join(RACINE, "sources-actus.json")
FICHIER_SORTIE = os.path.join(RACINE, "news.json")
AGENT = "Mozilla/5.0 (compatible; tableau-de-bord-actus/1.0)"


def telecharger(url):
    req = urllib.request.Request(url, headers={"User-Agent": AGENT, "Accept": "application/rss+xml, application/xml, text/xml, */*"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read()


def nettoyer(texte):
    texte = re.sub(r"<[^>]+>", "", texte or "")
    texte = html.unescape(html.unescape(texte))
    return re.sub(r"\s+", " ", texte).strip()


def lire_date(texte):
    texte = (texte or "").strip()
    if not texte:
        return None
    try:
        d = parsedate_to_datetime(texte)  # format RSS : "Wed, 12 Nov 2026 07:30:00 +0100"
    except (TypeError, ValueError, IndexError):
        d = None
    if d is None:
        try:
            d = datetime.fromisoformat(texte.replace("Z", "+00:00"))  # format Atom : "2026-11-12T07:30:00Z"
        except ValueError:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return int(d.timestamp() * 1000)


def nom_local(tag):
    return tag.rsplit("}", 1)[-1].lower() if isinstance(tag, str) else ""


def analyser_xml(donnees):
    racine = ET.fromstring(donnees.lstrip())
    articles = []
    for el in racine.iter():
        if nom_local(el.tag) not in ("item", "entry"):
            continue
        titre, lien, date = "", "", None
        for enfant in el:
            n = nom_local(enfant.tag)
            if n == "title":
                titre = "".join(enfant.itertext())
            elif n == "link":
                href = enfant.get("href")
                if href and (enfant.get("rel") in (None, "alternate")):
                    lien = lien or href
                elif not href and enfant.text:
                    lien = lien or enfant.text.strip()
            elif n in ("pubdate", "published", "updated", "date") and date is None:
                date = lire_date(enfant.text)
        articles.append((titre, lien, date))
    return articles


def analyser_regex(donnees):
    """Plan B si le XML est mal formé : extraction simple par motifs."""
    texte = donnees.decode("utf-8", "replace")
    articles = []
    for bloc in re.findall(r"<(?:item|entry)\b.*?</(?:item|entry)>", texte, re.S | re.I):
        def champ(nom):
            m = re.search(r"<%s\b[^>]*>(.*?)</%s>" % (nom, nom), bloc, re.S | re.I)
            return re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", m.group(1), flags=re.S) if m else ""
        lien = champ("link")
        if not lien:
            m = re.search(r'<link[^>]+href="([^"]+)"', bloc)
            lien = m.group(1) if m else ""
        articles.append((champ("title"), lien.strip(), lire_date(champ("pubDate") or champ("published") or champ("updated"))))
    return articles


def lire_flux(source):
    donnees = telecharger(source["url"])
    try:
        bruts = analyser_xml(donnees)
    except ET.ParseError:
        bruts = analyser_regex(donnees)
    articles = []
    for titre, lien, date in bruts:
        titre = nettoyer(titre)
        if titre and lien.startswith("http"):
            articles.append({"titre": titre[:220], "source": source["nom"], "lien": lien, "dateMs": date})
    return articles


def main():
    with open(FICHIER_SOURCES, encoding="utf-8") as f:
        conf = json.load(f)
    max_theme = conf.get("maxParTheme", 12)
    max_source = conf.get("maxParSource", 4)
    limite_ms = conf.get("heuresMax", 36) * 3600 * 1000
    maintenant = int(datetime.now(timezone.utc).timestamp() * 1000)

    themes, erreurs, total = [], [], 0
    vus = set()  # titres déjà pris (évite qu'un même article apparaisse dans 2 thèmes)
    for theme in conf["themes"]:
        if not theme.get("actif", True):
            continue
        tous = []
        for source in theme["sources"]:
            try:
                articles = lire_flux(source)
                articles.sort(key=lambda a: a["dateMs"] or 0, reverse=True)
                recents = [a for a in articles if a["dateMs"] and maintenant - a["dateMs"] < limite_ms and a["dateMs"] < maintenant + 3600 * 1000]
                tous.extend((recents or articles)[:max_source])
                print("OK   %-25s %d articles" % (source["nom"], len(articles)))
            except Exception as e:  # une source en panne ne bloque pas les autres
                erreurs.append({"source": source["nom"], "message": str(e)[:200]})
                print("ERR  %-25s %s" % (source["nom"], e), file=sys.stderr)
        # Supprime les doublons (même titre) puis trie du plus récent au plus ancien
        uniques = []
        for a in sorted(tous, key=lambda a: a["dateMs"] or 0, reverse=True):
            cle = re.sub(r"\W+", "", a["titre"].lower())
            if cle not in vus:
                vus.add(cle)
                uniques.append(a)
        for a in uniques[max_theme:]:
            vus.discard(re.sub(r"\W+", "", a["titre"].lower()))
        uniques = uniques[:max_theme]
        total += len(uniques)
        themes.append({"id": theme["id"], "nom": theme["nom"], "items": uniques})

    if total == 0:
        print("Aucun article récupéré : news.json n'est pas modifié.", file=sys.stderr)
        sys.exit(1)

    sortie = {
        "genere": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "genereMs": maintenant,
        "themes": themes,
        "erreurs": erreurs,
    }
    with open(FICHIER_SORTIE, "w", encoding="utf-8") as f:
        json.dump(sortie, f, ensure_ascii=False, indent=1)
    print("news.json écrit : %d titres, %d erreur(s)." % (total, len(erreurs)))


if __name__ == "__main__":
    main()
