import json
import random

import pytest

import script
from comun import leads_csv


class FakeResp:
    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data


@pytest.fixture
def places(monkeypatch):
    """Simula la API: `respuestas` mapea place_id (o 'search') → JSON devuelto."""
    respuestas = {}

    def fake_get(url, params, timeout):
        clave = params.get('place_id', 'search')
        r = respuestas[clave]
        if isinstance(r, Exception):
            raise r
        return FakeResp(r)

    monkeypatch.setattr('script.requests.get', fake_get)
    return respuestas


def ok(**result):
    return {'status': 'OK', 'result': result}


def test_busqueda_rechazada_lanza_error_en_vez_de_devolver_vacio(places):
    places['search'] = {'status': 'REQUEST_DENIED', 'error_message': 'API key inválida'}
    with pytest.raises(script.PlacesError, match='REQUEST_DENIED'):
        script.buscar('taller en Murcia', 'k')


def test_busqueda_sin_resultados_es_lista_vacia(places):
    places['search'] = {'status': 'ZERO_RESULTS', 'results': []}
    assert script.buscar('taller en Murcia', 'k') == []


def test_revisar_filtra_con_web_y_sin_nombre(places):
    places['a'] = ok(name='Taller A', formatted_address='X', formatted_phone_number='968 000 000')
    places['b'] = ok(name='Con web', website='https://b.test')
    places['c'] = {'status': 'NOT_FOUND'}
    places['d'] = ok(formatted_address='sin nombre')

    resultados, sin_revisar = script.revisar(['a', 'b', 'c', 'd'], 'Taller mecánico', 'k')

    assert [r['Nombre del negocio'] for r in resultados] == ['Taller A']
    assert resultados[0]['Tipo teléfono'] == 'Fijo'
    assert sin_revisar == []


def test_web_que_es_solo_una_red_social_sigue_siendo_lead(places):
    places['a'] = ok(name='Fisio Ana', website='https://www.facebook.com/fisioana', user_ratings_total=40,
                     rating=4.8, business_status='OPERATIONAL', photos=[{}] * 6, opening_hours={'open_now': True})
    places['b'] = ok(name='Taller Cerrado', business_status='CLOSED_PERMANENTLY')

    resultados, _ = script.revisar(['a', 'b'], 'Fisioterapia', 'k')

    assert len(resultados) == 1
    lead = resultados[0]
    assert lead['Web actual'] == 'https://www.facebook.com/fisioana'
    assert (lead['Reseñas'], lead['Valoración'], lead['Horario'], lead['Fotos']) == ('40', '4.8', 'True', '6')


def test_revisar_para_ante_un_error_y_devuelve_lo_que_falta(places):
    places['a'] = ok(name='Taller A', formatted_address='X')
    places['b'] = {'status': 'OVER_QUERY_LIMIT'}

    resultados, sin_revisar = script.revisar(['a', 'b', 'c'], 'Taller', 'k')

    assert len(resultados) == 1
    assert sin_revisar == ['b', 'c']


def test_limite_diario(tmp_path):
    uso = tmp_path / 'usage.json'
    for _ in range(script.LIMITE_DIARIO):
        assert script.consumir_busqueda_diaria(uso, hoy='2026-11-06')
    assert not script.consumir_busqueda_diaria(uso, hoy='2026-11-06')
    assert script.consumir_busqueda_diaria(uso, hoy='2026-11-07')  # nuevo día
    assert json.loads(uso.read_text()) == {'fecha': '2026-11-07', 'contador': 1}


def test_elegir_busqueda_no_repite(monkeypatch):
    hechas = [f'{t} en {c}' for t in script.TIPOS_NEGOCIO for c in script.CIUDADES]
    libre = hechas.pop(5)
    tipo, ciudad = script.elegir_busqueda({'hechas': hechas}, rng=random.Random(1))
    assert f'{tipo} en {ciudad}' == libre


def test_main_guarda_lo_encontrado_y_deja_el_resto_en_cola(places, csv, tmp_path, monkeypatch):
    estado = tmp_path / 'search_state.json'
    estado.write_text(json.dumps({'place_ids_pendientes': ['a', 'b'], 'tipo': 'taller mecánico', 'hechas': []}))
    monkeypatch.setattr('comun.rutas.SEARCH_STATE_FILE', estado)
    monkeypatch.setattr('comun.rutas.CSV_FILE', csv)
    monkeypatch.setenv('GOOGLE_PLACES_API_KEY', 'k')
    places['a'] = ok(name='Taller Nuevo', formatted_address='C. X, 1, 30001 Murcia, Spain', formatted_phone_number='612 111 222')
    places['b'] = {'status': 'OVER_QUERY_LIMIT'}

    assert script.main(['--cola']) == 1

    nombres = list(leads_csv.leer(csv)['Nombre del negocio'])
    assert nombres == ['Taller Pepe', 'Fisio Mar', 'Taller Nuevo']
    assert json.loads(estado.read_text())['place_ids_pendientes'] == ['b']
