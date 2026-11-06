import { useMemo, useState } from 'react';
import { ciudad, telHref } from '../../lib/format';
import {
  ESTADOS_LLAMADA,
  ESTADO_CLASE,
  SECTOR_LABEL,
  esFijoObjetivo,
  llamadaPendiente,
} from '../../lib/leads';
import type { Lead, LlamadaEstado, Sector } from '../../types/lead';

interface CallListProps {
  leads: Lead[];
  onPrepare: (id: number) => void;
  onMark: (id: number, estado: LlamadaEstado) => void;
}

const SMALL_BTN = 'px-2 py-1 text-xs rounded-md transition-colors';

function CallRow({ lead, onPrepare, onMark }: { lead: Lead; onPrepare: CallListProps['onPrepare']; onMark: CallListProps['onMark'] }) {
  const estado = lead.Llamada ?? '';
  const tel = lead['Teléfono'] ?? '';
  const sector = SECTOR_LABEL[lead.sector as Sector] ?? '';

  return (
    <div className={`flex flex-wrap items-center gap-x-4 gap-y-2 py-2.5 ${llamadaPendiente(lead) ? '' : 'opacity-60'}`}>
      <div className="min-w-48 flex-1">
        <p className="text-sm font-medium text-slate-200">{lead['Nombre del negocio']}</p>
        <p className="text-xs text-slate-500">
          {sector} · {ciudad(lead['Ubicación'])}
          {estado && (
            <>
              {' · '}
              <span className={`px-1.5 py-0.5 rounded ${ESTADO_CLASE[estado] ?? ''}`}>{estado}</span>{' '}
              <span className="text-slate-600">{lead['Fecha llamada']}</span>
            </>
          )}
        </p>
      </div>
      <a
        href={telHref(tel)}
        className="px-3 py-1.5 text-sm font-semibold rounded-lg bg-green-600 text-white hover:bg-green-500 transition-colors"
      >
        📞 {tel}
      </a>
      <div className="flex flex-wrap gap-1.5">
        <button
          type="button"
          onClick={() => onPrepare(lead.id)}
          className={`${SMALL_BTN} bg-blue-600/20 text-blue-300 hover:bg-blue-600/30`}
        >
          Guion
        </button>
        {ESTADOS_LLAMADA.map(({ valor, texto }) => (
          <button
            key={valor}
            type="button"
            onClick={() => onMark(lead.id, valor)}
            className={`${SMALL_BTN} bg-slate-800 text-slate-300 hover:bg-slate-700`}
          >
            {texto}
          </button>
        ))}
        {estado && (
          <button
            type="button"
            onClick={() => onMark(lead.id, '')}
            className={`${SMALL_BTN} bg-slate-800 text-slate-300 hover:bg-slate-700`}
          >
            Deshacer
          </button>
        )}
      </div>
    </div>
  );
}

export function CallList({ leads, onPrepare, onMark }: CallListProps) {
  const [showAll, setShowAll] = useState(false);

  const fijos = useMemo(() => leads.filter(esFijoObjetivo), [leads]);
  const pendientes = useMemo(() => fijos.filter(llamadaPendiente), [fijos]);
  const visibles = useMemo(
    () =>
      [...(showAll ? fijos : pendientes)].sort(
        (a, b) => Number(llamadaPendiente(b)) - Number(llamadaPendiente(a)),
      ),
    [showAll, fijos, pendientes],
  );

  return (
    <section className="px-6 pb-5">
      <div className="bg-slate-900 border border-amber-500/30 rounded-xl p-4">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-1">
          <h2 className="flex items-center gap-2 text-sm font-bold text-slate-100">
            📞 Por llamar <span className="text-slate-500 font-medium">· teléfonos fijos</span>
            <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-amber-500/15 text-amber-300">
              {pendientes.length} pendiente{pendientes.length === 1 ? '' : 's'}
            </span>
          </h2>
          <label className="flex items-center gap-2 text-xs text-slate-400 cursor-pointer">
            <input
              type="checkbox"
              checked={showAll}
              onChange={(e) => setShowAll(e.target.checked)}
              className="accent-amber-500"
            />
            Mostrar ya llamados
          </label>
        </div>
        <p className="text-xs text-slate-500 mb-3">
          Talleres, fisios y reformas sin WhatsApp: hay que llamarlos. Mejor en horario comercial (10–13 h y 17–19 h).
        </p>
        <div className="divide-y divide-slate-800/70">
          {visibles.length === 0 ? (
            <p className="py-3 text-sm text-slate-500">
              {fijos.length ? '¡Todo llamado! 🎉' : 'Aún no hay fijos de tus sectores.'}
            </p>
          ) : (
            visibles.map((l) => <CallRow key={l.id} lead={l} onPrepare={onPrepare} onMark={onMark} />)
          )}
        </div>
      </div>
    </section>
  );
}
