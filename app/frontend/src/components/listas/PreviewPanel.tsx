import { listaUrl } from '../../lib/api';
import { TONO_OPORTUNIDAD } from '../../lib/leads';
import { badge, btn, formatoNumero } from '../../lib/ui';
import type { NivelOportunidad } from '../../types/lead';
import type { ResultadoLista } from '../../types/lista';

const NIVELES: NivelOportunidad[] = ['Alta', 'Media', 'Baja'];
const COLUMNAS = ['Negocio', 'Sector', 'Ciudad', 'Teléfono', 'Email', 'Oportunidad'];

const DESCARTES: Record<string, string> = {
  sin_canal: 'sin el dato de contacto pedido',
  puntuacion_baja: 'con puntuación baja',
  en_tu_cartera: 'en tu cartera (Interesado)',
  ya_entregados: 'ya entregados a esta agencia',
  exclusivos_de_otro: 'exclusivos de otra agencia',
  ya_vendidos: 'ya vendidos (pedido exclusivo)',
};

interface PreviewPanelProps {
  resultado: ResultadoLista;
  /** El formulario cambió desde que se calculó. */
  desactualizada: boolean;
  onCerrar: () => void;
}

export function PreviewPanel({ resultado, desactualizada, onCerrar }: PreviewPanelProps) {
  const { resumen: r, sugerencias, muestra, archivo, pedido } = resultado;
  const creada = Boolean(archivo);
  const descartes = Object.entries(r.descartes).filter(([k, v]) => v > 0 && k in DESCARTES);
  const grupos = Object.entries(r.por_grupo).slice(0, 6);

  return (
    <section
      aria-live="polite"
      className={`space-y-5 rounded-card border bg-slate-900/40 p-4 transition-opacity sm:p-5 ${
        creada ? 'border-emerald-500/30' : 'border-slate-800'
      } ${desactualizada ? 'opacity-60' : ''}`}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-sm font-medium text-slate-200">
            {creada ? `Lista creada para ${pedido.cliente}` : `Vista previa · ${pedido.cliente}`}
          </h2>
          <p className="text-xs text-slate-500">
            {creada
              ? 'Entrega registrada: estos leads no se le repetirán el mes que viene.'
              : desactualizada
                ? 'Has cambiado el pedido: vuelve a previsualizar antes de crear.'
                : 'Aún no se ha guardado nada.'}
          </p>
        </div>
        <div className="flex items-center gap-1">
          {creada && archivo && (
            <a href={listaUrl(archivo)} download className={btn('success', 'sm')}>
              Descargar CSV
            </a>
          )}
          <button type="button" onClick={onCerrar} className={btn('ghost', 'sm')}>
            Cerrar
          </button>
        </div>
      </div>

      <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          ['Leads en la lista', `${formatoNumero(r.entregados)} / ${formatoNumero(r.pedidos)}`],
          ['Disponibles', formatoNumero(r.disponibles)],
          ['Oportunidad media', String(r.puntuacion_media)],
          ['Exclusiva', pedido.exclusivo ? 'Sí' : 'No'],
        ].map(([k, v]) => (
          <div key={k} className="rounded-lg border border-slate-800 bg-slate-950/40 px-3 py-2">
            <dt className="text-[11px] font-medium uppercase tracking-wider text-slate-500">{k}</dt>
            <dd className="mt-0.5 text-lg font-semibold tabular-nums text-slate-100">{v}</dd>
          </div>
        ))}
      </dl>

      <div className="flex flex-wrap items-center gap-1.5 text-xs text-slate-400">
        Prioridad:
        {NIVELES.map((n) => (
          <span key={n} className={badge(TONO_OPORTUNIDAD[n])}>
            {r.por_nivel[n]} {n.toLowerCase()}
          </span>
        ))}
      </div>

      {r.faltan > 0 && (
        <div className="rounded-lg border border-amber-500/20 bg-amber-500/10 p-3 text-sm">
          <p className="font-medium text-amber-300">
            Faltan {formatoNumero(r.faltan)} leads para completar el pedido
          </p>
          {sugerencias.length > 0 && (
            <>
              <p className="mt-1 text-xs text-amber-200/80">Búsquedas que conviene lanzar con script.py:</p>
              <ul className="mt-1.5 flex flex-wrap gap-1.5">
                {sugerencias.map((s) => (
                  <li key={s} className={badge('warning')}>{s}</li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}

      {(grupos.length > 0 || descartes.length > 0) && (
        <div className="grid gap-4 text-xs sm:grid-cols-2">
          {grupos.length > 0 && (
            <div className="space-y-1.5">
              <h3 className="text-[11px] font-medium uppercase tracking-wider text-slate-500">Reparto</h3>
              <ul className="space-y-1">
                {grupos.map(([g, n]) => (
                  <li key={g} className="flex justify-between gap-2 text-slate-300">
                    <span className="truncate">{g}</span>
                    <span className="tabular-nums text-slate-400">{n}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {descartes.length > 0 && (
            <div className="space-y-1.5">
              <h3 className="text-[11px] font-medium uppercase tracking-wider text-slate-500">Se han quedado fuera</h3>
              <ul className="space-y-1">
                {descartes.map(([k, v]) => (
                  <li key={k} className="flex justify-between gap-2 text-slate-300">
                    <span>{DESCARTES[k]}</span>
                    <span className="tabular-nums text-slate-400">{v}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {muestra.length > 0 && (
        <div className="space-y-1.5">
          <h3 className="text-[11px] font-medium uppercase tracking-wider text-slate-500">
            Primeros {muestra.length} leads
          </h3>
          <div className="overflow-x-auto rounded-lg border border-slate-800">
            <table className="w-full min-w-[40rem] text-left text-xs">
              <thead className="bg-slate-900/80 text-slate-500">
                <tr>
                  {COLUMNAS.map((c) => (
                    <th key={c} className={`px-3 py-2 font-medium ${c === 'Oportunidad' ? 'text-right' : ''}`}>{c}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/70 text-slate-300">
                {muestra.map((fila, i) => (
                  <tr key={i} className="hover:bg-slate-800/40">
                    {COLUMNAS.map((c) => (
                      <td
                        key={c}
                        className={`max-w-[14rem] truncate px-3 py-2 ${c === 'Oportunidad' ? 'text-right tabular-nums' : ''} ${c === 'Negocio' ? 'font-medium text-slate-100' : ''}`}
                      >
                        {String(fila[c] ?? '') || <span className="text-slate-600">—</span>}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  );
}
