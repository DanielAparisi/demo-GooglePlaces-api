import csv as csv_mod  # 'csv' es el fixture del CSV de leads

import pandas as pd
import pytest

import crear_lista
import script
from comun import leads_csv, listas, rutas


def lead(nombre, ciudad='30001 Murcia', categoria='Taller mecánico', movil=True, **extra):
    return {'Nombre del negocio': nombre, 'Categoría': categoria, 'Ubicación': f'C/ Mayor 1, {ciudad}, Spain',
            'Teléfono': '612 000 000' if movil else '968 000 000',
            'Tipo teléfono': 'Móvil' if movil else 'Fijo', **extra}


def pedido(**campos):
    return {'cliente': 'Agencia Sol', 'cantidad': 10, **campos}


# ── Filtros ───────────────────────────────────────────────────────────────────

@pytest.mark.parametrize('ubicacion, ciudad, esperado', [
    ('C/ X, 03201 Elx, Alacant, Spain', 'Elche', 'Elche'),
    ("C/ X, 08901 L'Hospitalet de Llobregat, Barcelona, Spain", 'Hospitalet', 'Hospitalet'),
    ('C/ X, 28914 Leganés, Madrid, Spain', 'leganes', 'leganes'),
    ('C/ X, Villaverde, 28021 Madrid, Spain', 'Madrid', 'Madrid'),
    ('C/ X, 30500 Molina de Segura, Murcia, Spain', 'Murcia', 'Murcia'),  # provincia
    ('C/ X, 30001 Murcia, Spain', 'Madrid', None),
    ('C/ Elcheros, 30001 Murcia, Spain', 'Elche', None),  # palabra dentro de otra
])
def test_zona_de(ubicacion, ciudad, esperado):
    assert listas.zona_de({'Ubicación': ubicacion}, [ciudad]) == esperado


def test_encaja_sector_por_sector_detectado_categoria_o_nombre():
    assert listas.encaja_sector(lead('Talleres Pepe', categoria='Negocio'), ['taller'])
    assert listas.encaja_sector(lead('Obrador Sol', categoria='Panadería'), ['panaderia'])
    assert not listas.encaja_sector(lead('Bar Sol', categoria='Bar'), ['taller'])
    assert listas.encaja_sector(lead('Bar Sol', categoria='Bar'), [])


# ── Algoritmo ─────────────────────────────────────────────────────────────────

def test_filtra_por_sector_ciudad_y_canal():
    leads = [lead('Taller A'), lead('Taller Fijo', movil=False), lead('Taller Madrid', ciudad='28001 Madrid'),
             lead('Bar Murcia', categoria='Bar')]
    r = listas.crear_lista(leads, pedido(sectores=['taller'], ciudades=['Murcia'], requiere=['movil']))
    assert [l['Nombre del negocio'] for l in r['leads']] == ['Taller A']
    assert r['resumen']['descartes']['sin_canal'] == 1
    assert r['resumen']['faltan'] == 9
    assert 'taller mecánico en Murcia' in r['sugerencias']


def test_ordena_por_puntuacion():
    leads = [lead('Sin datos', movil=False), lead('Completo', Email='a@b.es', Instagram='x', **{'Reseñas': '150', 'Valoración': '4.9'})]
    r = listas.crear_lista(leads, pedido(cantidad=2))
    assert [l['Nombre del negocio'] for l in r['leads']] == ['Completo', 'Sin datos']
    assert r['leads'][0]['_puntuacion'] > r['leads'][1]['_puntuacion']


def test_puntuacion_minima_y_descartes():
    leads = [lead('Malo', movil=False, **{'Reseñas': '0'}), lead('Con web', **{'Web actual': 'https://x.es'}),
             lead('Mío', Llamada='Interesado'), lead('Bueno', Email='a@b.es')]
    r = listas.crear_lista(leads, pedido(puntuacion_min=60))
    assert [l['Nombre del negocio'] for l in r['leads']] == ['Bueno']
    d = r['resumen']['descartes']
    assert (d['puntuacion_baja'], d['en_tu_cartera'], d['no_encajan']) == (1, 1, 1)


def test_reparte_entre_grupos():
    leads = [lead(f'Murcia {i}', Email='a@b.es') for i in range(5)] + \
            [lead(f'Lorca {i}', ciudad='30800 Lorca') for i in range(5)]
    r = listas.crear_lista(leads, pedido(cantidad=4, ciudades=['Murcia', 'Lorca']))
    assert r['resumen']['por_grupo'] == {'Taller mecánico · Murcia': 2, 'Taller mecánico · Lorca': 2}


