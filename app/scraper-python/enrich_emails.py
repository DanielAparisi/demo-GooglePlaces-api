import os
import re
import time
import requests
import pandas as pd
from urllib.parse import quote

from config import requerir

SCRAPEDO_TOKEN = requerir('SCRAPEDO_TOKEN')
CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Leads Google Maps.csv')
DELAY_BETWEEN_CALLS = 3

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')

SOCIAL_PATTERNS = {
    'Facebook':  re.compile(r'https?://(?:www\.)?facebook\.com/(?!sharer|share|dialog|pages/create)([A-Za-z0-9._\-]{3,})', re.I),
    'Instagram': re.compile(r'https?://(?:www\.)?instagram\.com/([A-Za-z0-9._]{1,30})(?:[/?#]|$)', re.I),
    'LinkedIn':  re.compile(r'https?://(?:www\.)?linkedin\.com/(?:company|in)/([A-Za-z0-9._\-]+)', re.I),
    'Twitter':   re.compile(r'https?://(?:www\.)?(?:twitter|x)\.com/(?!share|intent|home)([A-Za-z0-9_]{1,15})(?:[/?#]|$)', re.I),
    'TikTok':    re.compile(r'https?://(?:www\.)?tiktok\.com/@([A-Za-z0-9._]{1,24})(?:[/?#]|$)', re.I),
    'YouTube':   re.compile(r'https?://(?:www\.)?youtube\.com/(?:channel/|c/|@)([A-Za-z0-9._\-]+)', re.I),
}

DOMINIOS_EXCLUIDOS_EMAIL = {
    'sentry.io', 'wixpress.com', 'example.com', 'domain.com',
    'email.com', 'correo.com', 'tuempresa.com', 'empresa.com',
    'google.com', 'googleapis.com', 'gstatic.com', 'w3.org',
    'schema.org', 'facebook.com', 'twitter.com', 'instagram.com',
    'youtube.com', 'linkedin.com', 'whatsapp.com',
}

SLUGS_IGNORADOS = {
    'hashtag', 'explore', 'events', 'pages', 'groups', 'marketplace',
    'watch', 'gaming', 'home', 'profile', 'login', 'signup', 'about',
    'help', 'legal', 'privacy', 'terms', 'search', 'reel', 'reels',
    'stories', 'notifications', 'messages', 'p', 'tv',
}


def scrape_url(url):
    api_url = f"https://api.scrape.do?token={SCRAPEDO_TOKEN}&url={quote(url, safe='')}&render=false"
    try:
        resp = requests.get(api_url, timeout=30)
        if resp.status_code == 200:
            return resp.text
    except Exception as e:
        print(f"  Error scrape.do: {e}")
    return None


def extraer_emails(html):
    if not html:
        return []
    encontrados = EMAIL_REGEX.findall(html)
    vistos = set()
    limpios = []
    for email in encontrados:
        email = email.lower().rstrip('.')
        dominio = email.split('@')[-1]
        if dominio not in DOMINIOS_EXCLUIDOS_EMAIL and email not in vistos:
            vistos.add(email)
            limpios.append(email)
    return limpios


def extraer_redes(html):
    if not html:
        return {}
    resultados = {}
    for red, patron in SOCIAL_PATTERNS.items():
        matches = patron.findall(html)
        for slug in matches:
            slug_limpio = slug.strip('/').lower()
            if slug_limpio not in SLUGS_IGNORADOS and len(slug_limpio) >= 3:
                if red == 'Facebook':
                    resultados[red] = f"https://facebook.com/{slug_limpio}"
                elif red == 'Instagram':
                    resultados[red] = f"https://instagram.com/{slug_limpio}"
                elif red == 'LinkedIn':
                    resultados[red] = f"https://linkedin.com/company/{slug_limpio}"
                elif red == 'Twitter':
                    resultados[red] = f"https://x.com/{slug_limpio}"
                elif red == 'TikTok':
                    resultados[red] = f"https://tiktok.com/@{slug_limpio}"
                elif red == 'YouTube':
                    resultados[red] = f"https://youtube.com/@{slug_limpio}"
                break
    return resultados


def buscar_info(nombre, ubicacion):
    ciudad = ubicacion.split(',')[-2].strip() if ',' in ubicacion else ubicacion
    email = None
    redes = {}

    queries = [
        f'"{nombre}" "{ciudad}" site:facebook.com OR site:instagram.com OR site:linkedin.com OR site:tiktok.com',
        f'"{nombre}" "{ciudad}" correo electrónico OR email OR contacto',
        f'"{nombre}" "{ciudad}"',
    ]
    fuentes_extra = [
        f"https://www.paginasamarillas.es/search/{quote(nombre + ' ' + ciudad)}/all-ma/all-pr/all-is/all-ci/all-ba/all-pu/1",
    ]

    for query in queries:
        if email and len(redes) >= 3:
            break
        url = f"https://www.google.es/search?q={quote(query)}&hl=es&num=10"
        html = scrape_url(url)
        if not email:
            emails = extraer_emails(html)
            if emails:
                email = emails[0]
        nuevas = extraer_redes(html)
        redes.update({k: v for k, v in nuevas.items() if k not in redes})
        time.sleep(1)

    for url in fuentes_extra:
        if email and len(redes) >= 3:
            break
        html = scrape_url(url)
        if not email:
            emails = extraer_emails(html)
            if emails:
                email = emails[0]
        nuevas = extraer_redes(html)
        redes.update({k: v for k, v in nuevas.items() if k not in redes})
        time.sleep(1)

    return email, redes


COLUMNAS_REDES = ['Facebook', 'Instagram', 'LinkedIn', 'Twitter', 'TikTok', 'YouTube']


def main():
    df = pd.read_csv(CSV_FILE, encoding='utf-8-sig', dtype=str).fillna('')

    for col in ['Email'] + COLUMNAS_REDES:
        if col not in df.columns:
            df[col] = ''
    if 'enriched' not in df.columns:
        df['enriched'] = ''

    pendientes = [idx for idx in df.index if df.at[idx, 'enriched'] != 'True']
    print(f"Negocios a enriquecer: {len(pendientes)} de {len(df)} totales.\n")

    for i, idx in enumerate(pendientes):
        nombre = df.at[idx, 'Nombre del negocio']
        ubicacion = df.at[idx, 'Ubicación']

        print(f"[{i+1}/{len(pendientes)}] {nombre}")

        email, redes = buscar_info(nombre, ubicacion)

        if email and (pd.isna(df.at[idx, 'Email']) or df.at[idx, 'Email'] == ''):
            df.at[idx, 'Email'] = email
            print(f"  Email      → {email}")

        for red, url in redes.items():
            if pd.isna(df.at[idx, red]) or df.at[idx, red] == '':
                df.at[idx, red] = url
                print(f"  {red:<10} → {url}")

        if not email and not redes:
            print("  → Sin datos encontrados.")

        df.at[idx, 'enriched'] = 'True'
        df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')

        if i < len(pendientes) - 1:
            time.sleep(DELAY_BETWEEN_CALLS)

    encontrados_email = (df['Email'].notna() & (df['Email'] != '')).sum()
    print(f"\nCompletado:")
    print(f"  Emails: {encontrados_email}/{len(df)}")
    for col in COLUMNAS_REDES:
        count = (df[col].notna() & (df[col] != '')).sum()
        if count:
            print(f"  {col}: {count}/{len(df)}")
    print(f"\nCSV guardado: '{CSV_FILE}'")


if __name__ == '__main__':
    main()
