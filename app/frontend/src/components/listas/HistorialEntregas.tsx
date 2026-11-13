import { listaUrl } from '../../lib/api';
import { badge, formatoNumero } from '../../lib/ui';
import type { Entrega } from '../../types/lista';
import { fechaCorta } from './formulario';

const VISIBLES = 15;

export function HistorialEntregas({ entregas }: { entregas: Entrega[] }) {
  if (entregas.length === 0) return null;
  return (
    <section className="rounded-card border border-slate-800 bg-slate-900/40">
      <header className="border-b border-slate-800 px-4 py-3 sm:px-5">
        <h2 className="text-sm font-medium text-slate-200">Listas entregadas</h2>
      </header>
      <ul className="divide-y divide-slate-800/70 text-sm">
        {entregas.slice(0, VISIBLES).map((e) => (
          <li key={e.id} className="flex items-center gap-3 px-4 py-2.5 sm:px-5">
            <span className="w-14 shrink-0 text-xs tabular-nums text-slate-500">{fechaCorta(e.fecha)}</span>
            <span className="min-w-0 flex-1 truncate text-slate-200">{e.cliente}</span>
            {e.exclusivo && <span className={badge('info')}>Exclusiva</span>}
            <span className="tabular-nums text-xs text-slate-400">{formatoNumero(e.n_leads)} leads</span>
            {e.descargable ? (
              <a
                href={listaUrl(e.archivo)}
                download
                className="text-xs font-medium text-brand-300 hover:text-brand-400 focus-visible:outline-2 focus-visible:outline-brand-500"
              >
                CSV
              </a>
            ) : (
              <span className="text-xs text-slate-600" title="El archivo ya no está en la carpeta listas/">CSV</span>
            )}
          </li>
        ))}
      </ul>
      {entregas.length > VISIBLES && (
        <p className="border-t border-slate-800 px-4 py-2 text-xs text-slate-500 sm:px-5">
          y {entregas.length - VISIBLES} más en entregas.json
        </p>
      )}
    </section>
  );
}
