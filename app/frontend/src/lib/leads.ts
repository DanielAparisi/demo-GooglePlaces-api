import type { Lead, LlamadaEstado, RawLead, RedSocial, Sector } from '../types/lead';

export const REDES: { key: RedSocial; clase: string; etiqueta: string }[] = [
  { key: 'Facebook', clase: 's-fb', etiqueta: 'F' },
  { key: 'Instagram', clase: 's-ig', etiqueta: 'I' },
  { key: 'LinkedIn', clase: 's-li', etiqueta: 'in' },
  { key: 'Twitter', clase: 's-tw', etiqueta: 'X' },
  { key: 'TikTok', clase: 's-tt', etiqueta: 'T' },
  { key: 'YouTube', clase: 's-yt', etiqueta: 'Y' },
];

export const SECTOR_LABEL: Record<Sector, string> = {
  reformas: 'Reformas',
  taller: 'Taller',
  fisioterapia: 'Fisioterapia',
};

export const ESTADO_CLASE: Record<string, string> = {
  'No contesta': 'bg-slate-700 text-slate-300',
  Interesado: 'bg-green-500/15 text-green-300',
  'No interesado': 'bg-red-500/15 text-red-300',
};

export const ESTADOS_LLAMADA: { valor: LlamadaEstado; texto: string }[] = [
  { valor: 'No contesta', texto: 'No contesta' },
  { valor: 'Interesado', texto: '👍 Interesado' },
  { valor: 'No interesado', texto: '👎 No interesado' },
];

export function normalizeLead(raw: RawLead): Lead {
  return {
    ...raw,
    selected: raw.selected === true || raw.selected === 'True',
    email_enviado: raw.email_enviado === true,
  };
}

export function hasContact(l: Lead): boolean {
  return !!(
    l['Teléfono'] || l.Email || l.Facebook || l.Instagram ||
    l.LinkedIn || l.Twitter || l.TikTok || l.YouTube
  );
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

export interface LeadCounts {
  total: number;
  selected: number;
  withPhone: number;
  withEmail: number;
  selectedWithEmail: number;
  selectedWithInstagram: number;
}

export function countLeads(leads: Lead[]): LeadCounts {
  const counts: LeadCounts = {
    total: leads.length,
    selected: 0,
    withPhone: 0,
    withEmail: 0,
    selectedWithEmail: 0,
    selectedWithInstagram: 0,
  };
  for (const l of leads) {
    if (l['Teléfono']) counts.withPhone++;
    if (l.Email) counts.withEmail++;
    if (l.selected) {
      counts.selected++;
      if (l.Email) counts.selectedWithEmail++;
      if (l.Instagram) counts.selectedWithInstagram++;
    }
  }
  return counts;
}
