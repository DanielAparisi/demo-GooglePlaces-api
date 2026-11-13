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


def test_maqueta_de_taller_usa_su_tema_y_sin_whatsapp_si_es_fijo(env, ia_caida):
    r = env.client.post('/api/leads/1/maqueta')  # Taller Pepe, teléfono fijo

    assert r.status_code == 200
    html = env.client.get(f"/maquetas/{r.json()['maqueta']}").text
    assert '--acento:#1d4ed8' in html and 'Taller mecánico en Murcia' in html
    assert 'Pide cita' in html and 'Horario de ejemplo' in html
    assert 'tel:968123456' in html and 'wa.me' not in html


def test_maqueta_de_reformas_con_movil_lleva_whatsapp(env, ia_caida):
    html = env.client.get(f"/maquetas/{env.client.post('/api/leads/0/maqueta').json()['maqueta']}").text

    assert 'https://wa.me/34612345678' in html and 'class="barra"' in html
    assert 'Antes y después' in html


def test_maqueta_de_fisio_sin_telefono_enlaza_sus_redes(env, ia_caida):
    html = env.client.get(f"/maquetas/{env.client.post('/api/leads/2/maqueta').json()['maqueta']}").text

    assert 'Reserva tu cita' in html and 'Su primera visita' in html
    assert 'https://instagram.com/fisio_sol' in html
    assert 'tel:' not in html and 'class="barra"' not in html


def test_maqueta_sin_landing_url_no_tiene_enlace_publico(env, ia_caida):
    r = env.client.post('/api/leads/0/maqueta').json()

    assert r['publica'] is None


def test_maqueta_publicada_tiene_enlace_estable_y_no_adivinable(env, ia_caida):
    from fastapi.testclient import TestClient

    from core.settings import Settings
    from main import create_app

    app = create_app(Settings(root=env.root, allowed_hosts=('testserver',), landing_url='https://agencia.test'))
    client = TestClient(app, headers={'Origin': 'http://localhost:4321'})

    url = client.post('/api/leads/0/maqueta').json()['publica']
    assert url.startswith('https://agencia.test/m/reformas-levante-') and url.endswith('.html')
    codigo = url.rsplit('-', 1)[1].removesuffix('.html')
    assert len(codigo) == 12 and codigo != '0'
    publicada = env.root / 'landing' / 'public' / 'm' / url.rsplit('/', 1)[1]
    assert 'noindex' in publicada.read_text(encoding='utf-8')

    assert client.post('/api/leads/0/maqueta').json()['publica'] == url  # regenerar no cambia el enlace
    lead = next(l for l in client.get('/api/leads').json() if l['id'] == 0)
    assert lead['maqueta_publica'] == url


@pytest.mark.parametrize('nombre', ['../Leads Google Maps.csv', '..%2Fsecreto.html', 'a.html.exe', 'A.html'])
def test_ver_maqueta_rechaza_rutas_raras(env, nombre):
    assert env.client.get(f'/maquetas/{nombre}').status_code == 404


def test_ver_maqueta_inexistente_es_404(env):
    assert env.client.get('/maquetas/no-existe.html').status_code == 404
