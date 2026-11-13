"""Acceso al CSV de leads compartido por el backend y los scripts.

Todos los que escriben el CSV deben hacerlo dentro de `editar()` (o `anadir()`): toman
un bloqueo de fichero, releen el CSV, aplican su cambio y lo guardan de forma atómica.
Así un script largo (el enriquecido tarda minutos) no pisa las selecciones o llamadas
que se marcan en el panel mientras tanto.
"""
import fcntl
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import pandas as pd

from comun.ficheros import escribir_atomico
from comun import rutas

ENCODING = 'utf-8-sig'
VERDADEROS = {'true', '1', 'yes'}

_hilo = threading.local()


def _ruta(csv: Path | None) -> Path:
    """Sin ruta explícita se usa la del proyecto (resuelta al llamar, no al importar)."""
    return Path(csv) if csv is not None else rutas.CSV_FILE


def _ruta_bloqueo(csv: Path) -> Path:
    return csv.with_name(f'.{csv.name}.lock')


@contextmanager
def bloqueo(csv: Path | None = None) -> Iterator[None]:
    """Bloqueo exclusivo entre procesos e hilos. Reentrante dentro del mismo hilo."""
    if getattr(_hilo, 'dentro', False):
        yield
        return
    with open(_ruta_bloqueo(_ruta(csv)), 'a') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        _hilo.dentro = True
        try:
            yield
        finally:
            _hilo.dentro = False
            fcntl.flock(f, fcntl.LOCK_UN)


def leer(csv: Path | None = None) -> pd.DataFrame:
    """Todo como texto: sin esto pandas convierte 'True' en bool o teléfonos en números."""
    return pd.read_csv(_ruta(csv), encoding=ENCODING, dtype=str).fillna('')


def escribir(df: pd.DataFrame, csv: Path | None = None) -> None:
    escribir_atomico(_ruta(csv), lambda f: df.to_csv(f, index=False), encoding=ENCODING)


@contextmanager
def editar(csv: Path | None = None) -> Iterator[pd.DataFrame]:
    """Lee, deja modificar el DataFrame en sitio y guarda al salir. Si el bloque falla, no guarda."""
    with bloqueo(csv):
        df = leer(csv)
        yield df
        escribir(df, csv)


def anadir(filas: list[dict], columnas: list[str], csv: Path | None = None) -> int:
    """Añade negocios nuevos al final, sin duplicar (mismo nombre + dirección).

    Las filas existentes no se mueven: su posición es el id que usa el panel.
    Devuelve cuántos se añadieron.
    """
    csv = _ruta(csv)
    clave = ['Nombre del negocio', 'Ubicación']
    nuevos = pd.DataFrame(filas, columns=columnas).fillna('').drop_duplicates(subset=clave)
    with bloqueo(csv):
        if csv.exists():
            existentes = leer(csv)
            vistos = set(zip(existentes['Nombre del negocio'], existentes['Ubicación']))
            nuevos = nuevos[[k not in vistos for k in zip(nuevos['Nombre del negocio'], nuevos['Ubicación'])]]
            total = pd.concat([existentes, nuevos], ignore_index=True).fillna('')
        else:
            total = nuevos
        escribir(total, csv)
    return len(nuevos)


def esta_seleccionado(valor) -> bool:
    return str(valor).strip().lower() in VERDADEROS


def localizar(df: pd.DataFrame, nombre: str, ubicacion: str, pista: int | None = None) -> int | None:
    """Índice de un negocio. `pista` es su índice cuando se leyó: se comprueba primero."""
    if pista is not None and pista in df.index:
        fila = df.loc[pista]
        if fila['Nombre del negocio'] == nombre and fila['Ubicación'] == ubicacion:
            return pista
    coincide = df.index[(df['Nombre del negocio'] == nombre) & (df['Ubicación'] == ubicacion)]
    return int(coincide[0]) if len(coincide) else None
