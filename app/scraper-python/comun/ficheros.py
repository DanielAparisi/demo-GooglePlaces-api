"""Escritura atómica: se escribe a un temporal y se renombra.

Así quien lea el fichero (el panel, otro script) nunca ve uno a medio escribir, y un
fallo a mitad no deja el original truncado.
"""
import json
import os
import stat
import tempfile
from pathlib import Path
from typing import Callable, TextIO


def escribir_atomico(ruta: Path, escribir: Callable[[TextIO], None], encoding: str = 'utf-8') -> None:
    ruta = Path(ruta)
    fd, tmp = tempfile.mkstemp(dir=ruta.parent, prefix=f'.{ruta.name}-', suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding=encoding, newline='') as f:
            escribir(f)
        if ruta.exists():  # conserva los permisos del original
            os.chmod(tmp, stat.S_IMODE(ruta.stat().st_mode))
        os.replace(tmp, ruta)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def guardar_json(ruta: Path, datos) -> None:
    escribir_atomico(ruta, lambda f: json.dump(datos, f, indent=2, ensure_ascii=False))