def test_no_repite_al_mismo_cliente_y_respeta_exclusividad(tmp_path):
    ruta = tmp_path / 'entregas.json'
    leads = [lead(f'Taller {i}') for i in range(4)]

    primera = listas.crear_lista(leads, pedido(cantidad=2))
    listas.registrar_entrega(ruta, primera)
    segunda = listas.crear_lista(leads, pedido(cantidad=4), listas.leer_entregas(ruta))
    assert len(segunda['leads']) == 2
    assert not {listas.clave(l) for l in primera['leads']} & {listas.clave(l) for l in segunda['leads']}
    assert segunda['resumen']['descartes']['ya_entregados'] == 2

    # Otra agencia sí puede recibir los no exclusivos...
    otra = listas.crear_lista(leads, pedido(cliente='Agencia Luna', cantidad=4), listas.leer_entregas(ruta))
    assert len(otra['leads']) == 4
    # ...pero un pedido exclusivo solo lleva leads nunca vendidos
    excl = listas.crear_lista(leads, pedido(cliente='Agencia Luna', cantidad=4, exclusivo=True), listas.leer_entregas(ruta))
    assert len(excl['leads']) == 2
    listas.registrar_entrega(ruta, excl)
    # y lo vendido en exclusiva ya no le llega a nadie más
    tercera = listas.crear_lista(leads, pedido(cliente='Agencia Mar', cantidad=4), listas.leer_entregas(ruta))
    assert len(tercera['leads']) == 2
    assert tercera['resumen']['descartes']['exclusivos_de_otro'] == 2


def test_pedido_invalido():
    with pytest.raises(ValueError, match='cliente'):
        listas.crear_lista([], {'cantidad': 5})
    with pytest.raises(ValueError, match='cantidad'):
        listas.crear_lista([], {'cliente': 'X', 'cantidad': 0})
    with pytest.raises(ValueError, match='Canal'):
        listas.crear_lista([], pedido(requiere=['fax']))


def test_registro_danado_para_en_vez_de_ignorarlo(tmp_path):
    ruta = tmp_path / 'entregas.json'
    ruta.write_text('{roto')
    with pytest.raises(ValueError, match='dañado'):
        listas.leer_entregas(ruta)


def test_sugerencias_no_repiten_busquedas_hechas():
    s = listas.sugerir_busquedas(['taller', 'fisioterapia'], ['Vigo'], hechas=['taller mecánico en Vigo'])
    assert s == ['fisioterapia en Vigo']


def test_sectores_de_busqueda_coinciden_con_el_scraper():
    assert set(listas.BUSQUEDA_SECTOR.values()) <= set(script.TIPOS_NEGOCIO)


def test_filas_entrega_sin_columnas_internas():
    leads = [lead('TALLER PEPE - Mecánica rápida', Guion='secreto', Mensaje='hola', selected='True')]
    filas = listas.filas_entrega(listas.crear_lista(leads, pedido()))
    assert list(filas[0]) == listas.COLUMNAS_ENTREGA
    assert filas[0]['Negocio'] == 'Taller Pepe'
    assert filas[0]['Por qué']
    assert 'secreto' not in str(filas)


# ── CLI ───────────────────────────────────────────────────────────────────────

def test_cli_exporta_registra_y_no_repite(csv, monkeypatch, capsys):
    monkeypatch.setattr(rutas, 'CSV_FILE', csv)
    leads_csv.escribir(pd.DataFrame([lead(f'Taller {i}') for i in range(3)]).fillna(''), csv)

    assert crear_lista.main(['--cliente', 'Agencia Sol', '--cantidad', '2', '--simular']) == 0
    assert not rutas.ENTREGAS_FILE.exists()

    assert crear_lista.main(['--cliente', 'Agencia Sol', '--cantidad', '2']) == 0
    exportado = rutas.LISTAS_DIR / 'agencia-sol-2-leads.csv'
    with open(exportado, encoding='utf-8-sig') as f:
        filas = list(csv_mod.DictReader(f))
    assert len(filas) == 2 and filas[0]['Oportunidad']

    assert crear_lista.main(['--cliente', 'Agencia Sol', '--plan', 'basico']) == 0
    salida = capsys.readouterr().out
    assert '1/100 leads' in salida and 'Faltan 99' in salida
    assert len(listas.leer_entregas(rutas.ENTREGAS_FILE)) == 2

    assert crear_lista.main(['--entregas']) == 0
    assert 'Agencia Sol' in capsys.readouterr().out

