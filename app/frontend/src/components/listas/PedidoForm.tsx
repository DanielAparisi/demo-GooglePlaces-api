import type { Ocupado } from '../../hooks/useListas';
import { btn } from '../../lib/ui';
import type { Plan } from '../../types/lista';
import { CANALES, euros, type FormPedido } from './formulario';

interface PedidoFormProps {
  form: FormPedido;
  onChange: (form: FormPedido) => void;
  planes: Plan[];
  clientes: string[];
  /** La vista previa corresponde exactamente a este formulario: ya se puede crear. */
  previewAlDia: boolean;
  busy: Ocupado;
  onSimular: () => void;
  onMuestra: () => void;
  onCrear: () => void;
}

const INPUT =
  'h-9 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 text-sm text-slate-100 ' +
  'placeholder:text-slate-500 outline-none transition focus:border-brand-500 focus:ring-3 focus:ring-brand-500/20';
const LABEL = 'text-xs font-medium text-slate-300';
const AYUDA = 'text-xs text-slate-500';

export function PedidoForm({ form, onChange, planes, clientes, previewAlDia, busy, onSimular, onMuestra, onCrear }: PedidoFormProps) {
  const set = <K extends keyof FormPedido>(k: K, v: FormPedido[K]) => onChange({ ...form, [k]: v });
  const plan = planes.find((p) => p.id === form.plan);
  const exclusivoPorPlan = Boolean(plan?.exclusivo);
  const puedeEnviar = form.cliente.trim() !== '' && (form.plan !== null || form.cantidad.trim() !== '');

  const submit = (e: { preventDefault: () => void }) => {
    e.preventDefault();
    if (!puedeEnviar || busy) return;
    if (previewAlDia) onCrear();
    else onSimular();
  };

  return (
    <form onSubmit={submit} className="space-y-6 p-4 sm:p-5">
      <fieldset className="space-y-2">
        <legend className={LABEL}>Plan de suscripción</legend>
        <div className="grid gap-2 sm:grid-cols-3">
          {planes.map((p) => {
            const activo = form.plan === p.id;
            return (
              <label
                key={p.id}
                className={`relative flex cursor-pointer flex-col gap-1 rounded-lg border p-3 transition-colors has-focus-visible:outline-2 has-focus-visible:outline-brand-500 ${
                  activo ? 'border-brand-500/60 bg-brand-500/10' : 'border-slate-800 bg-slate-900/60 hover:border-slate-700'
                }`}
              >
                <input
                  type="radio"
                  name="plan"
                  className="sr-only"
                  checked={activo}
                  onChange={() => onChange({ ...form, plan: p.id, cantidad: '' })}
                />
                <span className="flex items-baseline justify-between gap-2">
                  <span className="text-sm font-semibold text-slate-100">{p.nombre}</span>
                  <span className="text-sm tabular-nums text-slate-300">
                    {euros(p.precio)}
                    <span className="text-xs text-slate-500">/mes</span>
                  </span>
                </span>
                <span className="text-xs text-slate-400">
                  {p.cantidad} leads/mes{p.exclusivo ? ' · exclusivos' : ''}
                </span>
              </label>
            );
          })}
        </div>
        <button
          type="button"
          onClick={() => set('plan', null)}
          className={`text-xs transition-colors ${form.plan === null ? 'text-brand-300' : 'text-slate-500 hover:text-slate-300'}`}
        >
          {form.plan === null ? '✓ Pedido a medida (sin plan)' : 'O haz un pedido a medida, sin plan'}
        </button>
      </fieldset>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-1.5">
          <label htmlFor="cliente" className={LABEL}>Agencia</label>
          <input
            id="cliente"
            list="clientes-existentes"
            className={INPUT}
            value={form.cliente}
            onChange={(e) => set('cliente', e.target.value)}
            placeholder="Agencia Sol"
            autoComplete="off"
            required
          />
          <datalist id="clientes-existentes">
            {clientes.map((c) => <option key={c} value={c} />)}
          </datalist>
          <p className={AYUDA}>Usa siempre el mismo nombre: así no se le repiten leads.</p>
        </div>

        <div className="space-y-1.5">
          <label htmlFor="cantidad" className={LABEL}>Cantidad de leads</label>
          <input
            id="cantidad"
            type="number"
            min={1}
            max={5000}
            inputMode="numeric"
            className={INPUT}
            value={form.cantidad}
            onChange={(e) => set('cantidad', e.target.value)}
            placeholder={plan ? `${plan.cantidad} (del plan)` : 'p. ej. 50'}
            required={form.plan === null}
          />
          <p className={AYUDA}>{plan ? 'Déjalo vacío para usar la del plan.' : 'Obligatoria en un pedido a medida.'}</p>
        </div>

        <div className="space-y-1.5">
          <label htmlFor="sectores" className={LABEL}>Sectores</label>
          <input
            id="sectores"
            className={INPUT}
            value={form.sectores}
            onChange={(e) => set('sectores', e.target.value)}
            placeholder="taller, reformas, fisioterapia"
          />
          <p className={AYUDA}>Separados por comas. Vacío = todos.</p>
        </div>

        <div className="space-y-1.5">
          <label htmlFor="ciudades" className={LABEL}>Ciudades o zonas</label>
          <input
            id="ciudades"
            className={INPUT}
            value={form.ciudades}
            onChange={(e) => set('ciudades', e.target.value)}
            placeholder="Murcia, Cartagena"
          />
          <p className={AYUDA}>Ciudad, barrio o provincia. Vacío = todas.</p>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <fieldset className="space-y-2">
          <legend className={LABEL}>Datos de contacto obligatorios</legend>
          <div className="flex flex-wrap gap-1.5">
            {CANALES.map((c) => {
              const activo = form.requiere.includes(c.id);
              return (
                <label
                  key={c.id}
                  className={`cursor-pointer rounded-md px-2.5 py-1 text-xs font-medium ring-1 ring-inset transition-colors has-focus-visible:outline-2 has-focus-visible:outline-brand-500 ${
                    activo ? 'bg-brand-500/15 text-brand-300 ring-brand-500/30' : 'text-slate-400 ring-slate-700 hover:text-slate-200'
                  }`}
                >
                  <input
                    type="checkbox"
                    className="sr-only"
                    checked={activo}
                    onChange={() =>
                      set('requiere', activo ? form.requiere.filter((r) => r !== c.id) : [...form.requiere, c.id])
                    }
                  />
                  {c.label}
                </label>
              );
            })}
          </div>
        </fieldset>

        <div className="space-y-2">
          <label htmlFor="minimo" className={`${LABEL} flex justify-between`}>
            <span>Puntuación de oportunidad mínima</span>
            <span className="tabular-nums text-slate-400">{form.puntuacion_min}</span>
          </label>
          <input
            id="minimo"
            type="range"
            min={0}
            max={100}
            step={5}
            value={form.puntuacion_min}
            onChange={(e) => set('puntuacion_min', Number(e.target.value))}
            className="w-full accent-brand-500"
          />
        </div>
      </div>

      <label className="flex items-start gap-2.5 text-sm text-slate-300">
        <input
          type="checkbox"
          className="mt-0.5 h-4 w-4 accent-brand-500"
          checked={exclusivoPorPlan || form.exclusivo}
          disabled={exclusivoPorPlan}
          onChange={(e) => set('exclusivo', e.target.checked)}
        />
        <span>
          Exclusiva
          <span className="block text-xs text-slate-500">
            {exclusivoPorPlan
              ? 'Incluida en el plan Premium: estos leads no se venderán a ninguna otra agencia.'
              : 'Estos leads no se volverán a vender a nadie y solo entran leads nunca vendidos.'}
          </span>
        </span>
      </label>

      <div className="flex flex-wrap items-center justify-end gap-2 border-t border-slate-800 pt-4">
        <button
          type="button"
          onClick={onMuestra}
          disabled={busy !== null}
          className={`${btn('ghost', 'md')} mr-auto`}
          title="Los 10 mejores leads con estos filtros, para enseñar a una agencia. No se registra como entrega."
        >
          {busy === 'muestra' ? 'Preparando…' : 'Muestra gratis (10 leads)'}
        </button>
        {previewAlDia ? (
          <>
            <button type="button" onClick={onSimular} disabled={busy !== null} className={btn('ghost', 'md')}>
              {busy === 'simular' ? 'Calculando…' : 'Volver a calcular'}
            </button>
            <button type="submit" disabled={!puedeEnviar || busy !== null} className={btn('primary', 'md')}>
              {busy === 'crear' ? 'Creando…' : 'Crear lista y descargar CSV'}
            </button>
          </>
        ) : (
          <button type="submit" disabled={!puedeEnviar || busy !== null} className={btn('primary', 'md')}>
            {busy === 'simular' ? 'Calculando…' : 'Previsualizar lista'}
          </button>
        )}
      </div>
    </form>
  );
}
