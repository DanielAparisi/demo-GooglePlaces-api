import { useCallback, useEffect, useState } from 'react';
import { api } from '../lib/api';
import type { Lead, ModeloOportunidad, Notify } from '../types/lead';

/**
 * Estado del modelo de oportunidad. Se vuelve a pedir cuando cambia el resultado de alguna
 * llamada (no al marcar casillas), y tras recalibrar recarga los leads con los pesos nuevos.
 */
export function useModelo(leads: Lead[], notify: Notify, reloadLeads: () => Promise<void>) {
  const [modelo, setModelo] = useState<ModeloOportunidad | null>(null);
  const [busy, setBusy] = useState(false);

  const firmaLlamadas = leads.map((l) => `${l.id}:${l.Llamada ?? ''}`).join('|');

  useEffect(() => {
    let cancelled = false;
    api.getModelo().then((m) => !cancelled && setModelo(m)).catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, [firmaLlamadas]);

  const ejecutar = useCallback(
    async (accion: () => Promise<ModeloOportunidad>, ok: string) => {
      setBusy(true);
      try {
        setModelo(await accion());
        notify(ok, 'success');
        await reloadLeads();
      } catch (e) {
        notify(e instanceof Error ? e.message : 'Error desconocido', 'error');
      } finally {
        setBusy(false);
      }
    },
    [notify, reloadLeads],
  );

  const calibrar = useCallback(() => ejecutar(api.calibrar, 'Modelo recalibrado con tus llamadas'), [ejecutar]);
  const restablecer = useCallback(() => ejecutar(api.restablecerModelo, 'Pesos de partida restaurados'), [ejecutar]);

  return { modelo, busy, calibrar, restablecer };
}
