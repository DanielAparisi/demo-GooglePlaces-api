import { useCallback, useEffect, useState } from 'react';
import { api } from '../lib/api';
import type { Notify } from '../types/lead';
import type { Pedido, ResultadoLista, ResumenListas } from '../types/lista';

export type Ocupado = 'simular' | 'crear' | 'muestra' | null;

const mensaje = (e: unknown) => (e instanceof Error ? e.message : 'Error desconocido');

/** Suscripciones, historial y el ciclo previsualizar → crear de una lista. */
export function useListas(notify: Notify) {
  const [datos, setDatos] = useState<ResumenListas | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<ResultadoLista | null>(null);
  /** Pedido exacto que se previsualizó: solo ese se puede crear. */
  const [firmaPreview, setFirmaPreview] = useState<string | null>(null);
  const [busy, setBusy] = useState<Ocupado>(null);

  const recargar = useCallback(async () => {
    try {
      setDatos(await api.getListas());
      setError(null);
    } catch (e) {
      setError(mensaje(e));
    }
  }, []);

  useEffect(() => {
    void recargar();
  }, [recargar]);

  const simular = useCallback(
    async (pedido: Pedido) => {
      setBusy('simular');
      try {
        setPreview(await api.simularLista(pedido));
        setFirmaPreview(JSON.stringify(pedido));
      } catch (e) {
        notify(mensaje(e), 'error');
      } finally {
        setBusy(null);
      }
    },
    [notify],
  );

  const crear = useCallback(
    async (pedido: Pedido) => {
      setBusy('crear');
      try {
        const r = await api.crearLista(pedido);
        setPreview(r);
        setFirmaPreview(null);
        notify(`Lista creada: ${r.resumen.entregados} leads para ${r.pedido.cliente}`, 'success');
        await recargar();
        return r;
      } catch (e) {
        notify(mensaje(e), 'error');
        return null;
      } finally {
        setBusy(null);
      }
    },
    [notify, recargar],
  );

  const muestra = useCallback(
    async (pedido: Pedido) => {
      setBusy('muestra');
      try {
        const { blob, nombre } = await api.muestraLista(pedido);
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = nombre;
        a.click();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
        notify('Muestra descargada (no cuenta como entrega)', 'success');
      } catch (e) {
        notify(mensaje(e), 'error');
      } finally {
        setBusy(null);
      }
    },
    [notify],
  );

  const descartarPreview = useCallback(() => {
    setPreview(null);
    setFirmaPreview(null);
  }, []);

  return { datos, error, recargar, preview, firmaPreview, busy, simular, crear, muestra, descartarPreview };
}
