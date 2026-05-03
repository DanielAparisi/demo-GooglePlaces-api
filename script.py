import requests
import pandas as pd
import json
import os
from datetime import date

API_KEY = '***GOOGLE_KEY_ROTADA***'
USAGE_FILE = 'usage.json'
LIMITE_DIARIO = 10

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

# --- Búsqueda de negocios en Madrid ---

def buscar_negocios(query):
    url = (
        f'https://maps.googleapis.com/maps/api/place/textsearch/json'
        f'?query={query}&key={API_KEY}'
    )
    response = requests.get(url)
    return response.json().get('results', [])

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

busqueda = 'negocios locales Madrid'
print(f"Buscando: {busqueda}")

lugares = buscar_negocios(busqueda)
resultados = []

for lugar in lugares:
    place_id = lugar.get('place_id')
    if not place_id:
        continue

    detalles = obtener_detalles(place_id)

    # Filtrar: solo negocios SIN página web
    if detalles.get('website'):
        continue

    tipos = detalles.get('types', lugar.get('types', []))
    resultados.append({
        'Nombre del negocio': detalles.get('name', lugar.get('name')),
        'Email': '',  # Google Places API no proporciona email
        'Categoría': tipo_a_categoria(tipos),
        'Ubicación': detalles.get('formatted_address', lugar.get('formatted_address')),
        'Teléfono': detalles.get('formatted_phone_number', ''),
    })

df = pd.DataFrame(resultados, columns=['Nombre del negocio', 'Email', 'Categoría', 'Ubicación', 'Teléfono'])
df.to_csv('Leads Google Maps.csv', index=False, encoding='utf-8-sig')

print(f"{len(resultados)} negocios sin web encontrados en Madrid.")
print("Guardados en 'Leads Google Maps.csv'")
