import pytest

from comun.oportunidad import necesita_web, nivel, puntuar, tipo_web


@pytest.mark.parametrize('url, esperado', [
    ('', ''),
    (None, ''),
    ('https://www.facebook.com/tallerpepe', 'debil'),
    ('https://instagram.com/fisio_mar', 'debil'),
    ('https://linktr.ee/reformasx', 'debil'),
    ('https://tallerpepe.business.site/', 'debil'),
    ('https://www.doctoralia.es/clinica-x', 'debil'),
    ('https://www.tallerpepe.es', 'propia'),
])
def test_tipo_web(url, esperado):
    assert tipo_web(url) == esperado
    assert necesita_web(url) == (esperado != 'propia')


def lead(**campos):
    base = {'Nombre del negocio': 'Fisio Mar', 'Categoría': 'Fisioterapia'}
    return {**base, **campos}


def test_lead_ideal_es_prioridad_alta():
    r = puntuar(lead(**{'Web actual': '', 'Reseñas': '150', 'Valoración': '4.8', 'Horario': 'True',
                        'Fotos': '10', 'Teléfono': '612 000 000', 'Email': 'a@b.es',
                        'Instagram': 'https://instagram.com/x'}))
    assert r['puntuacion'] == 100
    assert r['nivel'] == 'Alta'
    assert 'No tiene página web' in r['motivos']
    assert 'Móvil: contactable por WhatsApp' in r['motivos']


def test_negocio_sin_actividad_es_prioridad_baja():
    r = puntuar(lead(**{'Nombre del negocio': 'Bar X', 'Categoría': 'Bar', 'Reseñas': '0', 'Horario': 'False',
                        'Fotos': '0', 'Teléfono': ''}))
    assert r['nivel'] == 'Baja'
    assert 'Sin reseñas: poca actividad visible' in r['motivos']


def test_web_propia_o_negocio_cerrado_puntua_cero():
    assert puntuar(lead(**{'Web actual': 'https://fisiomar.es'}))['puntuacion'] == 0
    assert puntuar(lead(**{'Estado negocio': 'CLOSED_PERMANENTLY'}))['puntuacion'] == 0


def test_web_debil_puntua_menos_que_sin_web():
    datos = {'Reseñas': '30', 'Valoración': '4.5', 'Teléfono': '612 000 000'}
    sin_web = puntuar(lead(**datos))['puntuacion']
    debil = puntuar(lead(**datos, **{'Web actual': 'https://facebook.com/fisiomar'}))['puntuacion']
    assert sin_web - debil == 10


def test_mas_resenas_mas_puntuacion():
    puntos = [puntuar(lead(**{'Reseñas': str(n), 'Valoración': '4.5'}))['puntuacion'] for n in (1, 10, 50, 200)]
    assert puntos == sorted(puntos) and puntos[0] < puntos[-1]


def test_datos_desconocidos_puntuan_la_mitad_no_cero():
    """Un lead antiguo (sin columnas de Places) no debe quedar por debajo de uno sin reseñas."""
    antiguo = puntuar(lead(**{'Teléfono': '968 000 000'}))['puntuacion']
    sin_nada = puntuar(lead(**{'Teléfono': '968 000 000', 'Reseñas': '0', 'Horario': 'False', 'Fotos': '0'}))['puntuacion']
    assert antiguo > sin_nada


def test_admite_valores_nulos_y_basura():
    r = puntuar({'Nombre del negocio': None, 'Reseñas': 'abc', 'Valoración': None, 'Email': None})
    assert 0 <= r['puntuacion'] <= 100


@pytest.mark.parametrize('p, esperado', [(100, 'Alta'), (70, 'Alta'), (69, 'Media'), (45, 'Media'), (44, 'Baja')])
def test_nivel(p, esperado):
    assert nivel(p) == esperado
