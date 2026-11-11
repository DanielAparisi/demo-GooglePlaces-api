import json

import pytest

import calibrar
from comun import calibracion, rutas
from comun.oportunidad import PESOS_BASE, cargar_pesos, puntuar


def lead(llamada, movil=True, resenas='30', **extra):
    return {'Nombre del negocio': 'Taller X', 'Categoría': 'Taller mecánico',
            'Teléfono': '612 000 000' if movil else '968 000 000',
            'Reseñas': resenas, 'Valoración': '4.5', 'Llamada': llamada, **extra}


def historial(n_si=12, n_no=12):
    """Los móviles dicen que sí, los fijos que no: 'contacto' es lo que predice."""
    return [lead('Interesado', movil=True) for _ in range(n_si)] + \
           [lead('No interesado', movil=False) for _ in range(n_no)]


def test_estado_cuenta_solo_llamadas_con_resultado():
    leads = historial(2, 5) + [lead('No contesta'), lead('')]
    e = calibracion.estado(leads)
    assert (e['resultados'], e['interesados'], e['no_interesados']) == (7, 2, 5)
    assert not e['puede_calibrar']
    assert e['faltan'] == calibracion.MIN_RESULTADOS - 7


def test_sin_datos_suficientes_no_calibra():
    with pytest.raises(ValueError, match='Faltan llamadas'):
        calibracion.calibrar(historial(2, 30))  # solo 2 interesados


def test_sube_el_peso_de_lo_que_predice_y_suman_100():
    c = calibracion.calibrar(historial())
    assert c['pesos']['contacto'] > PESOS_BASE['contacto']
    assert sum(c['pesos'].values()) == pytest.approx(100, abs=0.5)
    assert c['detalle']['contacto']['media_interesados'] > c['detalle']['contacto']['media_no_interesados']
    # 'sector' es igual en ambos grupos: su multiplicador no cambia
    assert c['detalle']['sector']['multiplicador'] == 1


def test_baja_el_peso_de_lo_que_engana():
    leads = [lead('Interesado', resenas='0') for _ in range(12)] + [lead('No interesado', resenas='200') for _ in range(12)]
    c = calibracion.calibrar(leads)
    assert c['pesos']['demanda'] < PESOS_BASE['demanda']


def test_con_mas_llamadas_el_ajuste_es_mayor():
    poco = calibracion.calibrar(historial(12, 12))['detalle']['contacto']['multiplicador']
    mucho = calibracion.calibrar(historial(120, 120))['detalle']['contacto']['multiplicador']
    assert 1 < poco < mucho <= calibracion.MULT_MAX


def test_rendimiento_por_nivel():
    leads = [lead('Interesado', Email='a@b.es', Instagram='x'), lead('No interesado', movil=False, resenas='0')]
    filas = {f['nivel']: f for f in calibracion.rendimiento(leads)}
    total = sum(f['leads'] for f in filas.values())
    assert total == 2
    assert sum(f['interesados'] for f in filas.values()) == 1


def test_puntuar_usa_los_pesos_calibrados(tmp_path):
    ruta = tmp_path / 'pesos.json'
    c = calibracion.calibrar(historial())
    calibracion.guardar(ruta, c)
    pesos = cargar_pesos(ruta)
    assert pesos == c['pesos']
    movil = lead('', movil=True)
    fijo = lead('', movil=False)
    diferencia_base = puntuar(movil)['puntuacion'] - puntuar(fijo)['puntuacion']
    diferencia_nueva = puntuar(movil, pesos)['puntuacion'] - puntuar(fijo, pesos)['puntuacion']
    assert diferencia_nueva > diferencia_base


@pytest.mark.parametrize('contenido', ['no es json', '{"pesos": {"web": -5}}', '{"pesos": "x"}'])
def test_pesos_corruptos_vuelven_a_los_de_partida(tmp_path, contenido):
    ruta = tmp_path / 'pesos.json'
    ruta.write_text(contenido)
    assert cargar_pesos(ruta) == PESOS_BASE


def test_cli_calibra_guarda_y_reset(csv, monkeypatch, capsys):
    from comun import leads_csv
    import pandas as pd
    monkeypatch.setattr(rutas, 'CSV_FILE', csv)
    leads_csv.escribir(pd.DataFrame(historial()).fillna(''), csv)

    assert calibrar.main(['--simular']) == 0
    assert not rutas.PESOS_FILE.exists()

    assert calibrar.main([]) == 0
    assert json.loads(rutas.PESOS_FILE.read_text())['resultados'] == 24
    assert 'Guardado' in capsys.readouterr().out

    assert calibrar.main(['--reset']) == 0
    assert not rutas.PESOS_FILE.exists()
