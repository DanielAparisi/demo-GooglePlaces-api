import re
import time
import requests
import pandas as pd
from urllib.parse import quote

SCRAPEDO_TOKEN = 'SU_TOKEN_AQUI'
CSV_FILE = 'Leads Google Maps.csv'
DELAY_BETWEEN_CALLS = 3

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
DOMINIOS_EXCLUIDOS = {
    'sentry.io', 'wixpress.com', 'example.com', 'domain.com',
    'email.com', 'correo.com', 'tuempresa.com', 'empresa.com',
    'google.com', 'googleapis.com', 'gstatic.com', 'w3.org',
    'schema.org', 'facebook.com', 'twitter.com', 'instagram.com',
    'youtube.com', 'linkedin.com', 'whatsapp.com',
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
        if dominio not in DOMINIOS_EXCLUIDOS and email not in vistos:
            vistos.add(email)
            limpios.append(email)
    return limpios


def buscar_email(nombre, ubicacion):
    ciudad = ubicacion.split(',')[-2].strip() if ',' in ubicacion else ubicacion

    # Fuente 1: Google Search
    query_google = f'"{nombre}" "{ciudad}" correo electrónico OR email OR contacto'
    url_google = f"https://www.google.es/search?q={quote(query_google)}&hl=es&num=5"
    html = scrape_url(url_google)
    emails = extraer_emails(html)
    if emails:
        return emails[0]

    time.sleep(1)

    # Fuente 2: Páginas Amarillas España
    query_pa = quote(f"{nombre} {ciudad}")
    url_pa = f"https://www.paginasamarillas.es/search/{query_pa}/all-ma/all-pr/all-is/all-ci/all-ba/all-pu/1"
    html = scrape_url(url_pa)
    emails = extraer_emails(html)
    if emails:
        return emails[0]

    return None


def main():
    if not SCRAPEDO_TOKEN or SCRAPEDO_TOKEN == '***SCRAPEDO_TOKEN_ROTADO***':
        print("Error: reemplaza SCRAPEDO_TOKEN con tu token de scrape.do")
        return

    df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
    sin_email = df[df['Email'].isna() | (df['Email'] == '')].index.tolist()
    print(f"Negocios sin email: {len(sin_email)} de {len(df)} totales.\n")

    for i, idx in enumerate(sin_email):
        nombre = df.at[idx, 'Nombre del negocio']
        ubicacion = df.at[idx, 'Ubicación']

        print(f"[{i+1}/{len(sin_email)}] {nombre}")

        email = buscar_email(nombre, ubicacion)

        if email:
            df.at[idx, 'Email'] = email
            print(f"  → {email}")
        else:
            print(f"  → Sin email encontrado.")

        df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')

        if i < len(sin_email) - 1:
            time.sleep(DELAY_BETWEEN_CALLS)

    encontrados = (df['Email'].notna() & (df['Email'] != '')).sum()
    print(f"\nCompletado: {encontrados}/{len(df)} emails encontrados.")
    print(f"CSV guardado: '{CSV_FILE}'")


if __name__ == '__main__':
    main()
