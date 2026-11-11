import { TONO_OPORTUNIDAD } from '../../lib/leads';
import { badge, btn } from '../../lib/ui';
import type { ModeloOportunidad } from '../../types/lead';

interface ModelPanelProps {
  modelo: ModeloOportunidad | null;
  busy: boolean;
  onCalibrar: () => void;
  onRestablecer: () => void;
}

const pct = (n: number) => `${Math.round(n * 100)}%`;

/** ¿Acierta la puntuación de oportunidad? Tasa de interés por prioridad y recalibración. */
export function ModelPanel({ modelo, busy, onCalibrar, onRestablecer }: ModelPanelProps) {
  if (!modelo) return null;
  const { estado, calibrado, rendimiento, bloques } = modelo;
  const maxPeso = Math.max(...bloques.map((b) => Math.max(b.peso, b.peso_base)), 1);

  return (
    <details className="group rounded-card border border-slate-800 bg-slate-900/40">
      <summary className="flex cursor-pointer list-none flex-wrap items-center justify-between gap-2 px-4 py-3 sm:px-5">
        <div>
          <h2 className="text-sm font-medium text-slate-200">Modelo de oportunidad</h2>
          <p className="text-xs text-slate-500">
            {calibrado
              ? `Calibrado el ${calibrado.fecha} con ${calibrado.resultados} llamadas`
              : 'Pesos de partida · aún sin calibrar con tus llamadas'}
          </p>
        </div>
        <span className="text-xs text-slate-500 group-open:hidden">Ver detalle</span>
      </summary>

      <div className="grid gap-6 border-t border-slate-800 px-4 py-4 sm:px-5 md:grid-cols-2">
        <section className="space-y-3">
          <h3 className="text-xs font-medium uppercase tracking-wider text-slate-500">¿Acierta? Interés por prioridad</h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-slate-500">
                <th className="pb-1.5 font-medium">Prioridad</th>
                <th className="pb-1.5 text-right font-medium">Leads</th>
                <th className="pb-1.5 text-right font-medium">Con resultado</th>
                <th className="pb-1.5 text-right font-medium">Interesados</th>
              </tr>
            </thead>
            <tbody className="tabular-nums text-slate-300">
              {rendimiento.map((f) => (
                <tr key={f.nivel}>
                  <td className="py-1"><span className={badge(TONO_OPORTUNIDAD[f.nivel])}>{f.nivel}</span></td>
                  <td className="py-1 text-right">{f.leads}</td>
                  <td className="py-1 text-right">{f.resultados}</td>
                  <td className="py-1 text-right">
                    {f.tasa === null ? <span className="text-slate-600">—</span> : `${f.interesados} (${pct(f.tasa)})`}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="text-xs text-slate-500">
            Si el modelo acierta, la prioridad Alta debería tener más interesados que la Media y la Baja.
          </p>
        </section>

        <section className="space-y-3">
          <h3 className="text-xs font-medium uppercase tracking-wider text-slate-500">Peso de cada señal</h3>
          <ul className="space-y-1.5">
            {bloques.map((b) => {
              const cambio = b.peso - b.peso_base;
              return (
                <li key={b.id} className="grid grid-cols-[8.5rem_1fr_3.5rem] items-center gap-2 text-xs">
                  <span className="truncate text-slate-400">{b.nombre}</span>
                  <span className="h-1.5 overflow-hidden rounded-full bg-slate-800" aria-hidden="true">
                    <span className="block h-full rounded-full bg-brand-500" style={{ width: `${(b.peso / maxPeso) * 100}%` }} />
                  </span>
                  <span className="text-right tabular-nums text-slate-300" title={`Peso de partida: ${b.peso_base}`}>
                    {b.peso.toFixed(0)}
                    {Math.abs(cambio) >= 0.5 && (
                      <span className={cambio > 0 ? 'text-emerald-400' : 'text-red-400'}> {cambio > 0 ? '↑' : '↓'}</span>
                    )}
                  </span>
                </li>
              );
            })}
          </ul>

          <div className="flex flex-wrap items-center gap-2 pt-1">
            <button type="button" onClick={onCalibrar} disabled={busy || !estado.puede_calibrar} className={btn('primary', 'sm')}>
              {busy ? 'Calibrando…' : 'Recalibrar con mis llamadas'}
            </button>
            {calibrado && (
              <button type="button" onClick={onRestablecer} disabled={busy} className={btn('ghost', 'sm')}>
                Volver a los pesos de partida
              </button>
            )}
          </div>
          <p className="text-xs text-slate-500">
            {estado.puede_calibrar
              ? `${estado.resultados} llamadas con resultado (${estado.interesados} interesados) listas para calibrar.`
              : `Marca ${estado.faltan} llamada${estado.faltan === 1 ? '' : 's'} más como "Interesado" o "Descartado" para poder calibrar (llevas ${estado.resultados}).`}
          </p>
        </section>
      </div>
    </details>
  );
}
