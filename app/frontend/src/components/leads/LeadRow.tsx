import { memo } from 'react';
import { ciudad } from '../../lib/format';
import type { Lead } from '../../types/lead';
import { SocialLinks } from './SocialLinks';

interface LeadRowProps {
  lead: Lead;
  onToggle: (id: number, selected: boolean) => void;
  onPrepare: (id: number) => void;
}

function TelTag({ tipo }: { tipo: Lead['Tipo teléfono'] }) {
  if (tipo === 'Fijo') {
    return <span className="ml-1 px-1.5 py-0.5 text-[10px] rounded bg-amber-500/15 text-amber-300 font-semibold">☎️ Fijo</span>;
  }
  if (tipo === 'Móvil') {
    return <span className="ml-1 px-1.5 py-0.5 text-[10px] rounded bg-green-500/15 text-green-300 font-semibold">📱 WhatsApp</span>;
  }
  return null;
}

export const LeadRow = memo(function LeadRow({ lead, onToggle, onPrepare }: LeadRowProps) {
  const nombre = lead['Nombre del negocio'];
  const email = lead.Email;
  const mensaje = lead.Mensaje;

  return (
    <tr className={`${lead.selected ? 'selected-row' : 'hover:bg-slate-900/60'} transition-colors cursor-default`}>
      <td className="px-3 py-3">
        <input
          type="checkbox"
          checked={lead.selected}
          onChange={(e) => onToggle(lead.id, e.target.checked)}
          aria-label={`Seleccionar ${nombre ?? 'lead'}`}
          className="w-4 h-4 rounded accent-green-500 cursor-pointer"
        />
      </td>
      <td className="px-3 py-3 font-medium text-slate-200 max-w-48 truncate" title={nombre ?? ''}>
        {nombre ?? '—'}
      </td>
      <td className="px-3 py-3"><span className="badge">{lead['Categoría'] ?? '—'}</span></td>
      <td className="px-3 py-3 text-slate-400">{ciudad(lead['Ubicación'])}</td>
      <td className="px-3 py-3 whitespace-nowrap">
        <span className={`badge ${lead['Teléfono'] ? 'has-phone' : ''}`}>{lead['Teléfono'] ?? '—'}</span>
        <TelTag tipo={lead['Tipo teléfono']} />
      </td>
      <td className="px-3 py-3 text-slate-400 max-w-40 truncate" title={email ?? ''}>
        {email ?? '—'}
        {lead.email_enviado && (
          <span className="ml-1 px-1.5 py-0.5 text-xs rounded bg-blue-900/60 text-blue-300 font-medium">Enviado</span>
        )}
      </td>
      <td className="px-3 py-3"><SocialLinks lead={lead} /></td>
      <td className="px-3 py-3 text-slate-400 max-w-56 truncate" title={mensaje ?? ''}>{mensaje || '—'}</td>
      <td className="px-3 py-3 whitespace-nowrap">
        <button
          type="button"
          onClick={() => onPrepare(lead.id)}
          className="px-2.5 py-1 text-xs font-semibold rounded-md bg-slate-800 text-slate-200 hover:bg-slate-700 transition-colors"
        >
          {lead.Guion || lead.Maqueta ? 'Ver contacto' : 'Preparar'}
        </button>
      </td>
    </tr>
  );
});
