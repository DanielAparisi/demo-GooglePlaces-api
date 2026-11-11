"""Ajusta los pesos del modelo de oportunidad con el resultado real de las llamadas.

Idea: para cada bloque del modelo (web, demanda, contacto...) se compara cuánto lo cumplían
de media los leads que dijeron "Interesado" frente a los que dijeron "No interesado".
  · Si los interesados lo cumplen más → la señal predice bien → su peso sube.
  · Si lo cumplen menos → la señal engaña → su peso baja.
  · Si no hay diferencia → se queda como estaba.

Con pocas llamadas el ajuste es prudente: la diferencia se multiplica por una confianza
n / (n + FUERZA_PREVIA), así 20 llamadas mueven la mitad que infinitas. Cada peso se mueve
como mucho entre ×0.25 y ×2 del de partida, y al final se reescalan para sumar 100.

"No contesta" no cuenta: no dice nada sobre si el negocio quiere una web.
"""
import json
from datetime import date
from pathlib import Path

from comun.ficheros import guardar_json
from comun.oportunidad import PESOS_BASE, bloques, descartado, puntuar

MIN_RESULTADOS = 20      # llamadas con respuesta (interesado / no interesado) para calibrar
MIN_POR_CLASE = 3        # sin al menos 3 de cada, no hay con qué comparar
FUERZA_PREVIA = 20       # cuántas llamadas "vale" la opinión de partida
GANANCIA = 2.0           # diferencia de 0.5 entre grupos con confianza total → peso ×2
MULT_MIN, MULT_MAX = 0.25, 2.0

INTERESADO, NO_INTERESADO = 'Interesado', 'No interesado'


def _resultado(lead):
    """1 interesado, 0 no interesado, None si no hay resultado útil."""
    return {INTERESADO: 1, NO_INTERESADO: 0}.get(str(lead.get('Llamada') or '').strip())


def _con_resultado(leads):
    return [(l, y) for l in leads if (y := _resultado(l)) is not None and not descartado(l)]


def estado(leads):
    """Cuántas llamadas con resultado hay y cuántas faltan para poder calibrar."""
    decididos = _con_resultado(leads)
    si = sum(y for _, y in decididos)
    no = len(decididos) - si
    faltan = max(MIN_RESULTADOS - len(decididos), MIN_POR_CLASE - si, MIN_POR_CLASE - no, 0)
    return {'resultados': len(decididos), 'interesados': si, 'no_interesados': no,
            'puede_calibrar': faltan == 0, 'faltan': faltan}


def calibrar(leads, base=None):
    """Nuevos pesos a partir de las llamadas. Lanza ValueError si aún no hay datos suficientes."""
    base = base or PESOS_BASE
    info = estado(leads)
    if not info['puede_calibrar']:
        raise ValueError(
            f"Faltan llamadas con resultado para calibrar: hay {info['resultados']} "
            f"({info['interesados']} interesados, {info['no_interesados']} no interesados); "
            f"se necesitan {MIN_RESULTADOS} con al menos {MIN_POR_CLASE} de cada."
        )

    decididos = _con_resultado(leads)
    fracciones = [({b: f for b, (f, _) in bloques(l).items()}, y) for l, y in decididos]
    confianza = len(decididos) / (len(decididos) + FUERZA_PREVIA)

    detalle, pesos = {}, {}
    for b, peso_base in base.items():
        si = [f[b] for f, y in fracciones if y == 1]
        no = [f[b] for f, y in fracciones if y == 0]
        media_si, media_no = sum(si) / len(si), sum(no) / len(no)
        multiplicador = 1 + GANANCIA * (media_si - media_no) * confianza
        multiplicador = min(MULT_MAX, max(MULT_MIN, multiplicador))
        pesos[b] = peso_base * multiplicador
        detalle[b] = {'media_interesados': round(media_si, 3), 'media_no_interesados': round(media_no, 3),
                      'multiplicador': round(multiplicador, 3)}

    escala = 100 / sum(pesos.values())
    pesos = {b: round(p * escala, 1) for b, p in pesos.items()}
    return {'pesos': pesos, 'fecha': date.today().isoformat(), 'confianza': round(confianza, 3),
            **{k: info[k] for k in ('resultados', 'interesados', 'no_interesados')}, 'detalle': detalle}


def rendimiento(leads, pesos=None):
    """Tasa de interés real por nivel de prioridad: ¿acierta el modelo?"""
    filas = {n: {'nivel': n, 'leads': 0, 'resultados': 0, 'interesados': 0, 'tasa': None}
             for n in ('Alta', 'Media', 'Baja')}
    for lead in leads:
        if descartado(lead):
            continue
        fila = filas[puntuar(lead, pesos)['nivel']]
        fila['leads'] += 1
        y = _resultado(lead)
        if y is not None:
            fila['resultados'] += 1
            fila['interesados'] += y
    for fila in filas.values():
        if fila['resultados']:
            fila['tasa'] = round(fila['interesados'] / fila['resultados'], 3)
    return list(filas.values())


def guardar(ruta, calibracion):
    guardar_json(Path(ruta), calibracion)


def leer(ruta):
    """La última calibración guardada, o None."""
    ruta = Path(ruta)
    if not ruta.exists():
        return None
    try:
        return json.loads(ruta.read_text(encoding='utf-8'))
    except ValueError:
        return None
