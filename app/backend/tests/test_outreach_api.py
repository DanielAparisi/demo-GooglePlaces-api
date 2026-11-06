import pytest


class FakeProc:
    pid = 4242

    def poll(self):
        return None  # sigue en ejecución


@pytest.fixture
def popen(monkeypatch):
    lanzados = []

    def fake_popen(comando, cwd=None):
        lanzados.append(comando)
        return FakeProc()

    monkeypatch.setattr('services.outreach.subprocess.Popen', fake_popen)
    return lanzados


def seleccionar(env, *ids):
    env.client.patch('/api/leads/select', json={'ids': list(ids), 'selected': True})


def test_sin_seleccion_no_se_lanza_nada(env, popen):
    r = env.client.post('/api/whatsapp/launch')

    assert r.status_code == 400
    assert popen == []


def test_whatsapp_lanza_el_script_con_los_seleccionados(env, popen):
    seleccionar(env, 0, 1)

    r = env.client.post('/api/whatsapp/launch')

    assert r.status_code == 200
    assert r.json() == {'ok': True, 'pid': 4242, 'selected': 2}
    assert popen[0][0] == 'node' and popen[0][-1] == '--selected-only'


def test_email_cuenta_solo_los_seleccionados_con_email(env, popen):
    seleccionar(env, 0, 1)  # el lead 1 no tiene email

    r = env.client.post('/api/email/launch')

    assert r.json()['selected'] == 1


def test_email_falla_si_ninguno_tiene_email(env, popen):
    seleccionar(env, 1)

    r = env.client.post('/api/email/launch')

    assert r.status_code == 400 and 'email' in r.json()['detail']
    assert popen == []


def test_instagram_necesita_cuenta_de_instagram(env, popen):
    seleccionar(env, 0)
    assert env.client.post('/api/instagram/launch').status_code == 400

    seleccionar(env, 2)
    assert env.client.post('/api/instagram/launch').json()['selected'] == 1


def test_no_se_lanzan_dos_envios_del_mismo_canal_a_la_vez(env, popen):
    seleccionar(env, 0)
    assert env.client.post('/api/whatsapp/launch').status_code == 200

    r = env.client.post('/api/whatsapp/launch')

    assert r.status_code == 409
    assert len(popen) == 1


def test_canal_desconocido_es_422(env, popen):
    assert env.client.post('/api/telegram/launch').status_code == 422


def test_qr_no_existe_hasta_lanzar_whatsapp(env):
    assert env.client.get('/api/whatsapp/qr').status_code == 404

    (env.root / 'qr.png').write_bytes(b'\x89PNG')
    r = env.client.get('/api/whatsapp/qr')
    assert r.status_code == 200 and r.headers['cache-control'] == 'no-store'
