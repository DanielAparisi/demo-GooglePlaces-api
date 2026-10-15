import json
import os
import re
import subprocess
from datetime import date

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List

import contacto

app = FastAPI()

# Solo el frontend local puede llamar a la API: estos endpoints lanzan envíos
# reales de WhatsApp/email, así que nunca deben quedar abiertos a cualquier origen.
ALLOWED_ORIGINS = ["http://localhost:4321", "http://127.0.0.1:4321"]

# Rechaza cualquier Host que no sea local: evita ataques de DNS rebinding, en los
# que una web ajena resuelve su dominio a 127.0.0.1 y lee la API como "mismo origen".
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# CORS no impide que otra web dispare un POST (solo le impide leer la respuesta),
# así que además rechazamos cualquier petición de navegador con un Origin ajeno.
# Las que cambian estado (lanzan envíos o modifican el CSV) deben traer además un
# Origin permitido: una petición sin Origin no viene del frontend.
METODOS_SEGUROS = {"GET", "HEAD", "OPTIONS"}


@app.middleware("http")
async def bloquear_origenes_desconocidos(request: Request, call_next):
    origin = request.headers.get("origin")
    if origin and origin not in ALLOWED_ORIGINS:
        return JSONResponse(status_code=403, content={"detail": "Origen no permitido"})
    if request.method not in METODOS_SEGUROS and not origin:
        return JSONResponse(status_code=403, content={"detail": "Falta la cabecera Origin"})
    return await call_next(request)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CSV_FILE        = os.path.join(ROOT, 'Leads Google Maps.csv')
SEND_SCRIPT       = os.path.join(ROOT, 'app', 'whatsApp_node', 'send_whatsapp.js')
EMAIL_SCRIPT      = os.path.join(ROOT, 'app', 'scraper-python', 'send_emails.py')
INSTAGRAM_SCRIPT  = os.path.join(ROOT, 'app', 'scraper-python', 'send_instagram.py')
PYTHON_BIN        = os.path.join(ROOT, 'app', 'backend', '.venv', 'bin', 'python3')

COLUMNAS_REDES = ['Facebook', 'Instagram', 'LinkedIn', 'Twitter', 'TikTok', 'YouTube']

# Un proceso de envío por canal: lanzar dos a la vez manda mensajes duplicados
# (ambos leen el mismo log de enviados) y corrompe el log al escribirlo.
procesos_envio: dict[str, subprocess.Popen] = {}


def lanzar_envio(canal: str, comando: list[str]) -> subprocess.Popen:
    proc = procesos_envio.get(canal)
    if proc and proc.poll() is None:
        raise HTTPException(status_code=409, detail=f"Ya hay un envío de {canal} en curso (PID {proc.pid})")
    proc = subprocess.Popen(comando, cwd=ROOT)
    procesos_envio[canal] = proc
    return proc


def read_df() -> pd.DataFrame:
    if not os.path.exists(CSV_FILE):
        raise HTTPException(status_code=404, detail="CSV no encontrado")
    df = pd.read_csv(CSV_FILE, encoding='utf-8-sig', dtype=str).fillna('')
    if 'selected' not in df.columns:
        df['selected'] = False
    for col in COLUMNAS_REDES + ['Guion', 'Maqueta', 'Tipo teléfono', 'Llamada', 'Fecha llamada']:
        if col not in df.columns:
            df[col] = ''
    # Leads antiguos (anteriores a la etiqueta) o editados a mano: se calcula al vuelo
    sin_tipo = df['Tipo teléfono'] == ''
    df.loc[sin_tipo, 'Tipo teléfono'] = df.loc[sin_tipo, 'Teléfono'].apply(contacto.tipo_telefono)
    return df


def save_df(df: pd.DataFrame):
    df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')


def get_emailed_addresses() -> set:
    mail_log = os.path.join(ROOT, 'email_log.json')
    if not os.path.exists(mail_log):
        return set()
    with open(mail_log) as f:
        return {e['email'].strip() for e in json.load(f).get('enviados', []) if e.get('email')}


@app.get("/api/leads")
def get_leads():
    df = read_df()
    ya_enviados = get_emailed_addresses()
    df['email_enviado'] = df['Email'].apply(lambda e: bool(e and e.strip() in ya_enviados))
    df['sector'] = df.apply(lambda r: contacto.sector_de(r.to_dict()) or '', axis=1)
    df = df.where(pd.notnull(df), None)
    records = df.reset_index().rename(columns={'index': 'id'}).to_dict(orient='records')
    return records[::-1]


class SelectRequest(BaseModel):
    ids: List[int]
    selected: bool


@app.patch("/api/leads/select")
def update_selection(body: SelectRequest):
    df = read_df()
    for idx in body.ids:
        if idx in df.index:
            df.at[idx, 'selected'] = str(body.selected)
    save_df(df)
    return {"ok": True}


class SelectAllRequest(BaseModel):
    selected: bool


@app.patch("/api/leads/select-all")
def select_all(body: SelectAllRequest):
    df = read_df()
    df['selected'] = str(body.selected)
    save_df(df)
    return {"ok": True}


@app.patch("/api/leads/select-not-emailed")
def select_not_emailed():
    """Selecciona solo los leads cuyo email nunca ha sido enviado."""
    df = read_df()
    ya_enviados = get_emailed_addresses()
    df['selected'] = df['Email'].apply(
        lambda e: str(bool(e and e.strip() and e.strip() not in ya_enviados))
    )
    save_df(df)
    count = int((df['selected'] == 'True').sum())
    return {"ok": True, "selected": count}


