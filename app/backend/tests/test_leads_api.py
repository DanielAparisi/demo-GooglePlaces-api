def test_listar_devuelve_los_mas_recientes_primero_con_campos_calculados(env):
    leads = env.client.get('/api/leads').json()

    assert [l['id'] for l in leads] == [2, 1, 0]
    por_id = {l['id']: l for l in leads}
    assert por_id[0]['sector'] == 'reformas'
    assert por_id[0]['Tipo teléfono'] == 'Móvil'
    assert por_id[1]['Tipo teléfono'] == 'Fijo'
    assert por_id[2]['Tipo teléfono'] == ''


def test_listar_marca_emails_ya_enviados(env):
    env.write_log('email', [{'email': ' obras@example.test '}])

    por_id = {l['id']: l for l in env.client.get('/api/leads').json()}

    assert por_id[0]['email_enviado'] is True
    assert por_id[2]['email_enviado'] is False


def test_seleccionar_por_id_actualiza_el_csv(env):
    r = env.client.patch('/api/leads/select', json={'ids': [0, 2], 'selected': True})

    assert r.status_code == 200
    assert list(env.csv['selected']) == ['True', 'False', 'True']


def test_seleccionar_ignora_ids_inexistentes(env):
    r = env.client.patch('/api/leads/select', json={'ids': [99], 'selected': True})

    assert r.status_code == 200
    assert set(env.csv['selected']) == {'False'}


def test_seleccionar_todos_y_limpiar(env):
    env.client.patch('/api/leads/select-all', json={'selected': True})
    assert set(env.csv['selected']) == {'True'}

    env.client.patch('/api/leads/select-all', json={'selected': False})
    assert set(env.csv['selected']) == {'False'}


def test_seleccionar_sin_email_previo(env):
    env.write_log('email', [{'email': 'obras@example.test'}])

    r = env.client.patch('/api/leads/select-not-emailed')

    # Lead 0 ya recibió email, lead 1 no tiene email: solo queda el 2
    assert r.json() == {'ok': True, 'selected': 1}
    assert list(env.csv['selected']) == ['False', 'False', 'True']


def test_actualizar_llamada_guarda_estado_y_fecha(env):
    r = env.client.patch('/api/leads/1/llamada', json={'estado': 'Interesado'})

    assert r.status_code == 200
    fila = env.csv.loc[1]
    assert fila['Llamada'] == 'Interesado'
    assert fila['Fecha llamada'] != ''


def test_deshacer_llamada_limpia_la_fecha(env):
    env.client.patch('/api/leads/1/llamada', json={'estado': 'Interesado'})
    env.client.patch('/api/leads/1/llamada', json={'estado': ''})

    fila = env.csv.loc[1]
    assert fila['Llamada'] == '' and fila['Fecha llamada'] == ''


def test_llamada_con_estado_invalido_es_400(env):
    r = env.client.patch('/api/leads/1/llamada', json={'estado': 'Compra ya'})

    assert r.status_code == 400
    assert env.csv.loc[1]['Llamada'] == ''


def test_llamada_de_lead_inexistente_es_404(env):
    r = env.client.patch('/api/leads/99/llamada', json={'estado': 'Interesado'})

    assert r.status_code == 404


def test_status_cuenta_los_envios_de_cada_canal(env):
    env.write_log('whatsapp', [{'n': 1}, {'n': 2}])
    env.write_log('email', [{'email': 'a'}])

    assert env.client.get('/api/status').json() == {'enviados': 2, 'emails_enviados': 1, 'ig_enviados': 0}


def test_status_tolera_un_log_a_medio_escribir(env):
    (env.root / 'email_log.json').write_text('{"enviados": [', encoding='utf-8')

    assert env.client.get('/api/status').json()['emails_enviados'] == 0
