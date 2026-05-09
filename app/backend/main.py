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
SEND_SCRIPT     = os.path.join(ROOT, 'app', 'whatsApp_node', 'send_whatsapp.js')
EMAIL_SCRIPT    = os.path.join(ROOT, 'app', 'scraper-python', 'send_emails.py')
PYTHON_BIN      = os.path.join(ROOT, 'app', 'backend', '.venv', 'bin', 'python3')

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


@app.get("/api/leads")
def get_leads():
    df = read_df()
    df = df.where(pd.notnull(df), None)
    records = df.reset_index().rename(columns={'index': 'id'}).to_dict(orient='records')
    return records


class SelectRequest(BaseModel):
    ids: List[int]
    selected: bool


@app.patch("/api/leads/select")
def update_selection(body: SelectRequest):
    df = read_df()
    for idx in body.ids:
        if idx in df.index:
            df.at[idx, 'selected'] = body.selected
    save_df(df)
    return {"ok": True}


class SelectAllRequest(BaseModel):
    selected: bool


@app.patch("/api/leads/select-all")
def select_all(body: SelectAllRequest):
    df = read_df()
    df['selected'] = body.selected
    save_df(df)
    return {"ok": True}


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


@app.get("/api/status")
def get_status():
    wa_log   = os.path.join(ROOT, 'whatsapp_log.json')
    mail_log = os.path.join(ROOT, 'email_log.json')

    wa_enviados = 0
    if os.path.exists(wa_log):
        with open(wa_log) as f:
            wa_enviados = len(json.load(f).get('enviados', []))

    mail_enviados = 0
    if os.path.exists(mail_log):
        with open(mail_log) as f:
            mail_enviados = len(json.load(f).get('enviados', []))

    return {"enviados": wa_enviados, "emails_enviados": mail_enviados}
