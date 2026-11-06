import { useCallback, useEffect, useState } from 'react';
import { api } from '../lib/api';
import { esPendienteDeLlamar, normalizeLead } from '../lib/leads';
import type { GeneracionTipo, Lead, LlamadaEstado, Notify } from '../types/lead';

const errorMsg = (e: unknown) => (e instanceof Error ? e.message : 'Error desconocido');

/** Estado de los leads y todas las operaciones que los modifican. */
export function useLeads(notify: Notify) {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const patchLeads = useCallback(
    (ids: Set<number> | null, patch: (l: Lead) => Partial<Lead>) =>
      setLeads((prev) => prev.map((l) => (!ids || ids.has(l.id) ? { ...l, ...patch(l) } : l))),
    [],
  );

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const next = (await api.getLeads()).map(normalizeLead);
      setLeads(next);
      const pendientes = next.filter(esPendienteDeLlamar).length;
      if (pendientes > 0) {
        notify(`📞 Recuerda: tienes ${pendientes} negocio${pendientes === 1 ? '' : 's'} por llamar`);
      }
    } catch (e) {
      setError(errorMsg(e));
    } finally {
      setLoading(false);
    }
  }, [notify]);

  useEffect(() => {
    void reload();
  }, [reload]);

  /** Actualización optimista; si el backend falla se revierte lo que cambió. */
  const setSelected = useCallback(
    async (ids: number[], selected: boolean) => {
      const idSet = new Set(ids);
      const changed = new Set(leads.filter((l) => idSet.has(l.id) && l.selected !== selected).map((l) => l.id));
      patchLeads(idSet, () => ({ selected }));
      try {
        await api.setSelection(ids, selected);
      } catch (e) {
        patchLeads(changed, () => ({ selected: !selected }));
        notify('Error guardando selección: ' + errorMsg(e), 'error');
      }
    },
    [leads, notify, patchLeads],
  );

  /** "Seleccionar" marca solo los que no tienen email previo; "Limpiar" desmarca todos. */
  const selectAll = useCallback(
    async (selected: boolean) => {
      patchLeads(null, (l) => ({ selected: selected && !l.email_enviado }));
      try {
        if (selected) {
          const { selected: n } = await api.selectNotEmailed();
          if (n !== undefined) notify(`${n} leads seleccionados (sin email previo)`);
        } else {
          await api.setAllSelection(false);
        }
      } catch (e) {
        notify('Error guardando selección: ' + errorMsg(e), 'error');
        void reload();
      }
    },
    [notify, patchLeads, reload],
  );

  const marcarLlamada = useCallback(
    async (id: number, estado: LlamadaEstado) => {
      try {
        await api.setLlamada(id, estado);
        patchLeads(new Set([id]), () => ({
          Llamada: estado,
          'Fecha llamada': estado ? new Date().toISOString().slice(0, 10) : '',
        }));
      } catch (e) {
        notify('Error guardando la llamada: ' + errorMsg(e), 'error');
      }
    },
    [notify, patchLeads],
  );

  const generar = useCallback(
    async (id: number, tipo: GeneracionTipo) => {
      try {
        const data = await api.generar(id, tipo);
        patchLeads(new Set([id]), () => (tipo === 'guion' ? { Guion: data.guion } : { Maqueta: data.maqueta }));
        notify(tipo === 'guion' ? 'Guion listo' : 'Maqueta lista', 'success');
      } catch (e) {
        notify(errorMsg(e), 'error');
      }
    },
    [notify, patchLeads],
  );

  return { leads, loading, error, reload, setSelected, selectAll, marcarLlamada, generar };
}
