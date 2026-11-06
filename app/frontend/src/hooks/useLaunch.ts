import { useCallback, useState } from 'react';
import { api } from '../lib/api';
import type { Canal, Notify } from '../types/lead';

const MENSAJE_OK: Record<Canal, (selected: number, pid: number) => string> = {
  whatsapp: (n, pid) => `Script lanzado — ${n} mensajes en cola (PID ${pid})`,
  email: (n, pid) => `Emails en cola: ${n} mensajes (PID ${pid})`,
  instagram: (n, pid) => `Instagram DMs en cola: ${n} mensajes (PID ${pid})`,
};

/** Lanza el envío de un canal (WhatsApp, email o Instagram) y avisa del resultado. */
export function useLaunch(canal: Canal, notify: Notify, onLaunched?: () => void) {
  const [launching, setLaunching] = useState(false);

  const launch = useCallback(async () => {
    setLaunching(true);
    try {
      const { selected, pid } = await api.launch(canal);
      notify(MENSAJE_OK[canal](selected, pid), 'success');
      onLaunched?.();
    } catch (e) {
      notify('Error: ' + (e instanceof Error ? e.message : 'Error desconocido'), 'error');
    } finally {
      setLaunching(false);
    }
  }, [canal, notify, onLaunched]);

  return { launching, launch };
}
