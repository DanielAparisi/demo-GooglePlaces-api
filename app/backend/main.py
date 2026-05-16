import json
import os
import subprocess

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CSV_FILE        = os.path.join(ROOT, 'Leads Google Maps.csv')
SEND_SCRIPT       = os.path.join(ROOT, 'app', 'whatsApp_node', 'send_whatsapp.js')
EMAIL_SCRIPT      = os.path.join(ROOT, 'app', 'scraper-python', 'send_emails.py')
INSTAGRAM_SCRIPT  = os.path.join(ROOT, 'app', 'scraper-python', 'send_instagram.py')
PYTHON_BIN        = os.path.join(ROOT, 'app', 'backend', '.venv', 'bin', 'python3')

COLUMNAS_REDES = ['Facebook', 'Instagram', 'LinkedIn', 'Twitter', 'TikTok', 'YouTube']


def read_df() -> pd.DataFrame:
    if not os.path.exists(CSV_FILE):
        raise HTTPException(status_code=404, detail="CSV no encontrado")
    df = pd.read_csv(CSV_FILE, encoding='utf-8-sig', dtype=str).fillna('')
    if 'selected' not in df.columns:
        df['selected'] = False
    for col in COLUMNAS_REDES:
        if col not in df.columns:
            df[col] = ''
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
    selected_count = int((df['selected'] == True).sum())
    if selected_count == 0:
        raise HTTPException(status_code=400, detail="No hay leads seleccionados")

    proc = subprocess.Popen(
        ['node', SEND_SCRIPT, '--selected-only'],
        cwd=ROOT,
    )
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

    proc = subprocess.Popen(
        [PYTHON_BIN, EMAIL_SCRIPT, '--selected-only'],
        cwd=ROOT,
    )
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

    proc = subprocess.Popen(
        [PYTHON_BIN, INSTAGRAM_SCRIPT, '--selected-only'],
        cwd=ROOT,
    )
    return {"ok": True, "pid": proc.pid, "selected": con_ig}


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
