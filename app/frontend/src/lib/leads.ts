import type { Lead, LlamadaEstado, NivelOportunidad, RawLead, RedSocial, Sector } from '../types/lead';
import type { Tono } from './ui';

export const REDES: { key: RedSocial; etiqueta: string }[] = [
  { key: 'Facebook', etiqueta: 'f' },
  { key: 'Instagram', etiqueta: 'ig' },
  { key: 'LinkedIn', etiqueta: 'in' },
  { key: 'Twitter', etiqueta: 'x' },
  { key: 'TikTok', etiqueta: 'tt' },
  { key: 'YouTube', etiqueta: 'yt' },
];

export const SECTOR_LABEL: Record<Sector, string> = {
  reformas: 'Reformas',
  taller: 'Taller',
  fisioterapia: 'Fisioterapia',
};

export const ESTADOS_LLAMADA: { valor: LlamadaEstado; texto: string }[] = [
  { valor: 'No contesta', texto: 'No contesta' },
  { valor: 'Interesado', texto: 'Interesado' },
  { valor: 'No interesado', texto: 'Descartado' },
];

export function normalizeLead(raw: RawLead): Lead {
  return {
    ...raw,
    selected: raw.selected === true || raw.selected === 'True',
    email_enviado: raw.email_enviado === true,
  };
}

export function matchesQuery(l: Lead, query: string): boolean {
  const q = query.trim().toLowerCase();
  if (!q) return true;
  return [l['Nombre del negocio'], l['Categoría'], l['Ubicación'], l['Teléfono'], l.Email]
    .some((v) => v && v.toLowerCase().includes(q));
}

export const llamadaPendiente = (l: Lead): boolean => !l.Llamada || l.Llamada === 'No contesta';

/** Fijos de los sectores objetivo: no tienen WhatsApp, hay que llamarlos. */
export const esFijoObjetivo = (l: Lead): boolean => l['Tipo teléfono'] === 'Fijo' && !!l.sector;

export const esPendienteDeLlamar = (l: Lead): boolean => esFijoObjetivo(l) && llamadaPendiente(l);

export const esMovil = (l: Lead): boolean => l['Tipo teléfono'] === 'Móvil';

// ── Filtros de la vista ───────────────────────────────────────────────────────

export type Filtro = 'todos' | 'prioritarios' | 'whatsapp' | 'llamar' | 'email' | 'interesados';

export const FILTROS: { id: Filtro; label: string; incluye: (l: Lead) => boolean }[] = [
  { id: 'todos', label: 'Todos', incluye: () => true },
  { id: 'prioritarios', label: 'Prioritarios', incluye: (l) => l.oportunidad_nivel === 'Alta' && !l.Llamada },
  { id: 'whatsapp', label: 'WhatsApp', incluye: esMovil },
  { id: 'llamar', label: 'Por llamar', incluye: esPendienteDeLlamar },
  { id: 'email', label: 'Con email', incluye: (l) => !!l.Email },
  { id: 'interesados', label: 'Interesados', incluye: (l) => l.Llamada === 'Interesado' },
];

export const TONO_OPORTUNIDAD: Record<NivelOportunidad, Tono> = {
  Alta: 'success',
  Media: 'warning',
  Baja: 'neutral',
};

// ── Estado comercial de un lead ───────────────────────────────────────────────

export function estadoLead(l: Lead): { texto: string; tono: Tono } {
  if (l.Llamada === 'Interesado') return { texto: 'Interesado', tono: 'success' };
  if (l.Llamada === 'No interesado') return { texto: 'Descartado', tono: 'danger' };
  if (l.Llamada === 'No contesta') return { texto: 'No contesta', tono: 'warning' };
  if (l.email_enviado) return { texto: 'Email enviado', tono: 'info' };
  if (esFijoObjetivo(l)) return { texto: 'Por llamar', tono: 'warning' };
  return { texto: 'Nuevo', tono: 'neutral' };
}

// ── Contadores ────────────────────────────────────────────────────────────────

export interface LeadCounts {
  total: number;
  selected: number;
  withMobile: number;
  porLlamar: number;
  interesados: number;
  selectedWithMobile: number;
  selectedWithEmail: number;
  selectedWithInstagram: number;
}

export function countLeads(leads: Lead[]): LeadCounts {
  const c: LeadCounts = {
    total: leads.length, selected: 0, withMobile: 0, porLlamar: 0, interesados: 0,
    selectedWithMobile: 0, selectedWithEmail: 0, selectedWithInstagram: 0,
  };
  for (const l of leads) {
    if (esMovil(l)) c.withMobile++;
    if (esPendienteDeLlamar(l)) c.porLlamar++;
    if (l.Llamada === 'Interesado') c.interesados++;
    if (l.selected) {
      c.selected++;
      if (esMovil(l)) c.selectedWithMobile++;
      if (l.Email) c.selectedWithEmail++;
      if (l.Instagram) c.selectedWithInstagram++;
    }
  }
  return c;
}
