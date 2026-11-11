"""Busca negocios sin web en Google Places y los añade al CSV de leads.

    python script.py          → búsqueda nueva (cuenta para el límite diario) y revisa todos sus resultados
    python script.py --cola   → solo revisa los negocios que quedaron en cola (no cuenta para el límite)

Si la API falla a mitad, se guarda lo encontrado hasta ese momento y el resto queda
en cola para `--cola`.
"""
import argparse
import json
import random
import sys
import time
from datetime import date

import requests

from comun import leads_csv
from comun.dominio import tipo_telefono
from comun.oportunidad import cargar_pesos, necesita_web, puntuar
from comun.ficheros import guardar_json
from comun import rutas
from config import requerir

LIMITE_DIARIO = 10
URL_TEXTSEARCH = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
URL_DETALLES = 'https://maps.googleapis.com/maps/api/place/details/json'
# business_status, opening_hours y photos no encarecen la petición: ya se pagan los campos
# de contacto y atmósfera. Alimentan la puntuación de oportunidad (comun/oportunidad.py).
CAMPOS_DETALLE = ('name,formatted_address,rating,user_ratings_total,website,formatted_phone_number,'
                  'business_status,opening_hours,photos')
COLUMNAS = ['Nombre del negocio', 'Email', 'Categoría', 'Ubicación', 'Teléfono', 'Tipo teléfono',
            'Web actual', 'Reseñas', 'Valoración', 'Horario', 'Fotos', 'Estado negocio']

# Búsqueda en Google Maps → categoría con la que se guarda el lead. Google suele
# devolver tipos genéricos ("establishment"), así que el sector buscado es más fiable.
TIPOS_NEGOCIO = {
    'empresa de reformas': 'Reformas',         # ticket muy alto, muchos autónomos sin web
    'taller mecánico':     'Taller mecánico',  # clientes recurrentes y mucha búsqueda local
    'fisioterapia':        'Fisioterapia',     # la reserva online es un argumento de venta claro
}

# Peso de cada sector al elegir la búsqueda: talleres y fisios dan más negocios sin web
# (hoy: 5 y 3 leads en 2 búsquedas cada uno; reformas, 1 en 5), así que salen el doble.
PESOS = {
    'empresa de reformas': 1,
    'taller mecánico':     2,
    'fisioterapia':        2,
}

CIUDADES = [
    'Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Zaragoza',
    'Málaga', 'Murcia', 'Palma', 'Bilbao', 'Alicante',
    'Córdoba', 'Valladolid', 'Vigo', 'Gijón', 'Granada',
    'Elche', 'Oviedo', 'Badalona', 'Cartagena', 'Terrassa',
    'Sabadell', 'Jerez', 'Móstoles', 'Almería', 'Fuenlabrada',
    'Hospitalet', 'Santander', 'Burgos', 'Albacete', 'Getafe',
]


class PlacesError(Exception):
    """La API de Places ha rechazado la petición (clave, cuota, petición inválida...)."""


# ── Límite diario y estado ────────────────────────────────────────────────────

def _leer_json(ruta, por_defecto):
    return json.loads(ruta.read_text()) if ruta.exists() else por_defecto


def consumir_busqueda_diaria(ruta=None, hoy=None):
    """Cuenta una búsqueda. Devuelve False si ya se alcanzó el límite del día."""
    ruta = ruta or rutas.USAGE_FILE
    hoy = str(hoy or date.today())
    uso = _leer_json(ruta, {'fecha': '', 'contador': 0})
    if uso['fecha'] != hoy:
        uso = {'fecha': hoy, 'contador': 0}
    if uso['contador'] >= LIMITE_DIARIO:
        print(f"Límite diario de {LIMITE_DIARIO} búsquedas alcanzado. Vuelve mañana.")
        return False
    uso['contador'] += 1
    guardar_json(ruta, uso)
    print(f"Búsqueda {uso['contador']}/{LIMITE_DIARIO} del día.")
    return True


def cargar_estado(ruta=None):
    ruta = ruta or rutas.SEARCH_STATE_FILE
    estado = _leer_json(ruta, {})
    estado.setdefault('place_ids_pendientes', [])
    estado.setdefault('tipo', None)
    estado.setdefault('hechas', [])
    return estado


def elegir_busqueda(estado, rng=random):
    """Sector (según PESOS) + ciudad al azar que no se haya buscado ya; si se agotan, vuelve a empezar."""
    combinaciones = [(t, c) for t in TIPOS_NEGOCIO for c in CIUDADES]
    libres = [tc for tc in combinaciones if f'{tc[0]} en {tc[1]}' not in estado['hechas']]
    if not libres:
        estado['hechas'] = []
        libres = combinaciones
    return rng.choices(libres, weights=[PESOS[t] for t, _ in libres])[0]


# ── API de Google Places ──────────────────────────────────────────────────────

def _llamar(url, params):
    data = requests.get(url, params=params, timeout=30).json()
    status = data.get('status', 'UNKNOWN_ERROR')
    if status in ('OK', 'ZERO_RESULTS'):
        return data
    if status == 'NOT_FOUND':  # el negocio ya no existe en Maps
        return None
    raise PlacesError(f"{status}: {data.get('error_message', 'sin detalle')}")


