import threading
import time as real_time

import pytest

from comun import leads_csv

COLS = ['Nombre del negocio', 'Email', 'Categoría', 'Ubicación', 'Teléfono', 'Tipo teléfono']


def test_leer_mantiene_todo_como_texto(csv):
    df = leads_csv.leer(csv)
    assert df.loc[1, 'selected'] == 'True'          # no se convierte en bool
    assert df.loc[0, 'Teléfono'] == '968 123 456'
    assert df.loc[0, 'Email'] == ''                 # ni NaN


def test_editar_no_guarda_si_falla(csv):
    with pytest.raises(RuntimeError):
        with leads_csv.editar(csv) as df:
            df.at[0, 'Email'] = 'a medias'
            raise RuntimeError
    assert leads_csv.leer(csv).loc[0, 'Email'] == ''


def test_editar_conserva_permisos_y_no_deja_temporales(csv):
    csv.chmod(0o600)
    with leads_csv.editar(csv) as df:
        df.at[0, 'Email'] = 'x@y.test'
    assert csv.stat().st_mode & 0o777 == 0o600
    assert [p.name for p in csv.parent.glob('*.tmp')] == []


def test_anadir_no_duplica_ni_mueve_los_existentes(csv):
    nuevos = [
        {'Nombre del negocio': 'Taller Pepe', 'Ubicación': 'C. Sol, 5, 30001 Murcia, Murcia, Spain'},  # ya está
        {'Nombre del negocio': 'Reformas Ana', 'Ubicación': 'C. Luna, 1, 30001 Murcia, Murcia, Spain'},
        {'Nombre del negocio': 'Reformas Ana', 'Ubicación': 'C. Luna, 1, 30001 Murcia, Murcia, Spain'},  # repetido
    ]
    assert leads_csv.anadir(nuevos, COLS, csv) == 1
    df = leads_csv.leer(csv)
    assert list(df['Nombre del negocio']) == ['Taller Pepe', 'Fisio Mar', 'Reformas Ana']
    assert df.loc[1, 'selected'] == 'True'          # las columnas existentes se conservan


def test_anadir_crea_el_csv_si_no_existe(tmp_path):
    ruta = tmp_path / 'nuevo.csv'
    assert leads_csv.anadir([{'Nombre del negocio': 'A', 'Ubicación': 'B'}], COLS, ruta) == 1
    assert list(leads_csv.leer(ruta).columns) == COLS


def test_el_bloqueo_serializa_escrituras_concurrentes(csv, monkeypatch):
    """Dos editores a la vez: sin bloqueo, el segundo pisaría el cambio del primero."""
    monkeypatch.setattr('time.sleep', real_time.sleep)

    def marcar(col, valor):
        with leads_csv.editar(csv) as df:
            real_time.sleep(0.05)  # ventana en la que el otro hilo leería datos viejos
            df.at[0, col] = valor

    hilos = [threading.Thread(target=marcar, args=('Email', 'a@b.test')),
             threading.Thread(target=marcar, args=('enriched', 'True'))]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()

    fila = leads_csv.leer(csv).loc[0]
    assert fila['Email'] == 'a@b.test' and fila['enriched'] == 'True'


def test_bloqueo_reentrante_en_el_mismo_hilo(csv):
    with leads_csv.bloqueo(csv):
        with leads_csv.editar(csv) as df:   # no se queda esperando a sí mismo
            df.at[0, 'Email'] = 'ok@x.test'
    assert leads_csv.leer(csv).loc[0, 'Email'] == 'ok@x.test'


def test_localizar_usa_la_pista_y_si_no_busca(csv):
    df = leads_csv.leer(csv)
    assert leads_csv.localizar(df, 'Fisio Mar', 'Av. Mar, 3, 30500 Molina, Murcia, Spain', pista=1) == 1
    assert leads_csv.localizar(df, 'Fisio Mar', 'Av. Mar, 3, 30500 Molina, Murcia, Spain', pista=0) == 1
    assert leads_csv.localizar(df, 'No existe', '', pista=0) is None


@pytest.mark.parametrize('valor, esperado', [('True', True), ('true', True), ('1', True), ('yes', True),
                                             ('False', False), ('', False), (None, False)])
def test_esta_seleccionado(valor, esperado):
    assert leads_csv.esta_seleccionado(valor) is esperado
