"""Enriquece los leads del CSV con email y redes sociales buscándolos vía scrape.do.

    python enrich_emails.py                  → todos los no enriquecidos
    python enrich_emails.py --solo-sectores  → solo talleres, fisioterapia y reformas (ahorra créditos)

Cada lead se guarda en cuanto se procesa, releyendo el CSV con bloqueo: se puede usar
el panel mientras corre. Si scrape.do se queda sin créditos, se para sin marcar como
enriquecidos los leads que no se han podido buscar.
"""
import argparse
import re
import sys
import time
import unicodedata
from urllib.parse import quote

import requests

from comun import leads_csv
from comun.dominio import ciudad_de, sector_de
from config import requerir

DELAY_ENTRE_LEADS = 3
DELAY_ENTRE_PETICIONES = 1
COLUMNAS_REDES = ['Facebook', 'Instagram', 'LinkedIn', 'Twitter', 'TikTok', 'YouTube']

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')

# (patrón, plantilla). El último grupo es el identificador de la cuenta; los anteriores
# forman parte de la URL (p. ej. LinkedIn company/in, YouTube channel/c/@).
REDES = {
    'Facebook':  (re.compile(r'https?://(?:www\.|m\.)?facebook\.com/(?!sharer|share|dialog|pages/create)([A-Za-z0-9._\-]{3,})', re.I),
                  'https://facebook.com/{}'),
    'Instagram': (re.compile(r'https?://(?:www\.)?instagram\.com/([A-Za-z0-9._]{1,30})(?:[/?#"\'\s]|$)', re.I),
                  'https://instagram.com/{}'),
    'LinkedIn':  (re.compile(r'https?://(?:[a-z]{2,3}\.)?linkedin\.com/(company|in)/([A-Za-z0-9._\-]+)', re.I),
                  'https://linkedin.com/{}/{}'),
    'Twitter':   (re.compile(r'https?://(?:www\.)?(?:twitter|x)\.com/(?!share|intent|home)([A-Za-z0-9_]{1,15})(?:[/?#"\'\s]|$)', re.I),
                  'https://x.com/{}'),
    'TikTok':    (re.compile(r'https?://(?:www\.)?tiktok\.com/@([A-Za-z0-9._]{1,24})(?:[/?#"\'\s]|$)', re.I),
                  'https://tiktok.com/@{}'),
    'YouTube':   (re.compile(r'https?://(?:www\.)?youtube\.com/(channel/|c/|@)([A-Za-z0-9._\-]+)', re.I),
                  'https://youtube.com/{}{}'),
}

DOMINIOS_EXCLUIDOS_EMAIL = {
    'sentry.io', 'wixpress.com', 'example.com', 'domain.com',
    'email.com', 'correo.com', 'tuempresa.com', 'empresa.com',
    'google.com', 'googleapis.com', 'gstatic.com', 'w3.org',
    'schema.org', 'facebook.com', 'twitter.com', 'instagram.com',
    'youtube.com', 'linkedin.com', 'whatsapp.com',
}
EXTENSIONES_NO_EMAIL = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.js', '.css')

SLUGS_IGNORADOS = {
    'hashtag', 'explore', 'events', 'pages', 'groups', 'marketplace',
    'watch', 'gaming', 'home', 'profile', 'login', 'signup', 'about',
    'help', 'legal', 'privacy', 'terms', 'search', 'reel', 'reels',
    'stories', 'notifications', 'messages', 'p', 'tv',
}

# Palabras del nombre que no sirven para identificar al negocio
PALABRAS_GENERICAS = {
    'taller', 'talleres', 'mecanico', 'mecanica', 'reformas', 'reforma', 'clinica', 'centro',
    'fisioterapia', 'fisio', 'servicios', 'empresa', 'grupo', 'hermanos', 'rehabilitaciones',
    'autoservicio', 'lavanderia', 'restaurante', 'para', 'sport', 'auto', 'autos',
}


class ScrapeDoAgotado(Exception):
    """scrape.do rechaza el token (sin créditos, token inválido o límite de concurrencia)."""


# ── Extracción ────────────────────────────────────────────────────────────────

def extraer_emails(html):
    if not html:
        return []
    vistos, limpios = set(), []
    for email in EMAIL_REGEX.findall(html):
        email = email.lower().rstrip('.')
        dominio = email.split('@')[-1]
        # "logo@2x.png" encaja con la regex pero no es un email
        if dominio in DOMINIOS_EXCLUIDOS_EMAIL or email.endswith(EXTENSIONES_NO_EMAIL) or email in vistos:
            continue
        vistos.add(email)
        limpios.append(email)
    return limpios


def extraer_redes(html):
    """Primera cuenta válida de cada red encontrada en el HTML → URL normalizada."""
    if not html:
        return {}
    resultados = {}
    for red, (patron, plantilla) in REDES.items():
        for m in patron.finditer(html):
            *prefijo, slug = m.groups()
            slug = slug.strip('/')
            if slug.lower() in SLUGS_IGNORADOS or len(slug) < 3:
                continue
            # Los IDs de canal de YouTube distinguen mayúsculas; el resto de handles no.
            if not (red == 'YouTube' and prefijo[0].lower() == 'channel/'):
                slug = slug.lower()
            resultados[red] = plantilla.format(*(p.lower() for p in prefijo), slug)
            break
    return resultados


def _normalizar(texto):
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]', '', texto)


