import { useCallback, useMemo, useState } from 'react';
import { useApiStatus } from '../hooks/useApiStatus';
import { useLeads } from '../hooks/useLeads';
import { useLeadsView } from '../hooks/useLeadsView';
import { useModelo } from '../hooks/useModelo';
import { useToast } from '../hooks/useToast';
import { countLeads } from '../lib/leads';
import { btn } from '../lib/ui';
import { BulkActionBar } from './actions/BulkActionBar';
import { AppHeader } from './layout/AppHeader';
import { FilterTabs } from './leads/FilterTabs';
import { LeadCards } from './leads/LeadCards';
import { LeadDrawer } from './leads/LeadDrawer';
import { EmptyState, ErrorState, LoadingState } from './leads/LeadsStates';
import { LeadsTable } from './leads/LeadsTable';
import { Pagination } from './leads/Pagination';
import { QrModal } from './modals/QrModal';
import { ModelPanel } from './stats/ModelPanel';
import { StatsStrip } from './stats/StatsStrip';
import { RefreshIcon } from './ui/icons';
import { Toast } from './ui/Toast';

/** Raíz de la isla React: compone hooks de datos y componentes de presentación. */
export default function LeadsApp() {
  const { toast, notify } = useToast();
  const { leads, loading, error, reload, setSelected, selectAll, marcarLlamada, generar } = useLeads(notify);
  const { connected, status } = useApiStatus();
  const view = useLeadsView(leads);
  const modelo = useModelo(leads, notify, reload);

  const [qrOpen, setQrOpen] = useState(false);
  const [openId, setOpenId] = useState<number | null>(null);

  const counts = useMemo(() => countLeads(leads), [leads]);
  const openLead = useMemo(() => leads.find((l) => l.id === openId) ?? null, [leads, openId]);
  const enviados = status ? status.enviados + status.emails_enviados + status.ig_enviados : null;

  const openQr = useCallback(() => setQrOpen(true), []);
  const closeQr = useCallback(() => setQrOpen(false), []);
  const closeDrawer = useCallback(() => setOpenId(null), []);

  const toggleOne = useCallback((id: number, selected: boolean) => void setSelected([id], selected), [setSelected]);
  const toggleVisible = useCallback(
    (checked: boolean) =>
      void setSelected(checked ? view.selectableIds : view.filtered.map((l) => l.id), checked),
    [setSelected, view.selectableIds, view.filtered],
  );
  const refresh = () => {
    view.setPage(0);
    void reload();
  };

  const hayDatos = !loading && !error && view.filtered.length > 0;

  return (
    <>
      <AppHeader query={view.query} onQueryChange={view.setQuery} apiConnected={connected} onOpenQr={openQr} />

      <main className="mx-auto max-w-7xl space-y-6 px-4 pb-32 pt-6 sm:px-6">
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-slate-100">Leads</h1>
          <p className="mt-1 text-sm text-slate-400">Negocios locales sin página web, listos para contactar.</p>
        </div>

        <StatsStrip counts={counts} ready={!loading || leads.length > 0} enviados={enviados} />

        <ModelPanel
          modelo={modelo.modelo}
          busy={modelo.busy}
          onCalibrar={() => void modelo.calibrar()}
          onRestablecer={() => void modelo.restablecer()}
        />

        <section className="overflow-hidden rounded-card border border-slate-800 bg-slate-900/40">
          <div className="flex flex-wrap items-end justify-between gap-x-4 border-b border-slate-800 px-2 sm:px-3">
            <FilterTabs value={view.filtro} conteos={view.conteos} onChange={view.setFiltro} />
            <div className="flex items-center gap-1 py-2">
              <button
                type="button"
                onClick={() => void selectAll(true)}
                className={btn('ghost', 'sm')}
                title="Selecciona todos los leads con email al que aún no se ha escrito"
              >
                Seleccionar no contactados
              </button>
              <button type="button" onClick={refresh} className={btn('ghost', 'icon')} aria-label="Actualizar" title="Actualizar">
                <RefreshIcon />
              </button>
            </div>
          </div>

          {loading ? (
            <LoadingState />
          ) : error ? (
            <ErrorState message={error} onRetry={refresh} />
          ) : view.filtered.length === 0 ? (
            <EmptyState query={view.query} onClearQuery={() => view.setQuery('')} />
          ) : (
            <>
              <div className="hidden md:block">
                <LeadsTable
                  leads={view.pageLeads}
                  allSelected={view.allSelected}
                  someSelected={view.someSelected}
                  onToggleAll={toggleVisible}
                  onToggle={toggleOne}
                  onOpen={setOpenId}
                />
              </div>
              <div className="md:hidden">
                <LeadCards leads={view.pageLeads} onToggle={toggleOne} onOpen={setOpenId} />
              </div>
            </>
          )}

          {hayDatos && (
            <Pagination page={view.page} totalPages={view.totalPages} total={view.filtered.length} onPageChange={view.setPage} />
          )}
        </section>
      </main>

      <BulkActionBar counts={counts} notify={notify} onClear={() => void selectAll(false)} onWhatsappLaunched={openQr} />
      <LeadDrawer lead={openLead} onClose={closeDrawer} onGenerate={generar} onMarkCall={(id, e) => void marcarLlamada(id, e)} />
      <QrModal open={qrOpen} onClose={closeQr} />
      <Toast toast={toast} />
    </>
  );
}
