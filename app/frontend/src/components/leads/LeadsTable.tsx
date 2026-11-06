import { useEffect, useRef } from 'react';
import type { Lead } from '../../types/lead';
import { LeadRow } from './LeadRow';

interface LeadsTableProps {
  leads: Lead[];
  allSelected: boolean;
  someSelected: boolean;
  onToggleAll: (checked: boolean) => void;
  onToggle: (id: number, selected: boolean) => void;
  onOpen: (id: number) => void;
}

const TH = 'py-2.5 pr-4 text-left text-xs font-medium text-slate-500';

export function LeadsTable({ leads, allSelected, someSelected, onToggleAll, onToggle, onOpen }: LeadsTableProps) {
  const checkAll = useRef<HTMLInputElement>(null);
  useEffect(() => {
    if (checkAll.current) checkAll.current.indeterminate = someSelected && !allSelected;
  }, [someSelected, allSelected]);

  return (
    <table className="w-full text-sm">
      <thead className="border-b border-slate-800 bg-slate-900/60">
        <tr>
          <th className="w-10 py-2.5 pl-4 pr-2 text-left">
            <input
              ref={checkAll}
              type="checkbox"
              checked={allSelected}
              onChange={(e) => onToggleAll(e.target.checked)}
              aria-label="Seleccionar todos los de este filtro"
              className="h-4 w-4 cursor-pointer rounded accent-brand-500"
            />
          </th>
          <th className={TH}>Negocio</th>
          <th className={TH}>Teléfono</th>
          <th className={TH}>Canales</th>
          <th className={TH}>Estado</th>
          <th className="w-10" aria-label="Abrir" />
        </tr>
      </thead>
      <tbody className="divide-y divide-slate-800/70">
        {leads.map((l) => (
          <LeadRow key={l.id} lead={l} onToggle={onToggle} onOpen={onOpen} />
        ))}
      </tbody>
    </table>
  );
}
