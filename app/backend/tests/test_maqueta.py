"""Plantilla de maquetas: datos reales, honestidad y escapado (sin IA)."""
import json

import pytest

from services import maqueta

TEXTOS = {
    'eslogan': 'Eslogan', 'intro': 'Intro',
    'servicios': [{'titulo': 'S', 'texto': 'T', 'icono': 'check'}] * 3,
    'ventajas': [{'titulo': 'V', 'texto': 'T', 'icono': 'check'}] * 3,
}


def lead(**extra):
    return {'Nombre del negocio': 'Taller Pepe', 'Categoría': 'Taller', 'Teléfono': '612 345 678',
            'Tipo teléfono': 'Móvil', 'Ubicación': 'C/ Sol 5, 30001 Murcia, Murcia, Spain', **extra}


@pytest.mark.parametrize('nota, resenas, sale', [('4.6', '12', True), ('3.9', '40', False), ('4.8', '3', False), ('', '', False)])
def test_prueba_social_solo_si_es_buena_y_real(nota, resenas, sale):
    html = maqueta.renderizar(lead(**{'Valoración': nota, 'Reseñas': resenas}), TEXTOS)

    assert ('4,6 · 12 reseñas en Google' in html) is sale
    assert ('reseñas en Google' in html) is sale


def test_sector_desconocido_usa_tema_generico_con_su_categoria():
    html = maqueta.renderizar(lead(**{'Nombre del negocio': 'Peluquería Ana', 'Categoría': 'Peluquería'}), TEXTOS)

    assert '--acento:#334155' in html and 'Peluquería en Murcia' in html


def test_datos_del_lead_se_escapan_y_las_redes_raras_no_se_enlazan():
    html = maqueta.renderizar(lead(**{'Nombre del negocio': '<script>alert(1)</script> Taller',
                                      'Instagram': 'javascript:alert(1)', 'Facebook': 'https://facebook.com/pepe'}), TEXTOS)

    assert '<script>' not in html and '&lt;script&gt;' in html
    assert 'javascript:' not in html and 'https://facebook.com/pepe' in html


def test_whatsapp_solo_para_moviles_espanoles():
    assert maqueta.whatsapp_de(lead()) == '34612345678'
    assert maqueta.whatsapp_de(lead(**{'Teléfono': '+34 612 34 56 78'})) == '34612345678'
    assert maqueta.whatsapp_de(lead(**{'Tipo teléfono': 'Fijo'})) is None


def test_textos_de_la_ia_se_validan_y_si_vienen_mal_se_usa_el_respaldo(monkeypatch):
    class Resp:
        def __init__(self, contenido):
            self.choices = [type('C', (), {'message': type('M', (), {'content': contenido})()})()]

    def cliente_que_devuelve(contenido):
        class Cliente:
            class chat:
                class completions:
                    @staticmethod
                    def create(**_):
                        return Resp(contenido)
        return lambda: Cliente

    malos = json.dumps({'eslogan': '', 'servicios': [{'titulo': 'Solo uno', 'texto': 'x'}], 'ventajas': []})
    monkeypatch.setattr(maqueta, 'groq', cliente_que_devuelve(malos))
    html = maqueta.renderizar(lead())
    assert 'Tu coche, en buenas manos' in html and 'Pre-ITV' in html

    buenos = json.dumps({'eslogan': 'Mecánica <b>honrada</b>', 'intro': 'En Murcia.',
                         'servicios': [{'titulo': f'Serv {i}', 'texto': 'Frase.'} for i in range(6)],
                         'ventajas': [{'titulo': f'Vent {i}', 'texto': 'Frase.'} for i in range(3)]})
    monkeypatch.setattr(maqueta, 'groq', cliente_que_devuelve(buenos))
    html = maqueta.renderizar(lead())
    assert 'Serv 5' in html and 'Vent 2' in html and '<b>honrada</b>' not in html


def test_pesa_poco_y_no_carga_recursos_externos_salvo_el_mapa():
    html = maqueta.renderizar(lead(), TEXTOS)

    assert len(html.encode()) < 60_000
    assert 'fonts.googleapis' not in html and '<script' not in html
