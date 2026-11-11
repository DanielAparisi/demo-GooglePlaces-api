import pandas as pd
import pytest

COLUMNAS = ['Nombre del negocio', 'Email', 'Categoría', 'Ubicación', 'Teléfono', 'Instagram', 'selected', 'enriched']


@pytest.fixture
def csv(tmp_path):
    """CSV de leads sintético en un directorio temporal."""
    ruta = tmp_path / 'Leads Google Maps.csv'
    filas = [
        ['Taller Pepe', '', 'Taller mecánico', 'C. Sol, 5, 30001 Murcia, Murcia, Spain', '968 123 456', '', 'False', ''],
        ['Fisio Mar', 'hola@fisiomar.test', 'Fisioterapia', 'Av. Mar, 3, 30500 Molina, Murcia, Spain', '612 000 000',
         'https://instagram.com/Fisio_Mar/', 'True', 'True'],
    ]
    pd.DataFrame(filas, columns=COLUMNAS).to_csv(ruta, index=False, encoding='utf-8-sig')
    return ruta


@pytest.fixture(autouse=True)
def sin_esperas(monkeypatch):
    monkeypatch.setattr('time.sleep', lambda *_: None)


@pytest.fixture(autouse=True)
def rutas_aisladas(tmp_path, monkeypatch):
    """Red de seguridad: ningún test puede leer ni escribir los datos reales del proyecto."""
    from comun import rutas
    datos = tmp_path / 'proyecto'
    datos.mkdir()
    for nombre in ['CSV_FILE', 'BAJAS_FILE', 'IG_SESSION_FILE', 'LOG_WHATSAPP', 'LOG_EMAIL',
                   'LOG_INSTAGRAM', 'USAGE_FILE', 'SEARCH_STATE_FILE', 'PESOS_FILE',
                   'ENTREGAS_FILE', 'LISTAS_DIR']:
        monkeypatch.setattr(rutas, nombre, datos / getattr(rutas, nombre).name)
