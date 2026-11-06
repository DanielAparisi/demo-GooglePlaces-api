import pytest

import enrich_emails as enr
from comun import leads_csv


# ── Extracción ────────────────────────────────────────────────────────────────

def test_extraer_emails_filtra_dominios_imagenes_y_duplicados():
    html = 'Info@TallerPepe.es, info@tallerpepe.es. logo@2x.png error@sentry.io'
    assert enr.extraer_emails(html) == ['info@tallerpepe.es']


@pytest.mark.parametrize('html, red, url', [
    ('<a href="https://www.facebook.com/TallerPepe">', 'Facebook', 'https://facebook.com/tallerpepe'),
    ('<a href="https://www.instagram.com/taller_pepe">', 'Instagram', 'https://instagram.com/taller_pepe'),
    ('<a href="https://es.linkedin.com/in/pepe-garcia">', 'LinkedIn', 'https://linkedin.com/in/pepe-garcia'),
    ('<a href="https://linkedin.com/company/taller-pepe/">', 'LinkedIn', 'https://linkedin.com/company/taller-pepe'),
    ('<a href="https://youtube.com/channel/UCaBcDeF123">', 'YouTube', 'https://youtube.com/channel/UCaBcDeF123'),
    ('<a href="https://youtube.com/@TallerPepe">', 'YouTube', 'https://youtube.com/@tallerpepe'),
    ('<a href="https://x.com/tallerpepe">', 'Twitter', 'https://x.com/tallerpepe'),
    ('<a href="https://tiktok.com/@tallerpepe">', 'TikTok', 'https://tiktok.com/@tallerpepe'),
])
def test_extraer_redes_conserva_el_tipo_de_url(html, red, url):
    assert enr.extraer_redes(html)[red] == url


def test_extraer_redes_ignora_rutas_que_no_son_perfiles():
    html = 'https://instagram.com/explore/ https://facebook.com/sharer.php https://instagram.com/taller_pepe/'
    redes = enr.extraer_redes(html)
    assert redes['Instagram'] == 'https://instagram.com/taller_pepe'
    assert 'Facebook' not in redes


def test_es_del_negocio_ignora_palabras_genericas():
    assert enr.es_del_negocio('Taller Pepelu', 'info@pepelu.es')
    assert not enr.es_del_negocio('Taller Mecánico', 'info@tallermecanico.es')


# ── Búsqueda ──────────────────────────────────────────────────────────────────

class FakeScraper:
    def __init__(self, paginas):
        self.paginas = list(paginas)
        self.urls = []

    def get(self, url):
        self.urls.append(url)
        p = self.paginas.pop(0) if self.paginas else None
        if isinstance(p, Exception):
            raise p
        return p


def test_buscar_info_usa_la_ciudad_real_y_para_al_completar():
    scraper = FakeScraper(['pepelu@gmail.com https://facebook.com/pepelu https://instagram.com/pepelu https://x.com/pepelu'])
    email, redes, obtenidas = enr.buscar_info('Taller Pepelu', 'C. Sol, 5, 48001 Bilbao, Bizkaia, Spain', scraper)

    assert email == 'pepelu@gmail.com' and len(redes) == 3 and obtenidas == 1
    assert len(scraper.urls) == 1                       # no gasta más créditos
    assert 'Bilbao' in scraper.urls[0] and 'Bizkaia' not in scraper.urls[0]


def test_buscar_info_cuenta_paginas_fallidas():
    email, redes, obtenidas = enr.buscar_info('Taller Pepelu', 'Bilbao, Spain', FakeScraper([]))
    assert (email, redes, obtenidas) == (None, {}, 0)


def test_scrapedo_sin_creditos_es_error_fatal(monkeypatch):
    class Resp:
        status_code, text = 401, 'You have no credits'
    monkeypatch.setattr('enrich_emails.requests.get', lambda *a, **k: Resp())
    with pytest.raises(enr.ScrapeDoAgotado):
        enr.ScrapeDo('t', pausa=0).get('https://example.test')


# ── Guardado ──────────────────────────────────────────────────────────────────

def test_guardar_resultado_respeta_cambios_hechos_mientras_tanto(csv):
    # Mientras se buscaba, alguien seleccionó el lead en el panel
    with leads_csv.editar(csv) as df:
        df.at[0, 'selected'] = 'True'

    escritos = enr.guardar_resultado('Taller Pepe', 'C. Sol, 5, 30001 Murcia, Murcia, Spain', 0,
                                     'pepe@taller.test', {'Facebook': 'https://facebook.com/pepe'}, csv=csv)

    fila = leads_csv.leer(csv).loc[0]
    assert fila['selected'] == 'True'
    assert fila['Email'] == 'pepe@taller.test' and fila['enriched'] == 'True'
    assert set(escritos) == {'Email', 'Facebook'}


def test_guardar_resultado_no_pisa_datos_existentes(csv):
    escritos = enr.guardar_resultado('Fisio Mar', 'Av. Mar, 3, 30500 Molina, Murcia, Spain', 1,
                                     'otro@x.test', {}, csv=csv)
    assert escritos == {}
    assert leads_csv.leer(csv).loc[1, 'Email'] == 'hola@fisiomar.test'


def test_guardar_resultado_encuentra_el_lead_aunque_haya_cambiado_de_fila(csv):
    escritos = enr.guardar_resultado('Taller Pepe', 'C. Sol, 5, 30001 Murcia, Murcia, Spain', 1,
                                     'pepe@taller.test', {}, csv=csv)
    assert escritos == {'Email': 'pepe@taller.test'}
    assert leads_csv.leer(csv).loc[0, 'Email'] == 'pepe@taller.test'


def test_pendientes(csv):
    df = leads_csv.leer(csv)
    assert [n for _, n, _ in enr.pendientes(df)] == ['Taller Pepe']
