def test_rechaza_origenes_ajenos(env):
    r = env.client.get('/api/leads', headers={'Origin': 'https://evil.example'})

    assert r.status_code == 403


def test_peticion_que_cambia_estado_sin_origin_se_rechaza(env):
    r = env.client.patch('/api/leads/select-all', json={'selected': True}, headers={'Origin': ''})

    assert r.status_code == 403
    assert set(env.csv['selected']) == {'False'}


def test_lectura_sin_origin_se_permite(env):
    assert env.client.get('/api/status', headers={'Origin': ''}).status_code == 200


def test_rechaza_hosts_no_locales(env):
    r = env.client.get('/api/status', headers={'Host': 'evil.example'})

    assert r.status_code == 400
