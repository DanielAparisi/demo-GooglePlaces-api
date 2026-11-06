import { useCallback, useMemo, useState } from 'react';
import { useApiStatus } from '../hooks/useApiStatus';
import { useLeads } from '../hooks/useLeads';
import { useLeadsView } from '../hooks/useLeadsView';
import { useToast } from '../hooks/useToast';
import { countLeads } from '../lib/leads';
import { CallList } from './calls/CallList';
import { EmptyState, ErrorState, LoadingState } from './leads/LeadsStates';
import { LeadsTable } from './leads/LeadsTable';
import { Pagination } from './leads/Pagination';
import { Header } from './layout/Header';
import { SearchInput } from './layout/SearchInput';
import { PrepModal } from './modals/PrepModal';
import { QrModal } from './modals/QrModal';
import { StatsGrid } from './stats/StatsGrid';
import { Toast } from './ui/Toast';

/** Raíz de la isla React: compone hooks de datos y componentes de presentación. */
export default function LeadsApp() {
  const { toast, notify } = useToast();
  const { leads, loading, error, reload, setSelected, selectAll, marcarLlamada, generar } = useLeads(notify);
  const { connected, status } = useApiStatus();
  const view = useLeadsView(leads);

  const [qrOpen, setQrOpen] = useState(false);
  const [prepId, setPrepId] = useState<number | null>(null);

  const counts = useMemo(() => countLeads(leads), [leads]);
  const prepLead = useMemo(() => leads.find((l) => l.id === prepId) ?? null, [leads, prepId]);

  const openQr = useCallback(() => setQrOpen(true), []);
  const closeQr = useCallback(() => setQrOpen(false), []);
  const closePrep = useCallback(() => setPrepId(null), []);

  const toggleOne = useCallback((id: number, selected: boolean) => void setSelected([id], selected), [setSelected]);
  const toggleVisible = useCallback(
    (checked: boolean) =>
      void setSelected(checked ? view.selectableIds : view.filtered.map((l) => l.id), checked),
    [setSelected, view.selectableIds, view.filtered],
  );
  const refresh = useCallback(() => {
    view.setPage(0);
    void reload();
  }, [view, reload]);

  return (
    <>
      <Header
        query={view.query}
        onQueryChange={view.setQuery}
        counts={counts}
        apiConnected={connected}
        notify={notify}
        onSelectAll={() => void selectAll(true)}
        onClear={() => void selectAll(false)}
        onRefresh={refresh}
        onOpenQr={openQr}
      />

      <StatsGrid
        counts={counts}
        ready={!loading || leads.length > 0}
        emailsSent={status?.emails_enviados ?? null}
        instagramSent={status?.ig_enviados ?? null}
      />

      <CallList leads={leads} onPrepare={setPrepId} onMark={(id, estado) => void marcarLlamada(id, estado)} />

      <div className="sm:hidden px-6 pb-3">
        <SearchInput variant="mobile" value={view.query} onChange={view.setQuery} />
      </div>

      <div className="px-6 pb-16 overflow-x-auto">
        {loading ? (
          <LoadingState />
        ) : error ? (
          <ErrorState message={error} />
        ) : view.filtered.length === 0 ? (
          <EmptyState />
        ) : (
          <>
            <LeadsTable
              leads={view.pageLeads}
              allSelected={view.allSelected}
              onToggleAll={toggleVisible}
              onToggle={toggleOne}
              onPrepare={setPrepId}
            />
            <Pagination
              page={view.page}
              totalPages={view.totalPages}
              total={view.filtered.length}
              onPageChange={view.setPage}
            />
          </>
        )}
      </div>

      <QrModal open={qrOpen} onClose={closeQr} />
      <PrepModal lead={prepLead} onClose={closePrep} onGenerate={generar} />
      <Toast toast={toast} />
    </>
  );
}
