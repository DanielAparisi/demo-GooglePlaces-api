import requests
import pandas as pd
import json
import os
import time
import random
from datetime import date

_DIR    = os.path.dirname(os.path.abspath(__file__))
_ROOT   = os.path.abspath(os.path.join(_DIR, '..', '..'))

API_KEY    = '***GOOGLE_KEY_ROTADA***'
USAGE_FILE = os.path.join(_DIR, 'usage.json')
STATE_FILE = os.path.join(_DIR, 'search_state.json')
CSV_FILE   = os.path.join(_ROOT, 'Leads Google Maps.csv')
LIMITE_DIARIO = 10
MAX_POR_LLAMADA = 10

_TIPOS_NEGOCIO = [
    'restaurante', 'cafetería', 'bar', 'panadería', 'peluquería',
    'tienda de ropa', 'gimnasio', 'farmacia', 'dentista', 'fontanero',
    'electricista', 'taller de coches', 'inmobiliaria', 'veterinario',
    'floristería', 'zapatería', 'ferretería', 'librería', 'spa',
    'agencia de viajes', 'supermercado', 'lavandería', 'joyería',
]

_CIUDADES_ESPAÑA = [
    'Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Zaragoza',
    'Málaga', 'Murcia', 'Palma', 'Bilbao', 'Alicante',
    'Córdoba', 'Valladolid', 'Vigo', 'Gijón', 'Granada',
    'Elche', 'Oviedo', 'Badalona', 'Cartagena', 'Terrassa',
    'Sabadell', 'Jerez', 'Móstoles', 'Almería', 'Fuenlabrada',
    'Hospitalet', 'Santander', 'Burgos', 'Albacete', 'Getafe',
]

BUSQUEDA = f'{random.choice(_TIPOS_NEGOCIO)} en {random.choice(_CIUDADES_ESPAÑA)}'

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

# --- Estado de paginación ---

def cargar_estado():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {'place_ids_pendientes': [], 'next_page_token': None, 'pagina': 0}

def guardar_estado(estado):
    with open(STATE_FILE, 'w') as f:
        json.dump(estado, f)

def resetear_estado():
    guardar_estado({'place_ids_pendientes': [], 'next_page_token': None, 'pagina': 0})

# --- API de Google Places ---

def buscar_pagina(query=None, page_token=None):
    if page_token:
        # Google requiere ~2s de espera antes de usar el token de siguiente página
        time.sleep(2)
        url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?pagetoken={page_token}&key={API_KEY}'
    else:
        url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={API_KEY}'
    response = requests.get(url)
    data = response.json()
    return data.get('results', []), data.get('next_page_token')

CATEGORIAS_ES = {
    'restaurant': 'Restaurante',
    'food': 'Alimentación',
    'cafe': 'Cafetería',
    'bar': 'Bar',
    'bakery': 'Panadería',
    'beauty_salon': 'Salón de belleza',
    'hair_care': 'Peluquería',
    'clothing_store': 'Tienda de ropa',
    'shoe_store': 'Zapatería',
    'store': 'Tienda',
    'supermarket': 'Supermercado',
    'gym': 'Gimnasio',
    'laundry': 'Lavandería',
    'lodging': 'Alojamiento',
    'real_estate_agency': 'Inmobiliaria',
    'travel_agency': 'Agencia de viajes',
    'car_repair': 'Taller de coches',
    'electrician': 'Electricista',
    'plumber': 'Fontanero',
    'painter': 'Pintor',
    'general_contractor': 'Contratista',
    'accounting': 'Contabilidad',
    'lawyer': 'Abogado',
    'doctor': 'Médico',
    'dentist': 'Dentista',
    'pharmacy': 'Farmacia',
    'veterinary_care': 'Veterinario',
    'florist': 'Floristería',
    'jewelry_store': 'Joyería',
    'furniture_store': 'Mueblería',
    'hardware_store': 'Ferretería',
    'pet_store': 'Tienda de mascotas',
    'electronics_store': 'Electrónica',
    'book_store': 'Librería',
    'school': 'Escuela',
    'church': 'Iglesia',
    'night_club': 'Discoteca',
    'spa': 'Spa',
    'establishment': 'Negocio',
}

def tipo_a_categoria(types):
    for t in (types or []):
        if t in CATEGORIAS_ES:
            return CATEGORIAS_ES[t]
    return 'Otro'

def obtener_detalles(place_id):
    fields = 'name,formatted_address,rating,user_ratings_total,website,formatted_phone_number,types'
    url = (
        f'https://maps.googleapis.com/maps/api/place/details/json'
        f'?place_id={place_id}&fields={fields}&key={API_KEY}'
    )
    response = requests.get(url)
    return response.json().get('result', {})

# --- Main ---

uso = verificar_limite()
if uso is None:
    exit()

print(f"Búsqueda aleatoria: '{BUSQUEDA}'")

# Cada ejecución arranca con una búsqueda nueva y distinta
resetear_estado()
estado = cargar_estado()

print(f"Obteniendo resultados para: {BUSQUEDA}")
lugares, _ = buscar_pagina(query=BUSQUEDA)
place_ids = [l['place_id'] for l in lugares if l.get('place_id')]
estado['place_ids_pendientes'] = place_ids
guardar_estado(estado)
print(f"  → {len(place_ids)} ubicaciones encontradas.")

# Tomar hasta MAX_POR_LLAMADA place_ids del estado
lote = estado['place_ids_pendientes'][:MAX_POR_LLAMADA]
estado['place_ids_pendientes'] = estado['place_ids_pendientes'][MAX_POR_LLAMADA:]
guardar_estado(estado)

print(f"Procesando {len(lote)} ubicaciones (quedan {len(estado['place_ids_pendientes'])} en cola)...")

resultados = []
for place_id in lote:
    detalles = obtener_detalles(place_id)

    # Filtrar: solo negocios SIN página web
    if detalles.get('website'):
        continue

    tipos = detalles.get('types', [])
    resultados.append({
        'Nombre del negocio': detalles.get('name', ''),
        'Email': '',
        'Categoría': tipo_a_categoria(tipos),
        'Ubicación': detalles.get('formatted_address', ''),
        'Teléfono': detalles.get('formatted_phone_number', ''),
    })

# --- Guardar acumulando en CSV ---

columnas = ['Nombre del negocio', 'Email', 'Categoría', 'Ubicación', 'Teléfono']
df_nuevo = pd.DataFrame(resultados, columns=columnas)

if os.path.exists(CSV_FILE):
    df_existente = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
    df_total = pd.concat([df_existente, df_nuevo], ignore_index=True)
    df_total = df_total.drop_duplicates(subset=['Nombre del negocio', 'Ubicación'])
else:
    df_total = df_nuevo

df_total.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')

print(f"{len(resultados)} negocios sin web añadidos.")
print(f"Total acumulado en '{CSV_FILE}': {len(df_total)} negocios.")
