import type { LeadCounts } from '../../lib/leads';
import { formatoNumero } from '../../lib/ui';

interface StatsStripProps {
  counts: LeadCounts;
  ready: boolean;
  /** Total de mensajes enviados por WhatsApp, email e Instagram (null hasta conocerlo) */
  enviados: number | null;
}

interface Stat {
  label: string;
  value: number | null;
  hint: string;
  accent?: boolean;
}

/** Métricas en una sola franja: números neutros, un único acento para lo que importa. */
export function StatsStrip({ counts, ready, enviados }: StatsStripProps) {
  const v = (n: number) => (ready ? n : null);
  const stats: Stat[] = [
    { label: 'Leads', value: v(counts.total), hint: 'negocios sin web' },
    { label: 'Con WhatsApp', value: v(counts.withMobile), hint: 'teléfono móvil' },
    { label: 'Por llamar', value: v(counts.porLlamar), hint: 'fijos pendientes' },
    { label: 'Mensajes enviados', value: enviados, hint: 'WhatsApp, email e Instagram' },
    { label: 'Interesados', value: v(counts.interesados), hint: 'tras la llamada', accent: true },
  ];

  return (
    <dl className="grid grid-cols-2 gap-px overflow-hidden rounded-card border border-slate-800 bg-slate-800 sm:grid-cols-5">
      {stats.map((s) => (
        <div key={s.label} className="bg-slate-900 px-4 py-3 last:col-span-2 sm:px-5 sm:py-4 sm:last:col-span-1">
          <dt className="text-xs font-medium text-slate-400">{s.label}</dt>
          <dd className={`mt-1 text-2xl font-semibold tracking-tight tabular-nums ${s.accent ? 'text-emerald-300' : 'text-slate-100'}`}>
            {s.value === null ? <span className="text-slate-600">—</span> : formatoNumero(s.value)}
          </dd>
          <dd className="mt-0.5 hidden text-xs text-slate-500 sm:block">{s.hint}</dd>
        </div>
      ))}
    </dl>
  );
}
