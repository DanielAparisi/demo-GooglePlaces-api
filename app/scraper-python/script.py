import requests
import pandas as pd
import json
import os
import time
import random
import sys
from datetime import date

_DIR    = os.path.dirname(os.path.abspath(__file__))
_ROOT   = os.path.abspath(os.path.join(_DIR, '..', '..'))

from config import requerir, tipo_telefono

API_KEY    = requerir('GOOGLE_PLACES_API_KEY')
USAGE_FILE = os.path.join(_DIR, 'usage.json')
STATE_FILE = os.path.join(_DIR, 'search_state.json')
CSV_FILE   = os.path.join(_ROOT, 'Leads Google Maps.csv')
LIMITE_DIARIO = 10

# Búsqueda en Google Maps → categoría con la que se guarda el lead. Google suele
# devolver tipos genéricos ("establishment"), así que el sector buscado es más fiable.
_TIPOS_NEGOCIO = {
    'empresa de reformas': 'Reformas',         # ticket muy alto, muchos autónomos sin web
    'taller mecánico':     'Taller mecánico',  # clientes recurrentes y mucha búsqueda local
    'fisioterapia':        'Fisioterapia',     # la reserva online es un argumento de venta claro
}

# Peso de cada sector al elegir la búsqueda: talleres y fisios dan más negocios sin web
# (hoy: 5 y 3 leads en 2 búsquedas cada uno; reformas, 1 en 5), así que salen el doble.
_PESOS = {
    'empresa de reformas': 1,
    'taller mecánico':     2,
    'fisioterapia':        2,
}

_CIUDADES_ESPAÑA = [
    'Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Zaragoza',
    'Málaga', 'Murcia', 'Palma', 'Bilbao', 'Alicante',
    'Córdoba', 'Valladolid', 'Vigo', 'Gijón', 'Granada',
    'Elche', 'Oviedo', 'Badalona', 'Cartagena', 'Terrassa',
    'Sabadell', 'Jerez', 'Móstoles', 'Almería', 'Fuenlabrada',
    'Hospitalet', 'Santander', 'Burgos', 'Albacete', 'Getafe',
]


# --- Control de límite diario ---

def cargar_uso():
    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, 'r') as f:
            return json.load(f)
    return {'fecha': '', 'contador': 0}

def guardar_uso(uso):
    with open(USAGE_FILE, 'w') as f:
        json.dump(uso, f)

def verificar_limite():
    uso = cargar_uso()
    hoy = str(date.today())
    if uso['fecha'] != hoy:
        uso = {'fecha': hoy, 'contador': 0}
    if uso['contador'] >= LIMITE_DIARIO:
        print(f"Límite diario de {LIMITE_DIARIO} búsquedas alcanzado. Vuelve mañana.")
        return None
    uso['contador'] += 1
    guardar_uso(uso)
    print(f"Búsqueda {uso['contador']}/{LIMITE_DIARIO} del día.")
    return uso

# --- Estado: cola de negocios por revisar y búsquedas ya hechas ---

def cargar_estado():
    estado = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            estado = json.load(f)
    estado.setdefault('place_ids_pendientes', [])
    estado.setdefault('tipo', None)
    estado.setdefault('hechas', [])
    return estado

def guardar_estado(estado):
    with open(STATE_FILE, 'w') as f:
        json.dump(estado, f)

def elegir_busqueda(estado):
    """Sector (según _PESOS) + ciudad al azar que no se haya buscado ya; si se agotan, vuelve a empezar."""
    combinaciones = [(t, c) for t in _TIPOS_NEGOCIO for c in _CIUDADES_ESPAÑA]
    libres = [tc for tc in combinaciones if f'{tc[0]} en {tc[1]}' not in estado['hechas']]
    if not libres:
        estado['hechas'] = []
        libres = combinaciones
    return random.choices(libres, weights=[_PESOS[t] for t, _ in libres])[0]

# --- API de Google Places ---

