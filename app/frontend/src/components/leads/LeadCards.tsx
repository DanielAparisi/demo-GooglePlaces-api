import type { Lead } from '../../types/lead';
import { ContactChannels, LeadTitle, PhoneCell, StatusBadge } from './LeadBits';

interface LeadCardsProps {
  leads: Lead[];
  onToggle: (id: number, selected: boolean) => void;
  onOpen: (id: number) => void;
}

/** Vista móvil: una tarjeta por lead en lugar de una tabla ancha. */
export function LeadCards({ leads, onToggle, onOpen }: LeadCardsProps) {
  return (
    <ul className="divide-y divide-slate-800/70">
      {leads.map((l) => (
        <li key={l.id} className={l.selected ? 'selected-row' : ''}>
          <div className="flex gap-3 px-4 py-3.5">
            <input
              type="checkbox"
              checked={l.selected}
              onChange={(e) => onToggle(l.id, e.target.checked)}
              aria-label={`Seleccionar ${l['Nombre del negocio'] ?? 'lead'}`}
              className="mt-0.5 h-5 w-5 shrink-0 cursor-pointer rounded accent-brand-500"
            />
            <button type="button" onClick={() => onOpen(l.id)} className="min-w-0 flex-1 space-y-2 text-left text-sm">
              <div className="flex items-start justify-between gap-3">
                <LeadTitle lead={l} />
                <StatusBadge lead={l} />
              </div>
              <div className="flex flex-wrap items-center justify-between gap-2">
                <PhoneCell lead={l} />
                <ContactChannels lead={l} vacio={null} />
              </div>
            </button>
          </div>
        </li>
      ))}
    </ul>
  );
}
