import pytest

from core.errors import NotFoundError
from repositories.leads import LeadsRepository


def test_edit_guarda_los_cambios(env):
    repo = LeadsRepository(env.root / 'Leads Google Maps.csv')

    with repo.edit() as df:
        df.at[0, 'Mensaje'] = 'hola'

    assert env.csv.loc[0]['Mensaje'] == 'hola'


def test_edit_no_guarda_si_el_bloque_falla(env):
    repo = LeadsRepository(env.root / 'Leads Google Maps.csv')

    with pytest.raises(RuntimeError):
        with repo.edit() as df:
            df.at[0, 'Mensaje'] = 'a medias'
            raise RuntimeError('boom')

    assert env.csv.loc[0]['Mensaje'] == ''


def test_no_deja_ficheros_temporales(env):
    repo = LeadsRepository(env.root / 'Leads Google Maps.csv')

    with repo.edit() as df:
        df.at[0, 'Mensaje'] = 'x'

    assert [p.name for p in env.root.glob('.leads-*')] == []


def test_csv_ausente_es_not_found(tmp_path):
    with pytest.raises(NotFoundError):
        LeadsRepository(tmp_path / 'no-existe.csv').read()


def test_get_de_lead_inexistente(env):
    with pytest.raises(NotFoundError):
        LeadsRepository(env.root / 'Leads Google Maps.csv').get(99)


def test_conserva_acentos_del_csv(env):
    repo = LeadsRepository(env.root / 'Leads Google Maps.csv')

    with repo.edit() as df:
        df.at[0, 'Mensaje'] = 'Reunión mañana'

    assert env.csv.loc[0]['Mensaje'] == 'Reunión mañana'
    assert (env.root / 'Leads Google Maps.csv').read_bytes().startswith(b'\xef\xbb\xbf')
