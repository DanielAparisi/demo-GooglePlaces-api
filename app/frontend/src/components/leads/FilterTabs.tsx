import { FILTROS, type Filtro } from '../../lib/leads';

interface FilterTabsProps {
  value: Filtro;
  conteos: Record<Filtro, number>;
  onChange: (f: Filtro) => void;
}

export function FilterTabs({ value, conteos, onChange }: FilterTabsProps) {
  return (
    <div role="tablist" aria-label="Filtrar leads" className="-mb-px flex gap-1 overflow-x-auto">
      {FILTROS.map((f) => {
        const activo = f.id === value;
        return (
          <button
            key={f.id}
            type="button"
            role="tab"
            aria-selected={activo}
            onClick={() => onChange(f.id)}
            className={`flex h-11 shrink-0 items-center gap-2 border-b-2 px-3 text-sm font-medium transition-colors focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-brand-500 ${
              activo
                ? 'border-brand-500 text-slate-100'
                : 'border-transparent text-slate-400 hover:border-slate-600 hover:text-slate-200'
            }`}
          >
            {f.label}
            <span
              className={`rounded-full px-1.5 text-xs tabular-nums ${
                activo ? 'bg-brand-500/15 text-brand-300' : 'bg-slate-800 text-slate-400'
              }`}
            >
              {conteos[f.id]}
            </span>
          </button>
        );
      })}
    </div>
  );
}
