import { useCallback, useMemo, useState } from 'react';
import { PAGE_SIZE } from '../lib/config';
import { FILTROS, matchesQuery, type Filtro } from '../lib/leads';
import type { Lead } from '../types/lead';

/** Filtro por pestaña + búsqueda + paginación sobre la lista de leads. */
export function useLeadsView(leads: Lead[]) {
  const [query, setQueryState] = useState('');
  const [filtro, setFiltroState] = useState<Filtro>('todos');
  const [page, setPage] = useState(0);

  const conteos = useMemo(() => {
    const c = {} as Record<Filtro, number>;
    for (const f of FILTROS) c[f.id] = leads.filter(f.incluye).length;
    return c;
  }, [leads]);

  const filtered = useMemo(() => {
    const incluye = FILTROS.find((f) => f.id === filtro)!.incluye;
    const lista = leads.filter((l) => incluye(l) && matchesQuery(l, query));
    // En "Prioritarios" primero los que más necesitan una web; en el resto, el orden de llegada.
    return filtro === 'prioritarios' ? lista.sort((a, b) => (b.oportunidad ?? 0) - (a.oportunidad ?? 0)) : lista;
  }, [leads, filtro, query]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages - 1);
  const pageLeads = useMemo(
    () => filtered.slice(currentPage * PAGE_SIZE, (currentPage + 1) * PAGE_SIZE),
    [filtered, currentPage],
  );

  const setQuery = useCallback((q: string) => {
    setQueryState(q);
    setPage(0);
  }, []);

  const setFiltro = useCallback((f: Filtro) => {
    setFiltroState(f);
    setPage(0);
  }, []);

  /** Los que se pueden marcar de golpe: los que no han recibido ya un email. */
  const selectableIds = useMemo(
    () => filtered.filter((l) => !l.email_enviado).map((l) => l.id),
    [filtered],
  );
  const allSelected = selectableIds.length > 0 && filtered.every((l) => l.email_enviado || l.selected);
  const someSelected = filtered.some((l) => l.selected);

  return {
    query, setQuery, filtro, setFiltro, conteos,
    page: currentPage, setPage, totalPages,
    filtered, pageLeads, selectableIds, allSelected, someSelected,
  };
}
