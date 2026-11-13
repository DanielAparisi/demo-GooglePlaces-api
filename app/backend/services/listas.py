"""Listas de leads para agencias con suscripción mensual: previsualizar, crear y entregar.

El algoritmo vive en scraper-python/comun/listas.py (también lo usa crear_lista.py).
"""
import calendar
import json
import threading
from datetime import date
from pathlib import Path

from core.domain import cargar_pesos, listas
from core.errors import BadRequestError, ConflictError, NotFoundError
from core.settings import Settings
from repositories.leads import LeadsRepository
from schemas.listas import PedidoLista

MUESTRA = 10

# Dos pedidos a la vez podrían vender el mismo lead exclusivo: se crean de uno en uno.
_creando = threading.Lock()


def _mes_siguiente(d: date) -> date:
    anio, mes = (d.year + 1, 1) if d.month == 12 else (d.year, d.month + 1)
    return d.replace(year=anio, month=mes, day=min(d.day, calendar.monthrange(anio, mes)[1]))


class ListasService:
    def __init__(self, repo: LeadsRepository, settings: Settings):
        self.repo = repo
        self.settings = settings

    # ── Lectura ──────────────────────────────────────────────────────────────

    def _entregas(self) -> list[dict]:
        try:
            return listas.leer_entregas(self.settings.entregas_file)
        except ValueError as e:
            raise ConflictError(str(e)) from e

    def _busquedas_hechas(self) -> list[str]:
        try:
            return json.loads(self.settings.search_state_file.read_text(encoding='utf-8')).get('hechas', [])
        except (OSError, ValueError):
            return []

    def resumen(self, hoy: date | None = None) -> dict:
        """Planes, suscripciones por agencia (cuándo toca la próxima lista) e historial."""
        hoy = hoy or date.today()
        entregas = self._entregas()
        historial = [
            {k: e.get(k) for k in ('id', 'cliente', 'fecha', 'exclusivo', 'archivo', 'pedido')}
            | {'n_leads': len(e.get('leads', [])),
               'descargable': bool(e.get('archivo')) and (self.settings.listas_dir / e['archivo']).is_file()}
            for e in entregas
        ]

        clientes: dict[str, dict] = {}
        for e in historial:  # en orden de registro: la última entrega manda
            c = clientes.setdefault(e['cliente'], {'cliente': e['cliente'], 'entregas': 0, 'leads': 0})
            c['entregas'] += 1
            c['leads'] += e['n_leads']
            c['ultima'] = e['fecha']
            c['ultimo_pedido'] = e['pedido']
            c['plan'] = (e['pedido'] or {}).get('plan')
        for c in clientes.values():
            try:
                proxima = _mes_siguiente(date.fromisoformat(c['ultima']))
            except (TypeError, ValueError):
                proxima = hoy
            c['proxima'] = proxima.isoformat()
            c['dias'] = (proxima - hoy).days

        return {
            'planes': [{'id': k, **v} for k, v in listas.PLANES.items()],
            'clientes': sorted(clientes.values(), key=lambda c: c['dias']),
            'entregas': historial[::-1],  # las más recientes primero
        }

    # ── Pedidos ──────────────────────────────────────────────────────────────

    def _pedido(self, body: PedidoLista) -> dict:
        if body.plan and body.plan not in listas.PLANES:
            raise BadRequestError(f'Plan desconocido: {body.plan}')
        plan = listas.PLANES.get(body.plan or '', {})
        cantidad = body.cantidad or plan.get('cantidad')
        if not cantidad:
            raise BadRequestError('Elige un plan o indica la cantidad de leads')
        return {
            'cliente': body.cliente.strip(), 'plan': body.plan, 'cantidad': cantidad,
            'sectores': [s.strip() for s in body.sectores if s.strip()],
            'ciudades': [c.strip() for c in body.ciudades if c.strip()],
            'requiere': body.requiere, 'puntuacion_min': body.puntuacion_min,
            'exclusivo': body.exclusivo or plan.get('exclusivo', False),
        }

    def _crear_lista(self, body: PedidoLista) -> dict:
        leads = self.repo.read().to_dict(orient='records')
        try:
            return listas.crear_lista(leads, self._pedido(body), self._entregas(),
                                      pesos=cargar_pesos(self.settings.pesos_file),
                                      busquedas_hechas=self._busquedas_hechas())
        except ValueError as e:
            raise BadRequestError(str(e)) from e

    @staticmethod
    def _respuesta(lista: dict) -> dict:
        return {
            'pedido': lista['pedido'],
            'resumen': lista['resumen'],
            'sugerencias': lista['sugerencias'],
            'muestra': listas.filas_entrega({'leads': lista['leads'][:MUESTRA]}),
        }

    def simular(self, body: PedidoLista) -> dict:
        """Qué saldría con este pedido, sin exportar ni registrar nada."""
        return self._respuesta(self._crear_lista(body))

    def crear(self, body: PedidoLista) -> dict:
        """Crea la lista, exporta el CSV y registra la entrega (no se repetirán esos leads)."""
        with _creando:
            lista = self._crear_lista(body)
            if not lista['leads']:
                raise BadRequestError('No hay leads que encajen con este pedido')
            ruta = listas.exportar(lista, self.settings.listas_dir)
            entrega = listas.registrar_entrega(self.settings.entregas_file, lista, archivo=ruta.name)
        return {**self._respuesta(lista), 'entrega': entrega, 'archivo': ruta.name}

    def archivo(self, nombre: str) -> Path:
        carpeta = self.settings.listas_dir.resolve()
        ruta = (carpeta / nombre).resolve()
        if ruta.parent != carpeta or ruta.suffix != '.csv' or not ruta.is_file():
            raise NotFoundError('Lista no encontrada')
        return ruta
