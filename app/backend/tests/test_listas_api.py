import json
from datetime import date

from services.listas import _mes_siguiente

PEDIDO = {'cliente': 'Agencia Sol', 'plan': 'basico', 'ciudades': ['Murcia']}


def test_resumen_sin_entregas_lista_los_planes(env):
    r = env.client.get('/api/listas').json()

    assert [p['id'] for p in r['planes']] == ['basico', 'estandar', 'premium']
    assert r['planes'][0]['precio'] == 80
    assert r['clientes'] == [] and r['entregas'] == []


def test_simular_no_registra_ni_exporta(env):
    r = env.client.post('/api/listas/simular', json=PEDIDO)

    assert r.status_code == 200
    body = r.json()
    assert body['pedido']['cantidad'] == 100 and body['pedido']['plan'] == 'basico'
    assert body['resumen']['entregados'] == 3
    assert body['resumen']['faltan'] == 97
    assert len(body['muestra']) == 3 and 'Negocio' in body['muestra'][0]
    assert not (env.root / 'entregas.json').exists()
    assert not (env.root / 'listas').exists()


def test_crear_exporta_registra_y_no_repite_leads(env):
    r = env.client.post('/api/listas', json=PEDIDO)

    assert r.status_code == 200
    archivo = r.json()['archivo']
    descarga = env.client.get(f'/api/listas/archivo/{archivo}')
    assert descarga.status_code == 200 and 'Negocio' in descarga.text

    resumen = env.client.get('/api/listas').json()
    cliente = resumen['clientes'][0]
    assert cliente['cliente'] == 'Agencia Sol' and cliente['plan'] == 'basico'
    assert cliente['entregas'] == 1 and cliente['leads'] == 3
    assert resumen['entregas'][0]['descargable'] is True

    # Mes siguiente: al mismo cliente no se le repiten los leads
    otra = env.client.post('/api/listas', json=PEDIDO)
    assert otra.status_code == 400


def test_premium_es_exclusivo(env):
    r = env.client.post('/api/listas/simular', json={'cliente': 'X', 'plan': 'premium'})

    assert r.json()['pedido']['exclusivo'] is True
    assert r.json()['pedido']['cantidad'] == 500


def test_pedido_sin_plan_ni_cantidad_es_400(env):
    assert env.client.post('/api/listas/simular', json={'cliente': 'X'}).status_code == 400
    assert env.client.post('/api/listas/simular', json={'cliente': 'X', 'plan': 'oro'}).status_code == 400


def test_registro_danado_es_409(env):
    (env.root / 'entregas.json').write_text('{roto', encoding='utf-8')

    assert env.client.get('/api/listas').status_code == 409
    assert env.client.post('/api/listas', json=PEDIDO).status_code == 409


def test_descarga_no_sale_de_la_carpeta_de_listas(env):
    (env.root / 'listas').mkdir()
    (env.root / 'secreto.csv').write_text('x', encoding='utf-8')

    assert env.client.get('/api/listas/archivo/..%2Fsecreto.csv').status_code == 404
    assert env.client.get('/api/listas/archivo/no-existe.csv').status_code == 404


def test_proxima_entrega_es_al_mes_siguiente(env):
    (env.root / 'entregas.json').write_text(json.dumps({'entregas': [
        {'id': 'a', 'cliente': 'A', 'fecha': '2026-01-31', 'exclusivo': False,
         'pedido': {'plan': 'estandar'}, 'archivo': '', 'leads': [['n', 'u']]},
    ]}), encoding='utf-8')

    c = env.client.get('/api/listas').json()['clientes'][0]

    assert c['proxima'] == '2026-02-28'
    assert _mes_siguiente(date(2026, 12, 15)) == date(2027, 1, 15)
