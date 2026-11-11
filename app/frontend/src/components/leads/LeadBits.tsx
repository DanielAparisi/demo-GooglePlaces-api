// Piezas pequeñas de un lead, compartidas por la tabla, las tarjetas móviles y el panel.
import type { ReactNode } from 'react';
import { ciudad, safeUrl } from '../../lib/format';
import { REDES, TONO_OPORTUNIDAD, estadoLead } from '../../lib/leads';
import { badge } from '../../lib/ui';
import type { Lead } from '../../types/lead';
import { CheckIcon, MailIcon, MobileIcon, PhoneIcon } from '../ui/icons';

export function StatusBadge({ lead }: { lead: Lead }) {
  const { texto, tono } = estadoLead(lead);
  return <span className={badge(tono)}>{texto}</span>;
}

/** Puntuación de oportunidad: cuánto necesita este negocio una web. */
export function OpportunityBadge({ lead }: { lead: Lead }) {
  if (lead.oportunidad == null || !lead.oportunidad_nivel) return <span className="text-slate-600">—</span>;
  return (
    <span
      className={`${badge(TONO_OPORTUNIDAD[lead.oportunidad_nivel])} tabular-nums`}
      title={`Oportunidad ${lead.oportunidad_nivel.toLowerCase()}${lead.oportunidad_motivos?.length ? ': ' + lead.oportunidad_motivos.join(' · ') : ''}`}
    >
      {lead.oportunidad}
    </span>
  );
}

export function LeadTitle({ lead }: { lead: Lead }) {
  const nombre = lead['Nombre del negocio'] ?? '—';
  const meta = [lead['Categoría'], ciudad(lead['Ubicación'])].filter((v) => v && v !== '—').join(' · ');
  return (
    <div className="min-w-0">
      <p className="truncate font-medium text-slate-100" title={nombre}>{nombre}</p>
      <p className="truncate text-xs text-slate-500">{meta || '—'}</p>
    </div>
  );
}

export function PhoneCell({ lead }: { lead: Lead }) {
  const tel = lead['Teléfono'];
  if (!tel) return <span className="text-slate-600">—</span>;
  const movil = lead['Tipo teléfono'] === 'Móvil';
  const Icono = movil ? MobileIcon : PhoneIcon;
  return (
    <span className="inline-flex items-center gap-2 tabular-nums text-slate-300" title={movil ? 'Móvil · tiene WhatsApp' : 'Fijo · solo llamada'}>
      <Icono className={`h-4 w-4 shrink-0 ${movil ? 'text-emerald-400' : 'text-amber-400'}`} />
      {tel}
    </span>
  );
}

/** Email y redes como iconos discretos: se ve de un vistazo por dónde contactar. */
export function ContactChannels({ lead, vacio = <span className="text-slate-600">—</span> }: { lead: Lead; vacio?: ReactNode }) {
  const redes = REDES.map((r) => ({ ...r, url: safeUrl(lead[r.key]) })).filter((r) => r.url);
  if (!lead.Email && redes.length === 0) return <>{vacio}</>;

  return (
    <div className="flex items-center gap-1">
      {lead.Email && (
        <span
          className="inline-flex h-6 items-center gap-1 rounded-md bg-slate-800 px-1.5 text-slate-300"
          title={`${lead.Email}${lead.email_enviado ? ' · email enviado' : ''}`}
        >
          <MailIcon className="h-3.5 w-3.5" />
          {lead.email_enviado && <CheckIcon className="h-3 w-3 text-brand-300" />}
        </span>
      )}
      {redes.map(({ key, etiqueta, url }) => (
        <a
          key={key}
          href={url!}
          target="_blank"
          rel="noopener noreferrer"
          title={key}
          onClick={(e) => e.stopPropagation()}
          className="inline-flex h-6 min-w-6 items-center justify-center rounded-md bg-slate-800 px-1 text-[11px] font-semibold uppercase text-slate-400 transition-colors hover:bg-slate-700 hover:text-slate-100"
        >
          {etiqueta}
        </a>
      ))}
    </div>
  );
}
