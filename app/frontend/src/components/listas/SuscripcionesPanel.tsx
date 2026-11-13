import { badge, btn, formatoNumero } from '../../lib/ui';
import type { Plan, Suscripcion } from '../../types/lista';
import { euros, fechaCorta } from './formulario';

interface SuscripcionesPanelProps {
  clientes: Suscripcion[];
  planes: Plan[];
  onPreparar: (s: Suscripcion) => void;
}

function cuando(dias: number) {
  if (dias < 0) return { texto: `Atrasada ${-dias} día${dias === -1 ? '' : 's'}`, tono: 'danger' as const };
  if (dias === 0) return { texto: 'Toca hoy', tono: 'warning' as const };
  if (dias <= 5) return { texto: `En ${dias} día${dias === 1 ? '' : 's'}`, tono: 'warning' as const };
  return { texto: `En ${dias} días`, tono: 'neutral' as const };
}

/** Agencias suscritas, ordenadas por la próxima lista que hay que entregar. */
export function SuscripcionesPanel({ clientes, planes, onPreparar }: SuscripcionesPanelProps) {
  return (
    <section className="rounded-card border border-slate-800 bg-slate-900/40">
      <header className="border-b border-slate-800 px-4 py-3 sm:px-5">
        <h2 className="text-sm font-medium text-slate-200">Suscripciones</h2>
        <p className="text-xs text-slate-500">Una lista nueva cada mes desde la última entrega.</p>
      </header>

      {clientes.length === 0 ? (
        <p className="px-4 py-8 text-center text-sm text-slate-500 sm:px-5">
          Aún no hay agencias suscritas. Crea la primera lista y aparecerá aquí.
        </p>
      ) : (
        <ul className="divide-y divide-slate-800/70">
          {clientes.map((c) => {
            const plan = planes.find((p) => p.id === c.plan);
            const estado = cuando(c.dias);
            return (
              <li key={c.cliente} className="flex items-center gap-3 px-4 py-3 sm:px-5">
                <div className="min-w-0 flex-1 space-y-1">
                  <div className="flex flex-wrap items-center gap-1.5">
                    <span className="truncate text-sm font-medium text-slate-100">{c.cliente}</span>
                    <span className={badge(plan ? 'info' : 'neutral')}>
                      {plan ? `${plan.nombre} · ${euros(plan.precio)}` : 'A medida'}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500">
                    {c.entregas} entrega{c.entregas === 1 ? '' : 's'} · {formatoNumero(c.leads)} leads · próxima el{' '}
                    {fechaCorta(c.proxima)}
                  </p>
                </div>
                <span className={badge(estado.tono)}>{estado.texto}</span>
                <button
                  type="button"
                  onClick={() => onPreparar(c)}
                  className={btn(c.dias <= 0 ? 'secondary' : 'ghost', 'sm')}
                  title="Rellena el pedido con lo que pidió la última vez"
                >
                  Preparar lista
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