def es_del_negocio(nombre, texto):
    """El email/red solo se acepta si contiene alguna palabra distintiva del nombre del negocio.
    Sin esto se cuelan emails de cualquier web que salga en los resultados de Google."""
    nombre = nombre.split(' - ')[0]
    palabras = {_normalizar(p) for p in re.split(r'[\s.,&/\-]+', nombre)}
    distintivas = {p for p in palabras if len(p) >= 4 and p not in PALABRAS_GENERICAS}
    objetivo = _normalizar(texto)
    return any(p in objetivo for p in distintivas)


# ── Búsqueda ──────────────────────────────────────────────────────────────────

class ScrapeDo:
    def __init__(self, token, pausa=DELAY_ENTRE_PETICIONES):
        self.token = token
        self.pausa = pausa

    def get(self, url):
        """HTML de la página, o None si esa página concreta falla."""
        api_url = f"https://api.scrape.do?token={self.token}&url={quote(url, safe='')}&render=false"
        try:
            resp = requests.get(api_url, timeout=30)
        except requests.RequestException as e:
            print(f"  Error de red con scrape.do: {e}")
            return None
        finally:
            time.sleep(self.pausa)
        if resp.status_code in (401, 403, 429):
            raise ScrapeDoAgotado(f'scrape.do respondió {resp.status_code}: {resp.text[:120]}')
        if resp.status_code != 200:
            print(f"  scrape.do {resp.status_code} para {url[:80]}")
            return None
        return resp.text


def urls_de_busqueda(nombre, ciudad):
    consultas = [
        f'"{nombre}" "{ciudad}" site:facebook.com OR site:instagram.com OR site:linkedin.com OR site:tiktok.com',
        f'"{nombre}" "{ciudad}" correo electrónico OR email OR contacto',
        f'"{nombre}" "{ciudad}"',
    ]
    urls = [f"https://www.google.es/search?q={quote(q)}&hl=es&num=10" for q in consultas]
    urls.append(
        f"https://www.paginasamarillas.es/search/{quote(nombre + ' ' + ciudad)}/all-ma/all-pr/all-is/all-ci/all-ba/all-pu/1"
    )
    return urls


def buscar_info(nombre, ubicacion, scraper):
    """Devuelve (email, redes, páginas obtenidas). Para en cuanto tiene email y 3 redes."""
    email, redes, obtenidas = None, {}, 0
    for url in urls_de_busqueda(nombre, ciudad_de(ubicacion)):
        if email and len(redes) >= 3:
            break
        html = scraper.get(url)
        if html is None:
            continue
        obtenidas += 1
        if not email:
            email = next((e for e in extraer_emails(html) if es_del_negocio(nombre, e)), None)
        for red, enlace in extraer_redes(html).items():
            if red not in redes and es_del_negocio(nombre, enlace):
                redes[red] = enlace
    return email, redes, obtenidas


# ── Guardado ──────────────────────────────────────────────────────────────────

def guardar_resultado(nombre, ubicacion, pista, email, redes, csv=None):
    """Rellena solo los campos vacíos del lead y lo marca como enriquecido.
    Devuelve los campos que se han escrito (vacío si el lead ya no está en el CSV)."""
    escritos = {}
    with leads_csv.editar(csv) as df:
        for col in ['Email', 'enriched'] + COLUMNAS_REDES:
            if col not in df.columns:
                df[col] = ''
        idx = leads_csv.localizar(df, nombre, ubicacion, pista)
        if idx is None:
            return escritos
        for col, valor in [('Email', email), *redes.items()]:
            if valor and not df.at[idx, col]:
                df.at[idx, col] = escritos[col] = valor
        df.at[idx, 'enriched'] = 'True'
    return escritos


def pendientes(df, solo_sectores=False):
    filas = df[df['enriched'] != 'True'] if 'enriched' in df.columns else df
    if solo_sectores:
        filas = filas[[bool(sector_de(r)) for r in filas.to_dict('records')]]
    return [(int(i), r['Nombre del negocio'], r['Ubicación']) for i, r in filas.iterrows()]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--solo-sectores', action='store_true',
                        help='solo talleres, fisioterapia y reformas (ahorra créditos de scrape.do)')
    args = parser.parse_args(argv)

    scraper = ScrapeDo(requerir('SCRAPEDO_TOKEN'))
    df = leads_csv.leer()
    cola = pendientes(df, args.solo_sectores)
    print(f"Negocios a enriquecer: {len(cola)} de {len(df)} totales.\n")

    for i, (idx, nombre, ubicacion) in enumerate(cola):
        print(f"[{i+1}/{len(cola)}] {nombre}")
        try:
            email, redes, obtenidas = buscar_info(nombre, ubicacion, scraper)
        except ScrapeDoAgotado as e:
            print(f"\n⛔ {e}\nParo aquí: los {len(cola) - i} leads restantes siguen pendientes.")
            return 1

        if obtenidas == 0:
            print("  → Ninguna página respondió; se reintentará en la próxima ejecución.")
            continue

        escritos = guardar_resultado(nombre, ubicacion, idx, email, redes)
        for col, valor in escritos.items():
            print(f"  {col:<10} → {valor}")
        if not escritos:
            print("  → Sin datos nuevos.")

        if i < len(cola) - 1:
            time.sleep(DELAY_ENTRE_LEADS)

    final = leads_csv.leer()
    print("\nCompletado:")
    for col in ['Email'] + COLUMNAS_REDES:
        if col in final.columns and (n := int((final[col] != '').sum())):
            print(f"  {col}: {n}/{len(final)}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
