import { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { QR_POLL_MS } from '../lib/config';

/** Mientras `active` sea true, refresca la imagen del QR de WhatsApp. Devuelve su object URL. */
export function useQrCode(active: boolean): string | null {
  const [src, setSrc] = useState<string | null>(null);

  useEffect(() => {
    if (!active) return;
    let cancelled = false;
    let current: string | null = null;

    const refresh = async () => {
      try {
        const url = URL.createObjectURL(await api.getQrBlob());
        if (cancelled) return URL.revokeObjectURL(url);
        if (current) URL.revokeObjectURL(current);
        current = url;
        setSrc(url);
      } catch {
        if (!cancelled) setSrc(null);
      }
    };

    void refresh();
    const timer = setInterval(() => void refresh(), QR_POLL_MS);
    return () => {
      cancelled = true;
      clearInterval(timer);
      if (current) URL.revokeObjectURL(current);
    };
  }, [active]);

  return src;
}