def buscar(query, api_key):
    data = _llamar(URL_TEXTSEARCH, {'query': query, 'key': api_key})
    return [l['place_id'] for l in (data or {}).get('results', []) if l.get('place_id')]


def obtener_detalles(place_id, api_key):
    data = _llamar(URL_DETALLES, {'place_id': place_id, 'fields': CAMPOS_DETALLE, 'key': api_key})
    return (data or {}).get('result') or None


def fila_lead(detalles, categoria):
    """Lead para el CSV, o None si el negocio ya tiene web propia, está cerrado o le faltan datos.

    Una "web" que es solo Facebook, Instagram, un directorio o un enlace corto no cuenta
    como web: ese negocio sigue necesitando una y entra como lead.
    """
    if not detalles.get('name') or not necesita_web(detalles.get('website')):
        return None
    telefono = detalles.get('formatted_phone_number', '')
    fila = {
        'Nombre del negocio': detalles['name'],
        'Email': '',
        'Categoría': categoria,
        'Ubicación': detalles.get('formatted_address', ''),
        'Teléfono': telefono,
        'Tipo teléfono': tipo_telefono(telefono),
        'Web actual': detalles.get('website', ''),
        # Places omite los campos sin datos: sin reseñas = 0 reseñas, no "desconocido"
        'Reseñas': str(detalles.get('user_ratings_total', 0)),
        'Valoración': str(detalles.get('rating', '')),
        'Horario': str(bool(detalles.get('opening_hours'))),
        'Fotos': str(len(detalles.get('photos') or [])),
        'Estado negocio': detalles.get('business_status', ''),
    }
    if fila['Estado negocio'] in ('CLOSED_PERMANENTLY', 'CLOSED_TEMPORARILY'):
        return None
    return fila


def revisar(place_ids, categoria, api_key, pausa=0.0):
    """Devuelve (leads sin web, place_ids que quedaron sin revisar por un error)."""
    resultados = []
    for i, place_id in enumerate(place_ids):
        try:
            detalles = obtener_detalles(place_id, api_key)
        except (PlacesError, requests.RequestException) as e:
            print(f"⚠ Error de la API de Places: {e}. Lo que falta queda en cola (usa --cola).")
            return resultados, place_ids[i:]
        if detalles and (fila := fila_lead(detalles, categoria)):
            resultados.append(fila)
        time.sleep(pausa)
    return resultados, []


# ── Main ──────────────────────────────────────────────────────────────────────

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--cola', action='store_true', help='revisar solo los negocios pendientes de la última búsqueda')
    args = parser.parse_args(argv)

    api_key = requerir('GOOGLE_PLACES_API_KEY')
    estado = cargar_estado()

    if args.cola:
        if not estado['place_ids_pendientes'] or not estado['tipo']:
            print("No hay negocios en cola.")
            return 0
        print(f"Revisando la cola de '{estado.get('busqueda', estado['tipo'])}'")
    else:
        if not consumir_busqueda_diaria():
            return 0
        tipo, ciudad = elegir_busqueda(estado)
        busqueda = f'{tipo} en {ciudad}'
        print(f"Búsqueda: '{busqueda}'")
        try:
            place_ids = buscar(busqueda, api_key)
        except (PlacesError, requests.RequestException) as e:
            # No se marca como hecha: se podrá repetir cuando la API responda.
            print(f"⚠ La búsqueda ha fallado: {e}")
            return 1
        print(f"  → {len(place_ids)} ubicaciones encontradas.")
        # Lo que quedara en cola de una búsqueda anterior se descarta: su sector puede ser otro.
        estado.update(place_ids_pendientes=place_ids, tipo=tipo, busqueda=busqueda)
        estado['hechas'].append(busqueda)
        guardar_json(rutas.SEARCH_STATE_FILE, estado)

    lote = estado['place_ids_pendientes']
    categoria = TIPOS_NEGOCIO.get(estado['tipo'], estado['tipo'])
    print(f"Revisando {len(lote)} ubicaciones...")

    resultados, sin_revisar = revisar(lote, categoria, api_key)
    nuevos = leads_csv.anadir(resultados, COLUMNAS)

    # La cola solo se recorta cuando lo revisado ya está guardado en el CSV
    estado['place_ids_pendientes'] = sin_revisar
    guardar_json(rutas.SEARCH_STATE_FILE, estado)

    print(f"{len(resultados)} negocios sin web encontrados, {nuevos} nuevos (el resto ya estaban).")
    # La puntuación no se guarda: el panel la recalcula con lo que añada el enriquecido.
    pesos = cargar_pesos(rutas.PESOS_FILE)
    for puntos, nombre in sorted(((puntuar(r, pesos)['puntuacion'], r['Nombre del negocio']) for r in resultados),
                                 reverse=True)[:5]:
        print(f"  ★ {puntos:>3}/100  {nombre}")
    print(f"Total acumulado en '{rutas.CSV_FILE.name}': {len(leads_csv.leer())} negocios.")
    fijos = [r['Nombre del negocio'] for r in resultados if r['Tipo teléfono'] == 'Fijo']
    if fijos:
        print(f"📞 {len(fijos)} con teléfono fijo (sin WhatsApp): están en 'Por llamar' del panel → {', '.join(fijos)}")
    return 1 if sin_revisar else 0


if __name__ == '__main__':
    sys.exit(main())