def buscar_pagina(query=None, page_token=None):
    if page_token:
        # Google requiere ~2s de espera antes de usar el token de siguiente página
        time.sleep(2)
        params = {'pagetoken': page_token, 'key': API_KEY}
    else:
        params = {'query': query, 'key': API_KEY}
    response = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json', params=params, timeout=30)
    data = response.json()
    return data.get('results', []), data.get('next_page_token')

def obtener_detalles(place_id):
    fields = 'name,formatted_address,rating,user_ratings_total,website,formatted_phone_number'
    response = requests.get(
        'https://maps.googleapis.com/maps/api/place/details/json',
        params={'place_id': place_id, 'fields': fields, 'key': API_KEY},
        timeout=30,
    )
    return response.json().get('result', {})

# --- Main ---
#   python script.py          → búsqueda nueva (cuenta para el límite diario) y revisa todos sus resultados
#   python script.py --cola   → solo revisa los negocios que quedaron en cola (no cuenta para el límite)

estado = cargar_estado()

if '--cola' in sys.argv:
    if not estado['place_ids_pendientes'] or not estado['tipo']:
        print("No hay negocios en cola.")
        sys.exit()
    print(f"Revisando la cola de '{estado.get('busqueda', estado['tipo'])}'")
else:
    if verificar_limite() is None:
        sys.exit()
    tipo, ciudad = elegir_busqueda(estado)
    busqueda = f'{tipo} en {ciudad}'
    print(f"Búsqueda: '{busqueda}'")
    lugares, _ = buscar_pagina(query=busqueda)
    place_ids = [l['place_id'] for l in lugares if l.get('place_id')]
    print(f"  → {len(place_ids)} ubicaciones encontradas.")
    # Lo que quedara en cola de una búsqueda anterior se descarta: su sector puede ser otro.
    estado.update(place_ids_pendientes=place_ids, tipo=tipo, busqueda=busqueda)
    estado['hechas'].append(busqueda)
    guardar_estado(estado)

lote = estado['place_ids_pendientes']
categoria = _TIPOS_NEGOCIO.get(estado['tipo'], estado['tipo'])
print(f"Revisando {len(lote)} ubicaciones...")

resultados = []
for place_id in lote:
    detalles = obtener_detalles(place_id)

    # Filtrar: solo negocios SIN página web
    if detalles.get('website'):
        continue

    resultados.append({
        'Nombre del negocio': detalles.get('name', ''),
        'Email': '',
        'Categoría': categoria,
        'Ubicación': detalles.get('formatted_address', ''),
        'Teléfono': detalles.get('formatted_phone_number', ''),
        'Tipo teléfono': tipo_telefono(detalles.get('formatted_phone_number', '')),
    })

# --- Guardar acumulando en CSV ---

columnas = ['Nombre del negocio', 'Email', 'Categoría', 'Ubicación', 'Teléfono', 'Tipo teléfono']
df_nuevo = pd.DataFrame(resultados, columns=columnas)

if os.path.exists(CSV_FILE):
    df_existente = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
    antes = len(df_existente)
    df_total = pd.concat([df_existente, df_nuevo], ignore_index=True)
    df_total = df_total.drop_duplicates(subset=['Nombre del negocio', 'Ubicación'])
else:
    antes = 0
    df_total = df_nuevo

df_total.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')

# La cola se vacía solo cuando los resultados ya están guardados en el CSV
estado['place_ids_pendientes'] = []
guardar_estado(estado)

print(f"{len(resultados)} negocios sin web encontrados, {len(df_total) - antes} nuevos (el resto ya estaban).")
print(f"Total acumulado en '{CSV_FILE}': {len(df_total)} negocios.")

fijos = [r['Nombre del negocio'] for r in resultados if r['Tipo teléfono'] == 'Fijo']
if fijos:
    print(f"📞 {len(fijos)} con teléfono fijo (sin WhatsApp): están en 'Por llamar' del panel → {', '.join(fijos)}")
