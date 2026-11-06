import { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { STATUS_POLL_MS } from '../lib/config';
import type { ApiStatus } from '../types/lead';

export interface ApiStatusState {
  /** null mientras no se ha recibido la primera respuesta */
  connected: boolean | null;
  status: ApiStatus | null;
}

/** Consulta /api/status periódicamente: estado de la conexión y contadores de envíos. */
export function useApiStatus(): ApiStatusState {
  const [state, setState] = useState<ApiStatusState>({ connected: null, status: null });

  useEffect(() => {
    let cancelled = false;
    const poll = async () => {
      try {
        const status = await api.getStatus();
        if (!cancelled) setState({ connected: true, status });
      } catch {
        if (!cancelled) setState((s) => ({ ...s, connected: false }));
      }
    };
    void poll();
    const timer = setInterval(() => void poll(), STATUS_POLL_MS);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  return state;
}
