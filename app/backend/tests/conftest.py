"""Fixtures: una app completa montada sobre un directorio temporal con datos sintéticos."""
import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from core.settings import Settings
from main import create_app

COLUMNAS = [
    'Nombre del negocio', 'Email', 'Categoría', 'Ubicación', 'Teléfono', 'Facebook', 'Instagram',
    'LinkedIn', 'Twitter', 'TikTok', 'YouTube', 'selected', 'enriched', 'Mensaje', 'Guion',
    'Maqueta', 'Tipo teléfono', 'Llamada', 'Fecha llamada',
]

LEADS = [
    {'Nombre del negocio': 'REFORMAS LEVANTE - Reformas en Cartagena', 'Email': 'obras@example.test',
     'Categoría': 'Negocio', 'Ubicación': 'Calle Mayor 1, 30201 Cartagena, Murcia, Spain',
     'Teléfono': '612 345 678', 'selected': 'False'},
    {'Nombre del negocio': 'Taller Pepe', 'Email': '', 'Categoría': 'Negocio',
     'Ubicación': 'Calle Sol 5, 30001 Murcia, Murcia, Spain', 'Teléfono': '968 123 456', 'selected': 'False'},
    {'Nombre del negocio': 'Fisio Sol', 'Email': 'fisio@example.test', 'Categoría': 'Negocio',
     'Ubicación': 'Av. Mar 3, 30500 Molina, Murcia, Spain', 'Teléfono': '',
     'Instagram': 'https://instagram.com/fisio_sol', 'selected': 'False'},
]


@dataclass
class Env:
    root: Path
    client: TestClient
    app: object

    @property
    def csv(self) -> pd.DataFrame:
        return pd.read_csv(self.root / 'Leads Google Maps.csv', encoding='utf-8-sig', dtype=str).fillna('')

    def write_log(self, canal: str, enviados: list[dict]) -> None:
        nombre = {'whatsapp': 'whatsapp_log.json', 'email': 'email_log.json', 'instagram': 'instagram_log.json'}[canal]
        (self.root / nombre).write_text(json.dumps({'enviados': enviados}), encoding='utf-8')


@pytest.fixture
def env(tmp_path: Path) -> Env:
    filas = [{**{c: '' for c in COLUMNAS}, **fila} for fila in LEADS]
    pd.DataFrame(filas, columns=COLUMNAS).to_csv(tmp_path / 'Leads Google Maps.csv', index=False, encoding='utf-8-sig')

    settings = Settings(root=tmp_path, allowed_hosts=('testserver',))
    app = create_app(settings)
    # Origin permitido por defecto: los endpoints que cambian estado lo exigen
    client = TestClient(app, headers={'Origin': 'http://localhost:4321'})
    return Env(root=tmp_path, client=client, app=app)
