/** Solo enlaces http(s): bloquea javascript:, data:, etc. */
export function safeUrl(valor: unknown): string | null {
  try {
    const url = new URL(String(valor ?? ''));
    return url.protocol === 'https:' || url.protocol === 'http:' ? url.href : null;
  } catch {
    return null;
  }
}

/**
 * Ciudad de una dirección de Google Maps: va justo detrás del código postal
 * ("C. Delicias, 5, Arganzuela, 28005 Madrid, Spain" → "Madrid").
 * Misma regla que `ciudad_de` en comun/comun/dominio.py.
 */
export function ciudad(ubicacion: string | null | undefined): string {
  const partes = String(ubicacion ?? '').split(',').map((p) => p.trim()).filter(Boolean);
  for (let i = partes.length - 1; i >= 0; i--) {
    const m = /^\d{5}\s+(.+)$/.exec(partes[i]);
    if (m) return m[1];
  }
  if (partes.length >= 2) return partes[partes.length - 2];
  return partes[0] ?? '—';
}

/** Deja solo dígitos y "+" para usar el número en un enlace tel: */
export const telHref = (tel: string | null | undefined) =>
  `tel:${String(tel ?? '').replace(/[^\d+]/g, '')}`;
