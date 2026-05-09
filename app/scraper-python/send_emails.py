import os
import json
import time
import smtplib
import argparse
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from groq import Groq

# ── Configuración ─────────────────────────────────────────────────────────────

GMAIL_USER     = 'daniel.aparisi.lozano@gmail.com'
GMAIL_PASSWORD = '***GMAIL_APP_PASSWORD_ROTADA***'  # Google App Password (16 caracteres)
GROQ_API_KEY   = '***GROQ_KEY_ROTADA***'

CSV_FILE  = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Leads Google Maps.csv')
LOG_FILE  = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'email_log.json')
DELAY_S   = 10

# ── Groq: generar email personalizado ─────────────────────────────────────────

groq = Groq(api_key=GROQ_API_KEY)

def generar_email(nombre, categoria, ubicacion):
    ciudad = ubicacion.split(',')[-2].strip() if ',' in ubicacion else ubicacion

    prompt = f"""Eres un consultor de marketing digital. Escribe un email profesional en español para contactar a un negocio local que NO tiene página web.

Datos del negocio:
- Nombre: {nombre}
- Categoría: {categoria}
- Ciudad: {ciudad}

Requisitos:
- Asunto atractivo (devuélvelo en la primera línea como "Asunto: ...")
- Cuerpo del email debajo del asunto
- Tono profesional pero cercano
- Máximo 6 líneas en el cuerpo
- Menciona el nombre del negocio y la ciudad
- Ofrece crear una página web moderna con IA a precio asequible
- Menciona que incluye una primera consulta gratuita sin compromiso
- Termina con una pregunta para abrir conversación
- Firma como: Daniel Aparisi, Consultor de Presencia Digital
- Sin asteriscos ni markdown, solo texto plano"""

    response = groq.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.8,
        max_tokens=400,
    )
    return response.choices[0].message.content.strip()

# ── Email ──────────────────────────────────────────────────────────────────────

def parsear_asunto_y_cuerpo(texto):
    lineas = texto.strip().splitlines()
    asunto = 'Mejora tu presencia digital — consulta gratuita'
    cuerpo_inicio = 0
    for i, linea in enumerate(lineas):
        if linea.lower().startswith('asunto:'):
            asunto = linea.split(':', 1)[1].strip()
            cuerpo_inicio = i + 1
            break
    cuerpo = '\n'.join(lineas[cuerpo_inicio:]).strip()
    return asunto, cuerpo

def enviar_email(destinatario, asunto, cuerpo):
    msg = MIMEMultipart()
    msg['From']    = GMAIL_USER
    msg['To']      = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, destinatario, msg.as_string())

# ── Log ────────────────────────────────────────────────────────────────────────

def cargar_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            return json.load(f)
    return {'enviados': [], 'fallidos': []}

def guardar_log(log):
    with open(LOG_FILE, 'w') as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if GMAIL_PASSWORD == 'TU_APP_PASSWORD_AQUI':
        print('Error: configura GMAIL_PASSWORD con tu Google App Password.')
        print('Instrucciones: myaccount.google.com → Seguridad → Contraseñas de aplicación')
        return

    parser = argparse.ArgumentParser()
    parser.add_argument('--selected-only', action='store_true')
    args = parser.parse_args()

    df = pd.read_csv(CSV_FILE, encoding='utf-8-sig', dtype=str).fillna('')
    log = cargar_log()
    ya_enviados = {e['email'] for e in log['enviados']}

    pendientes = []
    for _, row in df.iterrows():
        email = row.get('Email', '').strip()
        if not email:
            continue
        if email in ya_enviados:
            continue
        if args.selected_only:
            sel = row.get('selected', '').lower()
            if sel not in ('true', '1', 'yes'):
                continue
        pendientes.append(row)

    print(f"Total en CSV:  {len(df)}")
    print(f"Ya enviados:   {len(log['enviados'])}")
    print(f"Pendientes:    {len(pendientes)}\n")

    if not pendientes:
        print('No hay emails pendientes.')
        return

    print('Generando emails con IA (Groq)...')
    emails_generados = []
    for row in pendientes:
        texto = generar_email(
            row['Nombre del negocio'],
            row.get('Categoría', 'Negocio local'),
            row.get('Ubicación', ''),
        )
        asunto, cuerpo = parsear_asunto_y_cuerpo(texto)
        emails_generados.append((asunto, cuerpo))
        print('.', end='', flush=True)
    print(' ✓\n')

    for i, (row, (asunto, cuerpo)) in enumerate(zip(pendientes, emails_generados)):
        nombre = row['Nombre del negocio']
        email  = row['Email'].strip()

        print(f"[{i+1}/{len(pendientes)}] {nombre} → {email}")
        print(f"  Asunto: {asunto}")
        print(f"  Cuerpo: {cuerpo[:80]}...")

        try:
            enviar_email(email, asunto, cuerpo)
            log['enviados'].append({
                'nombre': nombre,
                'email': email,
                'asunto': asunto,
                'fecha': pd.Timestamp.now().isoformat(),
            })
            guardar_log(log)
            print('  Enviado')
        except Exception as e:
            log['fallidos'].append({
                'nombre': nombre,
                'email': email,
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
