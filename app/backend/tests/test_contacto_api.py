import pytest


@pytest.fixture
def ia_caida(monkeypatch):
    """La IA falla: guion y maqueta deben salir igualmente con sus plantillas."""
    def falla():
        raise RuntimeError('sin IA')

    monkeypatch.setattr('services.guion.groq', falla)
    monkeypatch.setattr('services.maqueta.groq', falla)


def test_guion_usa_plantilla_si_la_ia_falla_y_se_guarda(env, ia_caida):
    r = env.client.post('/api/leads/0/guion')

    assert r.status_code == 200
    guion = r.json()['guion']
    assert 'APERTURA' in guion and 'Reformas Levante' in guion
    assert r.json()['sector'] == 'reformas'
    assert env.csv.loc[0]['Guion'] == guion


def test_guion_no_pisa_la_seleccion_hecha_mientras_se_generaba(env, monkeypatch):
    def groq_que_cambia_el_csv():
        env.client.patch('/api/leads/select', json={'ids': [1], 'selected': True})
        raise RuntimeError('sin IA')

    monkeypatch.setattr('services.guion.groq', groq_que_cambia_el_csv)

    env.client.post('/api/leads/0/guion')

    assert env.csv.loc[1]['selected'] == 'True'


def test_guion_de_lead_inexistente_es_404(env, ia_caida):
    assert env.client.post('/api/leads/99/guion').status_code == 404


def test_maqueta_de_reformas_se_genera_con_textos_genericos(env, ia_caida):
    r = env.client.post('/api/leads/0/maqueta')

    assert r.status_code == 200
    archivo = r.json()['maqueta']
    assert archivo == 'reformas-levante-0.html'
    assert env.csv.loc[0]['Maqueta'] == archivo

    html = env.client.get(f'/maquetas/{archivo}').text
    assert 'noindex' in html and 'No es su web oficial' in html


def test_maqueta_de_sector_sin_plantilla_es_400(env, ia_caida):
    r = env.client.post('/api/leads/1/maqueta')  # taller

    assert r.status_code == 400 and 'plantilla' in r.json()['detail']


@pytest.mark.parametrize('nombre', ['../Leads Google Maps.csv', '..%2Fsecreto.html', 'a.html.exe', 'A.html'])
def test_ver_maqueta_rechaza_rutas_raras(env, nombre):
    assert env.client.get(f'/maquetas/{nombre}').status_code == 404


def test_ver_maqueta_inexistente_es_404(env):
    assert env.client.get('/maquetas/no-existe.html').status_code == 404
