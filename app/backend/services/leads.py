"""Casos de uso sobre la lista de leads: listado, selección y llamadas."""
from datetime import date
from pathlib import Path

import pandas as pd

from core.domain import cargar_pesos, puntuar, sector_de
from core.errors import BadRequestError
from repositories.leads import LeadsRepository, selected_mask
from repositories.logs import SendLogsRepository

ESTADOS_LLAMADA = {'', 'No contesta', 'Interesado', 'No interesado'}


class LeadsService:
    def __init__(self, repo: LeadsRepository, logs: SendLogsRepository, pesos_file: Path):
        self.repo = repo
        self.logs = logs
        self.pesos_file = pesos_file

    def listar(self) -> list[dict]:
        df = self.repo.read()
        ya_enviados = self.logs.emails_enviados()
        df['email_enviado'] = df['Email'].apply(lambda e: bool(e and e.strip() in ya_enviados))
        df['sector'] = df.apply(lambda r: sector_de(r.to_dict()) or '', axis=1)
        df = df.where(pd.notnull(df), None)
        registros = df.reset_index().rename(columns={'index': 'id'}).to_dict(orient='records')
        pesos = cargar_pesos(self.pesos_file)
        for r in registros:
            # Se calcula al vuelo: cambia cuando el enriquecido añade email o redes o se recalibra.
            o = puntuar(r, pesos)
            r.update(oportunidad=o['puntuacion'], oportunidad_nivel=o['nivel'], oportunidad_motivos=o['motivos'])
        return registros[::-1]  # los más recientes primero

    def seleccionar(self, ids: list[int], selected: bool) -> None:
        with self.repo.edit() as df:
            for idx in ids:
                if idx in df.index:
                    df.at[idx, 'selected'] = str(selected)

    def seleccionar_todos(self, selected: bool) -> None:
        with self.repo.edit() as df:
            df['selected'] = str(selected)

    def seleccionar_sin_email_previo(self) -> int:
        """Marca solo los leads con email al que nunca se ha escrito. Devuelve cuántos."""
        ya_enviados = self.logs.emails_enviados()
        with self.repo.edit() as df:
            df['selected'] = df['Email'].apply(
                lambda e: str(bool(e and e.strip() and e.strip() not in ya_enviados))
            )
            return int(selected_mask(df).sum())

    def actualizar_llamada(self, lead_id: int, estado: str) -> None:
        if estado not in ESTADOS_LLAMADA:
            raise BadRequestError('Estado de llamada no válido')
        self.repo.set_fields(
            lead_id,
            **{'Llamada': estado, 'Fecha llamada': date.today().isoformat() if estado else ''},
        )
