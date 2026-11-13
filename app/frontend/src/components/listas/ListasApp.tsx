import { useMemo, useRef, useState } from 'react';
import { useApiStatus } from '../../hooks/useApiStatus';
import { useListas } from '../../hooks/useListas';
import { useToast } from '../../hooks/useToast';
import { listaUrl } from '../../lib/api';
import { btn, formatoNumero } from '../../lib/ui';
import type { Suscripcion } from '../../types/lista';
import { AppHeader } from '../layout/AppHeader';
import { RefreshIcon } from '../ui/icons';
import { Toast } from '../ui/Toast';
import { FORM_VACIO, aPedido, desdePedido, euros, type FormPedido } from './formulario';
import { HistorialEntregas } from './HistorialEntregas';
import { PedidoForm } from './PedidoForm';
import { PreviewPanel } from './PreviewPanel';
import { SuscripcionesPanel } from './SuscripcionesPanel';

function descargar(archivo: string) {
  const a = document.createElement('a');
  a.href = listaUrl(archivo);
  a.download = archivo;
  a.click();
}

/** Listas de leads para agencias: pedido por plan, vista previa, entrega y suscripciones. */
export default function ListasApp() {
  const { toast, notify } = useToast();
  const { connected } = useApiStatus();
  const listas = useListas(notify);
  const [form, setForm] = useState<FormPedido>(FORM_VACIO);
  const formRef = useRef<HTMLElement>(null);

  const pedido = useMemo(() => aPedido(form), [form]);
  const firma = JSON.stringify(pedido);
  const previewAlDia = listas.firmaPreview === firma;

  const { datos } = listas;
  const planes = datos?.planes ?? [];
  const clientes = datos?.clientes ?? [];

  const metricas = useMemo(() => {
    const precio = (id: string | null) => planes.find((p) => p.id === id)?.precio ?? 0;
    return [
      { label: 'Agencias', valor: formatoNumero(clientes.length) },
      { label: 'Ingresos al mes', valor: euros(clientes.reduce((s, c) => s + precio(c.plan), 0)) },
      { label: 'Listas por entregar', valor: formatoNumero(clientes.filter((c) => c.dias <= 0).length) },
      { label: 'Leads entregados', valor: formatoNumero(clientes.reduce((s, c) => s + c.leads, 0)) },
    ];
  }, [planes, clientes]);

  const preparar = (s: Suscripcion) => {
    setForm(desdePedido({ ...s.ultimo_pedido, cliente: s.cliente }));
    listas.descartarPreview();
    formRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    notify(`Pedido de ${s.cliente} cargado: previsualiza la lista de este mes`);
  };

  const crear = async () => {
    const r = await listas.crear(pedido);
    if (r?.archivo) descargar(r.archivo);
  };

  return (
    <>
      <AppHeader seccion="listas" apiConnected={connected} />

      <main className="mx-auto max-w-7xl space-y-6 px-4 pb-16 pt-6 sm:px-6">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h1 className="text-xl font-semibold tracking-tight text-slate-100">Listas para agencias</h1>
            <p className="mt-1 text-sm text-slate-400">
              Suscripción mensual: cada mes una lista fresca por sector y ciudad, sin repetir leads.
            </p>
          </div>
          <button type="button" onClick={() => void listas.recargar()} className={btn('ghost', 'icon')} aria-label="Actualizar" title="Actualizar">
            <RefreshIcon />
          </button>
        </div>

        {listas.error ? (
          <div className="rounded-card border border-red-500/20 bg-red-500/10 px-4 py-6 text-center text-sm">
            <p className="font-medium text-red-300">No se han podido cargar las listas</p>
            <p className="mt-1 text-red-200/70">{listas.error}</p>
            <button type="button" onClick={() => void listas.recargar()} className={`${btn('secondary', 'sm')} mt-3`}>
              <RefreshIcon /> Reintentar
            </button>
          </div>
        ) : (
          <dl className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            {metricas.map((m) => (
              <div key={m.label} className="rounded-card border border-slate-800 bg-slate-900/40 px-4 py-3">
                <dt className="text-[11px] font-medium uppercase tracking-wider text-slate-500">{m.label}</dt>
                <dd className="mt-1 text-2xl font-semibold tracking-tight tabular-nums text-slate-100">
                  {datos ? m.valor : <span className="inline-block h-7 w-16 animate-pulse rounded bg-slate-800" />}
                </dd>
              </div>
            ))}
          </dl>
        )}

        <div className="grid items-start gap-6 lg:grid-cols-5">
          <div className="space-y-6 lg:col-span-3">
            <section ref={formRef} className="scroll-mt-20 rounded-card border border-slate-800 bg-slate-900/40">
              <header className="border-b border-slate-800 px-4 py-3 sm:px-5">
                <h2 className="text-sm font-medium text-slate-200">Nueva lista</h2>
                <p className="text-xs text-slate-500">Previsualiza primero: la lista solo se guarda al crearla.</p>
              </header>
              {datos ? (
                <PedidoForm
                  form={form}
                  onChange={setForm}
                  planes={planes}
                  clientes={clientes.map((c) => c.cliente)}
                  previewAlDia={previewAlDia}
                  busy={listas.busy}
                  onSimular={() => void listas.simular(pedido)}
                  onMuestra={() => void listas.muestra(pedido)}
                  onCrear={() => void crear()}
                />
              ) : (
                <div className="space-y-3 p-5" aria-busy="true">
                  <div className="h-16 animate-pulse rounded-lg bg-slate-800/70" />
                  <div className="h-9 animate-pulse rounded-lg bg-slate-800/70" />
                  <div className="h-9 animate-pulse rounded-lg bg-slate-800/70" />
                </div>
              )}
            </section>

            {listas.preview && (
              <PreviewPanel
                resultado={listas.preview}
                desactualizada={!listas.preview.archivo && !previewAlDia}
                onCerrar={listas.descartarPreview}
              />
            )}
          </div>

          <div className="space-y-6 lg:col-span-2">
            <SuscripcionesPanel clientes={clientes} planes={planes} onPreparar={preparar} />
            <HistorialEntregas entregas={datos?.entregas ?? []} />
          </div>
        </div>
      </main>

      <Toast toast={toast} />
    </>
  );
}
