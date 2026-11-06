import { RefreshIcon } from '../ui/icons';

interface SelectionActionsProps {
  onSelectAll: () => void;
  onClear: () => void;
  onRefresh: () => void;
}

const BTN =
  'px-2.5 py-1 text-xs font-medium rounded-md text-slate-300 hover:bg-slate-700 hover:text-slate-100 transition-colors';

export function SelectionActions({ onSelectAll, onClear, onRefresh }: SelectionActionsProps) {
  return (
    <div className="flex items-center gap-1 bg-slate-800/60 border border-slate-700/60 rounded-lg p-1">
      <button type="button" onClick={onSelectAll} className={BTN}>Seleccionar</button>
      <div className="w-px h-4 bg-slate-700" />
      <button type="button" onClick={onClear} className={BTN}>Limpiar</button>
      <div className="w-px h-4 bg-slate-700" />
      <button type="button" onClick={onRefresh} className={BTN} title="Actualizar" aria-label="Actualizar">
        <RefreshIcon />
      </button>
    </div>
  );
}
