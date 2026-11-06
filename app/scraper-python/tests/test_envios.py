import json

import pandas as pd
import pytest

import send_emails
import send_instagram
from comun import rutas
from comun.envios import PIE_BAJA, LogEnvios, cargar_bajas


@pytest.fixture
def ia_caida(monkeypatch):
    def falla(*a, **k):
        raise RuntimeError('sin IA')
    monkeypatch.setattr('comun.ia.generar', falla)


def leads(*filas):
    cols = ['Nombre del negocio', 'Email', 'Instagram', 'Ubicación', 'Categoría', 'selected']
    return pd.DataFrame([dict(zip(cols, f)) for f in filas], columns=cols).fillna('')


# ── Log y bajas ───────────────────────────────────────────────────────────────

def test_log_compara_sin_mayusculas_ni_espacios(tmp_path):
    ruta = tmp_path / 'email_log.json'
    ruta.write_text(json.dumps({'enviados': [{'email': ' Info@Pepe.es '}]}))
    log = LogEnvios(ruta)
    assert log.ya_enviados('email') == {'info@pepe.es'}
    assert log.datos['fallidos'] == []


def test_log_se_guarda_tras_cada_envio(tmp_path):
    ruta = tmp_path / 'log.json'
    LogEnvios(ruta).enviado(email='a@b.test')
    assert json.loads(ruta.read_text())['enviados'][0]['email'] == 'a@b.test'


def test_cargar_bajas(tmp_path):
    ruta = tmp_path / 'bajas.txt'
    ruta.write_text('# pedidas por email\nInfo@Pepe.es\n\n@Fisio_Mar  # por DM\n')
    assert cargar_bajas(ruta) == {'info@pepe.es', 'fisio_mar'}
    assert cargar_bajas(tmp_path / 'no-existe.txt') == set()


# ── Email ─────────────────────────────────────────────────────────────────────

def test_email_un_envio_por_direccion_y_respeta_log_bajas_y_seleccion():
    df = leads(
        ('A', 'a@x.test', '', '', '', 'True'),
        ('A bis', 'A@X.test ', '', '', '', 'True'),   # mismo email en otra fila
        ('B', 'b@x.test', '', '', '', 'True'),        # ya enviado
        ('C', 'c@x.test', '', '', '', 'True'),        # pidió la baja
        ('D', 'd@x.test', '', '', '', 'False'),       # no seleccionado
        ('E', '', '', '', '', 'True'),                # sin email
    )
    pendientes = send_emails.seleccionar_pendientes(df, {'b@x.test'}, {'c@x.test'}, solo_seleccionados=True)
    assert [p['Nombre del negocio'] for p in pendientes] == ['A']


def test_email_siempre_lleva_pie_de_baja(monkeypatch):
    monkeypatch.setattr('comun.ia.generar', lambda *a, **k: 'Asunto: Hola\nCuerpo generado por IA')
    asunto, cuerpo = send_emails.redactar({'Nombre del negocio': 'Taller Pepe', 'Ubicación': ''})
    assert asunto == 'Hola'
    assert cuerpo.endswith(PIE_BAJA)


def test_email_plantilla_si_la_ia_falla(ia_caida):
    asunto, cuerpo = send_emails.redactar({'Nombre del negocio': 'TALLER PEPE - Mecánica', 'Ubicación': ''})
    assert asunto == 'Una web para Taller Pepe'
    assert cuerpo.count(PIE_BAJA) == 1


def test_parsear_asunto_y_cuerpo():
    assert send_emails.parsear_asunto_y_cuerpo('Asunto: Hola\n\nCuerpo') == ('Hola', 'Cuerpo')
    assert send_emails.parsear_asunto_y_cuerpo('Solo cuerpo')[0] == send_emails.ASUNTO_POR_DEFECTO


def test_dry_run_no_envia_ni_escribe_log(csv, tmp_path, monkeypatch, ia_caida, capsys):
    monkeypatch.setattr('comun.rutas.CSV_FILE', csv)
    monkeypatch.setattr('send_emails.Gmail', lambda *a: pytest.fail('no debe conectarse'))

    assert send_emails.main(['--dry-run']) == 0
    assert 'hola@fisiomar.test' in capsys.readouterr().out
    assert not rutas.LOG_EMAIL.exists()


# ── Instagram ─────────────────────────────────────────────────────────────────

@pytest.mark.parametrize('valor, username', [
    ('https://www.instagram.com/Fisio_Mar/', 'fisio_mar'),
    ('instagram.com/fisio.mar?hl=es', 'fisio.mar'),
    ('@FisioMar', 'fisiomar'),
    ('fisiomar', 'fisiomar'),
    ('https://instagram.com/p/Cx123/', None),          # una publicación, no un perfil
    ('https://instagram.com/explore', None),
    ('', None),
])
def test_extraer_username(valor, username):
    assert send_instagram.extraer_username(valor) == username


def test_instagram_una_vez_por_cuenta():
    df = leads(
        ('A', '', 'https://instagram.com/Pepe', '', '', 'True'),
        ('A bis', '', '@pepe', '', '', 'True'),
        ('B', '', '@ya_escrito', '', '', 'True'),
        ('C', '', '@de_baja', '', '', 'True'),
    )
    pendientes = send_instagram.seleccionar_pendientes(df, {'ya_escrito'}, {'de_baja'}, solo_seleccionados=True)
    assert [u for _, u in pendientes] == ['pepe']


def test_instagram_plantilla_si_la_ia_falla(ia_caida):
    msg = send_instagram.redactar({'Nombre del negocio': 'Fisio Mar', 'Ubicación': 'Av. Mar, 3, 30500 Molina, Spain'})
    assert 'Fisio Mar en Molina' in msg
