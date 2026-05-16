import os
import re
import json
import time
import argparse
import pandas as pd
from groq import Groq
from instagrapi import Client

# ── Configuración ──────────────────────────────────────────────────────────────

INSTAGRAM_USER     = os.environ.get('IG_USER', 'TU_USUARIO_INSTAGRAM')
INSTAGRAM_PASSWORD = os.environ.get('IG_PASS', 'TU_CONTRASEÑA_INSTAGRAM')
GROQ_API_KEY       = '***GROQ_KEY_ROTADA***'

CSV_FILE     = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Leads Google Maps.csv')
LOG_FILE     = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'instagram_log.json')
SESSION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '.ig_session.json')
DELAY_S      = 15

# ── Groq: generar mensaje personalizado ───────────────────────────────────────

groq = Groq(api_key=GROQ_API_KEY)

def generar_mensaje(nombre, categoria, ubicacion):
    ciudad = ubicacion.split(',')[-2].strip() if ',' in ubicacion else ubicacion

    prompt = f"""Eres un consultor de marketing digital. Escribe un mensaje directo de Instagram corto y profesional en español para contactar a un negocio local que NO tiene página web.

Datos del negocio:
- Nombre: {nombre}
- Categoría: {categoria}
- Ciudad: {ciudad}

Requisitos:
- Tono cercano pero profesional
- Máximo 4 líneas
- Menciona el nombre del negocio y la ciudad
- Ofrece crear una página web moderna con IA a precio asequible
- Termina con una pregunta breve para abrir conversación
- Usa 1 o 2 emojis máximo
- Sin asteriscos ni markdown, solo texto plano
- Firma como: Daniel, Consultor de Presencia Digital"""

    response = groq.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.8,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()

# ── Utilidades ────────────────────────────────────────────────────────────────

def extraer_username(valor):
    """Extrae el username de un handle (@user) o URL de Instagram."""
    valor = valor.strip()
    if not valor:
        return None
    # URL: https://www.instagram.com/username/ o instagram.com/username
    m = re.search(r'instagram\.com/([^/?#\s]+)', valor)
    if m:
        username = m.group(1).strip('/')
        return username if username else None
    # Handle: @username
    if valor.startswith('@'):
        return valor[1:] or None
    # Username directo
    return valor or None

def cargar_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            return json.load(f)
    return {'enviados': [], 'fallidos': []}

def guardar_log(log):
    with open(LOG_FILE, 'w') as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if INSTAGRAM_USER == 'TU_USUARIO_INSTAGRAM':
        print('Error: configura IG_USER e IG_PASS como variables de entorno.')
        print('  export IG_USER="tu_usuario"')
        print('  export IG_PASS="tu_contraseña"')
        return

    parser = argparse.ArgumentParser()
    parser.add_argument('--selected-only', action='store_true')
    args = parser.parse_args()

    df = pd.read_csv(CSV_FILE, encoding='utf-8-sig', dtype=str).fillna('')
    log = cargar_log()
    ya_enviados = {e['username'] for e in log['enviados']}

    pendientes = []
    for _, row in df.iterrows():
        ig_raw = row.get('Instagram', '').strip()
        if not ig_raw:
            continue
        username = extraer_username(ig_raw)
        if not username:
            continue
        if username in ya_enviados:
            continue
        if args.selected_only:
            sel = row.get('selected', '').lower()
            if sel not in ('true', '1', 'yes'):
                continue
        pendientes.append((row, username))

    print(f"Total en CSV:  {len(df)}")
    print(f"Ya enviados:   {len(log['enviados'])}")
    print(f"Pendientes:    {len(pendientes)}\n")

    if not pendientes:
        print('No hay mensajes de Instagram pendientes.')
        return

    print('Generando mensajes con IA (Groq)...')
    mensajes = []
    for row, _ in pendientes:
        msg = generar_mensaje(
            row['Nombre del negocio'],
            row.get('Categoría', 'Negocio local'),
            row.get('Ubicación', ''),
        )
        mensajes.append(msg)
        print('.', end='', flush=True)
    print(' ✓\n')

    cl = Client()
    cl.delay_range = [2, 5]

    if os.path.exists(SESSION_FILE):
        try:
            cl.load_settings(SESSION_FILE)
            cl.login(INSTAGRAM_USER, INSTAGRAM_PASSWORD)
            print('Sesión reutilizada.')
        except Exception:
            print('Sesión caducada, iniciando sesión nueva...')
            cl.login(INSTAGRAM_USER, INSTAGRAM_PASSWORD)
    else:
        print('Iniciando sesión en Instagram...')
        cl.login(INSTAGRAM_USER, INSTAGRAM_PASSWORD)

    cl.dump_settings(SESSION_FILE)
    print('Sesión guardada.\n')

    for i, ((row, username), mensaje) in enumerate(zip(pendientes, mensajes)):
        nombre = row['Nombre del negocio']

        print(f"[{i+1}/{len(pendientes)}] {nombre} → @{username}")
        print(f"  Mensaje: {mensaje[:80]}...")

        try:
            user_id = cl.user_id_from_username(username)
            cl.direct_send(mensaje, [user_id])
            log['enviados'].append({
                'nombre': nombre,
                'username': username,
                'mensaje': mensaje,
                'fecha': pd.Timestamp.now().isoformat(),
            })
            guardar_log(log)
            print('  Enviado')
        except Exception as e:
            log['fallidos'].append({
                'nombre': nombre,
                'username': username,
                'error': str(e),
                'fecha': pd.Timestamp.now().isoformat(),
            })
            guardar_log(log)
            print(f'  Error: {e}')

        if i < len(pendientes) - 1:
            print(f'  Esperando {DELAY_S}s...')
            time.sleep(DELAY_S)

    print(f"\nCompletado. Enviados: {len(log['enviados'])} | Fallidos: {len(log['fallidos'])}")

if __name__ == '__main__':
    main()
