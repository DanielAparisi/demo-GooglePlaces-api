import json
from pathlib import Path

import pytest

from comun.dominio import ciudad_de, limpiar_dato, nombre_comercial, tipo_telefono


CASOS = json.loads((Path(__file__).parent / 'casos_dominio.json').read_text(encoding='utf-8'))


@pytest.mark.parametrize('ubicacion, ciudad', CASOS['ciudad'])
def test_ciudad_de(ubicacion, ciudad):
    assert ciudad_de(ubicacion) == ciudad


def test_ciudad_de_none():
    assert ciudad_de(None) == ''


@pytest.mark.parametrize('telefono, movil', CASOS['movil'])
def test_tipo_telefono_coincide_con_node(telefono, movil):
    assert (tipo_telefono(telefono) == 'Móvil') is movil


@pytest.mark.parametrize('sucio, limpio', CASOS['limpiar_dato'])
def test_limpiar_dato_coincide_con_node(sucio, limpio):
    assert limpiar_dato(sucio) == limpio


def test_nombre_comercial():
    assert nombre_comercial('REFORMAS DE LEVANTE - Reformas en Cartagena') == 'Reformas De Levante'
    assert nombre_comercial('Taller Pepe - Mecánica') == 'Taller Pepe'
