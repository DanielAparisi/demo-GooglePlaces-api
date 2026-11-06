"""Acceso al CSV de leads desde el backend.

Usa el mismo bloqueo de fichero y la misma escritura atómica que los scripts
(scraper-python/comun/leads_csv.py), así el panel y un enriquecido en marcha no se
pisan los cambios.
"""
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import pandas as pd

from core.domain import leads_csv, tipo_telefono
from core.errors import NotFoundError

COLUMNAS_REDES = ['Facebook', 'Instagram', 'LinkedIn', 'Twitter', 'TikTok', 'YouTube']
COLUMNAS_EXTRA = ['Guion', 'Maqueta', 'Tipo teléfono', 'Llamada', 'Fecha llamada']


def selected_mask(df: pd.DataFrame) -> pd.Series:
    """Filas marcadas. El CSV guarda 'True'/'False' como texto y los scripts de envío lo leen así."""
    return df['selected'].map(leads_csv.esta_seleccionado).astype(bool)


class LeadsRepository:
    def __init__(self, path: Path):
        self.path = Path(path)

    def _read(self) -> pd.DataFrame:
        if not self.path.exists():
            raise NotFoundError('CSV no encontrado')
        df = leads_csv.leer(self.path)
        if 'selected' not in df.columns:
            df['selected'] = 'False'
        for col in COLUMNAS_REDES + COLUMNAS_EXTRA:
            if col not in df.columns:
                df[col] = ''
        # Leads antiguos (anteriores a la etiqueta) o editados a mano: se calcula al vuelo
        sin_tipo = df['Tipo teléfono'] == ''
        df.loc[sin_tipo, 'Tipo teléfono'] = df.loc[sin_tipo, 'Teléfono'].apply(tipo_telefono)
        return df

    def read(self) -> pd.DataFrame:
        # La escritura es atómica: leer no necesita el bloqueo.
        return self._read()

    @contextmanager
    def edit(self) -> Iterator[pd.DataFrame]:
        """Lee, deja modificar el DataFrame y guarda al salir. Si el bloque falla, no guarda."""
        with leads_csv.bloqueo(self.path):
            df = self._read()
            yield df
            leads_csv.escribir(df, self.path)

    def get(self, lead_id: int) -> dict:
        df = self.read()
        if lead_id not in df.index:
            raise NotFoundError('Lead no encontrado')
        return df.loc[lead_id].to_dict()

    def set_fields(self, lead_id: int, **campos: str) -> None:
        with self.edit() as df:
            if lead_id not in df.index:
                raise NotFoundError('Lead no encontrado')
            for col, valor in campos.items():
                df.at[lead_id, col] = valor
