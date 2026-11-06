import type { Lead } from '../../types/lead';
import { LeadRow } from './LeadRow';

interface LeadsTableProps {
  leads: Lead[];
  allSelected: boolean;
  onToggleAll: (checked: boolean) => void;
  onToggle: (id: number, selected: boolean) => void;
  onPrepare: (id: number) => void;
}

const TH = 'px-3 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider';
const COLUMNS = ['Negocio', 'Categoría', 'Ciudad', 'Teléfono', 'Email', 'Redes', 'Mensaje', 'Contacto'];

export function LeadsTable({ leads, allSelected, onToggleAll, onToggle, onPrepare }: LeadsTableProps) {
  return (
    <table className="w-full text-sm border-collapse">
      <thead>
        <tr className="border-b border-slate-800">
          <th className="w-9 px-3 py-3 text-left">
            <input
              type="checkbox"
              checked={allSelected}
              onChange={(e) => onToggleAll(e.target.checked)}
              aria-label="Seleccionar todos"
              className="w-4 h-4 rounded accent-green-500 cursor-pointer"
            />
          </th>
          {COLUMNS.map((c) => (
            <th key={c} className={TH}>{c}</th>
          ))}
        </tr>
      </thead>
      <tbody className="divide-y divide-slate-800/60">
        {leads.map((l) => (
          <LeadRow key={l.id} lead={l} onToggle={onToggle} onPrepare={onPrepare} />
        ))}
      </tbody>
    </table>
  );
}
