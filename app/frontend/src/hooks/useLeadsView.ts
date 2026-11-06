import { useCallback, useMemo, useState } from 'react';
import { PAGE_SIZE } from '../lib/config';
import { hasContact, matchesQuery } from '../lib/leads';
import type { Lead } from '../types/lead';

/** Búsqueda + paginación sobre la lista de leads. */
export function useLeadsView(leads: Lead[]) {
  const [query, setQueryState] = useState('');
  const [page, setPage] = useState(0);

  const filtered = useMemo(
    () => leads.filter((l) => hasContact(l) && matchesQuery(l, query)),
    [leads, query],
  );

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

  /** Los que se pueden marcar de golpe: los que no han recibido ya un email. */
  const selectableIds = useMemo(
    () => filtered.filter((l) => !l.email_enviado).map((l) => l.id),
    [filtered],
  );
  const allSelected = selectableIds.length > 0 && filtered.every((l) => l.email_enviado || l.selected);

  return {
    query, setQuery, page: currentPage, setPage, totalPages,
    filtered, pageLeads, selectableIds, allSelected,
  };
}