@app.post("/api/whatsapp/launch")
def launch_whatsapp():
    df = read_df()
    selected_count = int((df['selected'] == 'True').sum() + (df['selected'] == True).sum())
    if selected_count == 0:
        raise HTTPException(status_code=400, detail="No hay leads seleccionados")

    proc = lanzar_envio('whatsapp', ['node', SEND_SCRIPT, '--selected-only'])
    return {"ok": True, "pid": proc.pid, "selected": selected_count}


@app.post("/api/email/launch")
def launch_email():
    df = read_df()
    selected_count = int((df['selected'] == 'True').sum() + (df['selected'] == True).sum())
    if selected_count == 0:
        raise HTTPException(status_code=400, detail="No hay leads seleccionados")

    con_email = df[(df['selected'].isin(['True', 'true', '1'])) & (df['Email'] != '')].shape[0]
    if con_email == 0:
        raise HTTPException(status_code=400, detail="Ningún lead seleccionado tiene email")

    proc = lanzar_envio('email', [PYTHON_BIN, EMAIL_SCRIPT, '--selected-only'])
    return {"ok": True, "pid": proc.pid, "selected": con_email}


@app.post("/api/instagram/launch")
def launch_instagram():
    df = read_df()
    selected_count = int((df['selected'] == 'True').sum() + (df['selected'] == True).sum())
    if selected_count == 0:
        raise HTTPException(status_code=400, detail="No hay leads seleccionados")

    con_ig = df[(df['selected'].isin(['True', 'true', '1'])) & (df['Instagram'] != '')].shape[0]
    if con_ig == 0:
        raise HTTPException(status_code=400, detail="Ningún lead seleccionado tiene Instagram")

    proc = lanzar_envio('instagram', [PYTHON_BIN, INSTAGRAM_SCRIPT, '--selected-only'])
    return {"ok": True, "pid": proc.pid, "selected": con_ig}


@app.get("/api/whatsapp/qr")
def get_whatsapp_qr():
    """Sirve el último QR generado por send_whatsapp.js (se regenera cada ~30s)."""
    qr_path = os.path.join(ROOT, 'qr.png')
    if not os.path.exists(qr_path):
        raise HTTPException(status_code=404, detail="Aún no hay QR: lanza el envío de WhatsApp primero")
    return FileResponse(qr_path, media_type='image/png', headers={'Cache-Control': 'no-store'})


@app.get("/api/status")
def get_status():
    wa_log  = os.path.join(ROOT, 'whatsapp_log.json')
    mail_log = os.path.join(ROOT, 'email_log.json')
    ig_log  = os.path.join(ROOT, 'instagram_log.json')

    wa_enviados = 0
    if os.path.exists(wa_log):
        with open(wa_log) as f:
            wa_enviados = len(json.load(f).get('enviados', []))

    mail_enviados = 0
    if os.path.exists(mail_log):
        with open(mail_log) as f:
            mail_enviados = len(json.load(f).get('enviados', []))

    ig_enviados = 0
    if os.path.exists(ig_log):
        with open(ig_log) as f:
            ig_enviados = len(json.load(f).get('enviados', []))

    return {"enviados": wa_enviados, "emails_enviados": mail_enviados, "ig_enviados": ig_enviados}


# ── Preparar contacto: guion de llamada y maqueta de web ──────────────────────

def lead_por_id(df: pd.DataFrame, lead_id: int) -> dict:
    if lead_id not in df.index:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    return df.loc[lead_id].to_dict()


@app.post("/api/leads/{lead_id}/guion")
def crear_guion(lead_id: int):
    df = read_df()
    lead = lead_por_id(df, lead_id)
    try:
        guion = contacto.generar_guion(lead)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"No se pudo generar el guion: {e}")
    df.at[lead_id, 'Guion'] = guion
    save_df(df)
    return {"guion": guion, "sector": contacto.sector_de(lead)}


@app.post("/api/leads/{lead_id}/maqueta")
def crear_maqueta(lead_id: int):
    df = read_df()
    lead = lead_por_id(df, lead_id)
    try:
        archivo = contacto.generar_maqueta(lead, lead_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    df.at[lead_id, 'Maqueta'] = archivo
    save_df(df)
    return {"maqueta": archivo, "url": f"/maquetas/{archivo}"}


@app.get("/maquetas/{archivo}")
def ver_maqueta(archivo: str):
    # Solo nombres generados por contacto._slug: nada de rutas ni ../
    if not re.fullmatch(r'[a-z0-9-]+\.html', archivo):
        raise HTTPException(status_code=404, detail="Maqueta no encontrada")
    ruta = os.path.join(contacto.MAQUETAS_DIR, archivo)
    if not os.path.exists(ruta):
        raise HTTPException(status_code=404, detail="Maqueta no encontrada")
    return FileResponse(ruta, media_type='text/html')


# ── Llamadas: leads con teléfono fijo (sin WhatsApp) ───────────────────────────

ESTADOS_LLAMADA = {'', 'No contesta', 'Interesado', 'No interesado'}


class LlamadaRequest(BaseModel):
    estado: str


@app.patch("/api/leads/{lead_id}/llamada")
def actualizar_llamada(lead_id: int, body: LlamadaRequest):
    if body.estado not in ESTADOS_LLAMADA:
        raise HTTPException(status_code=400, detail="Estado de llamada no válido")
    df = read_df()
    lead_por_id(df, lead_id)
    df.at[lead_id, 'Llamada'] = body.estado
    df.at[lead_id, 'Fecha llamada'] = date.today().isoformat() if body.estado else ''
    save_df(df)
    return {"ok": True}
