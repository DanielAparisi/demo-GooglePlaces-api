"""Utilidades comunes a las campañas de email e Instagram: log, bajas y ritmo."""
import json
import time
from datetime import datetime
from pathlib import Path

from comun.ficheros import guardar_json
from comun import rutas

PIE_BAJA = 'Si no quieres recibir más mensajes, responde "baja" y no volveré a escribirte.'


class LogEnvios:
    """Log JSON {'enviados': [...], 'fallidos': [...]} que también lee el panel."""

    def __init__(self, ruta: Path):
        self.ruta = Path(ruta)
        self.datos = {'enviados': [], 'fallidos': []}
        if self.ruta.exists():
            self.datos.update(json.loads(self.ruta.read_text(encoding='utf-8')))
        self.datos.setdefault('enviados', [])
        self.datos.setdefault('fallidos', [])

    def ya_enviados(self, campo: str) -> set[str]:
        return {str(e[campo]).strip().lower() for e in self.datos['enviados'] if e.get(campo)}

    def _registrar(self, lista: str, **entrada) -> None:
        self.datos[lista].append({**entrada, 'fecha': datetime.now().isoformat()})
        guardar_json(self.ruta, self.datos)  # tras cada envío: si se corta, no se repite

    def enviado(self, **entrada) -> None:
        self._registrar('enviados', **entrada)

    def fallido(self, **entrada) -> None:
        self._registrar('fallidos', **entrada)

    def resumen(self) -> str:
        return f"Enviados: {len(self.datos['enviados'])} | Fallidos: {len(self.datos['fallidos'])}"


def cargar_bajas(ruta: Path | None = None) -> set[str]:
    """Emails o usuarios de Instagram que han pedido no recibir más mensajes (uno por línea)."""
    ruta = Path(ruta) if ruta is not None else rutas.BAJAS_FILE
    if not ruta.exists():
        return set()
    lineas = (l.split('#', 1)[0].strip().lower().lstrip('@') for l in ruta.read_text(encoding='utf-8').splitlines())
    return {l for l in lineas if l}


def esperar_entre(i: int, total: int, segundos: float) -> None:
    if i < total - 1:
        print(f'  Esperando {segundos}s...')
        time.sleep(segundos)
