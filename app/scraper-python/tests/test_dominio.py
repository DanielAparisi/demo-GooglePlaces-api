import pytest

from comun.dominio import ciudad_de, nombre_comercial


@pytest.mark.parametrize('ubicacion, ciudad', [
    ('C. Mayor, 1, 30201 Cartagena, Murcia, Spain', 'Cartagena'),
    ('C. Delicias, 5, Arganzuela, 28005 Madrid, Spain', 'Madrid'),       # con barrio
    ('Carrer Major, 2, 08901 L\'Hospitalet de Llobregat, Barcelona, Spain', "L'Hospitalet de Llobregat"),
    ('Calle Gran Vía, 10, 48001 Bilbao, Bizkaia, Spain', 'Bilbao'),       # no la provincia
    ('C. Alcalá, 1, 28014 Madrid, Spain', 'Madrid'),                       # 4 partes
    ('Madrid, Spain', 'Madrid'),                                           # sin código postal
    ('Sevilla', 'Sevilla'),
    ('', ''),
    (None, ''),
])
def test_ciudad_de(ubicacion, ciudad):
    assert ciudad_de(ubicacion) == ciudad


def test_nombre_comercial():
    assert nombre_comercial('REFORMAS DE LEVANTE - Reformas en Cartagena') == 'Reformas De Levante'
    assert nombre_comercial('Taller Pepe - Mecánica') == 'Taller Pepe'
