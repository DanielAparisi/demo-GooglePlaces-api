import { memo } from 'react';
import type { Lead } from '../../types/lead';
import { ChevronRightIcon } from '../ui/icons';
import { ContactChannels, LeadTitle, PhoneCell, StatusBadge } from './LeadBits';

interface LeadRowProps {
  lead: Lead;
  onToggle: (id: number, selected: boolean) => void;
  onOpen: (id: number) => void;
}

export const LeadRow = memo(function LeadRow({ lead, onToggle, onOpen }: LeadRowProps) {
  return (
    <tr
      onClick={() => onOpen(lead.id)}
      className={`group cursor-pointer transition-colors ${lead.selected ? 'selected-row' : 'hover:bg-slate-800/40'}`}
    >
      <td className="w-10 py-3 pl-4 pr-2" onClick={(e) => e.stopPropagation()}>
        <input
          type="checkbox"
          checked={lead.selected}
          onChange={(e) => onToggle(lead.id, e.target.checked)}
          aria-label={`Seleccionar ${lead['Nombre del negocio'] ?? 'lead'}`}
          className="h-4 w-4 cursor-pointer rounded accent-brand-500"
        />
      </td>
      <td className="w-[38%] max-w-0 py-3 pr-4"><LeadTitle lead={lead} /></td>
      <td className="whitespace-nowrap py-3 pr-4"><PhoneCell lead={lead} /></td>
      <td className="py-3 pr-4"><ContactChannels lead={lead} /></td>
      <td className="whitespace-nowrap py-3 pr-4"><StatusBadge lead={lead} /></td>
      <td className="w-10 py-3 pr-4 text-right">
        <button
          type="button"
          onClick={(e) => { e.stopPropagation(); onOpen(lead.id); }}
          aria-label={`Abrir ${lead['Nombre del negocio'] ?? 'lead'}`}
          className="rounded-md p-1 text-slate-500 transition-colors group-hover:text-slate-200 focus-visible:outline-2 focus-visible:outline-brand-500"
        >
          <ChevronRightIcon />
        </button>
      </td>
    </tr>
  );
});
