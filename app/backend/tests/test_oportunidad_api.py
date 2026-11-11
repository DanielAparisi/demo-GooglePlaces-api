import pandas as pd


def _con_llamadas(env, n_si=12, n_no=12):
    """Reescribe el CSV: móviles interesados, fijos no interesados."""
    filas = [{'Nombre del negocio': f'Taller {i}', 'Categoría': 'Taller', 'Ubicación': f'C/ {i}',
              'Teléfono': '612 000 000' if i < n_si else '968 000 000', 'Email': '', 'selected': 'False',
              'Llamada': 'Interesado' if i < n_si else 'No interesado'} for i in range(n_si + n_no)]
    pd.DataFrame(filas).to_csv(env.root / 'Leads Google Maps.csv', index=False, encoding='utf-8-sig')


def test_resumen_sin_calibrar(env):
    r = env.client.get('/api/oportunidad').json()
    assert r['calibrado'] is None
    assert r['estado']['puede_calibrar'] is False
    assert {b['id'] for b in r['bloques']} >= {'web', 'contacto', 'sector'}
    assert all(b['peso'] == b['peso_base'] for b in r['bloques'])
    assert [f['nivel'] for f in r['rendimiento']] == ['Alta', 'Media', 'Baja']


def test_calibrar_sin_datos_es_400(env):
    r = env.client.post('/api/oportunidad/calibrar')
    assert r.status_code == 400
    assert 'Faltan llamadas' in r.json()['detail']
    assert not (env.root / 'pesos_oportunidad.json').exists()


def test_calibrar_guarda_y_cambia_las_puntuaciones(env):
    _con_llamadas(env)
    antes = {l['id']: l['oportunidad'] for l in env.client.get('/api/leads').json()}

    r = env.client.post('/api/oportunidad/calibrar')
    assert r.status_code == 200
    datos = r.json()
    assert datos['calibrado']['resultados'] == 24
    contacto = next(b for b in datos['bloques'] if b['id'] == 'contacto')
    assert contacto['peso'] > contacto['peso_base']

    despues = {l['id']: l['oportunidad'] for l in env.client.get('/api/leads').json()}
    assert despues != antes

    r = env.client.delete('/api/oportunidad/calibrar')
    assert r.json()['calibrado'] is None
    assert not (env.root / 'pesos_oportunidad.json').exists()


def test_calibrar_exige_origin(env):
    from fastapi.testclient import TestClient
    sin_origin = TestClient(env.app)
    assert sin_origin.post('/api/oportunidad/calibrar').status_code == 403
