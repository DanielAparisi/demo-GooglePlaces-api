import type { LeadCounts } from '../../lib/leads';
import type { Notify } from '../../types/lead';
import { MapPinIcon } from '../ui/icons';
import { ApiStatusBadge } from './ApiStatusBadge';
import { LaunchButtons } from './LaunchButtons';
import { SearchInput } from './SearchInput';
import { SelectionActions } from './SelectionActions';

interface HeaderProps {
  query: string;
  onQueryChange: (q: string) => void;
  counts: LeadCounts;
  apiConnected: boolean | null;
  notify: Notify;
  onSelectAll: () => void;
  onClear: () => void;
  onRefresh: () => void;
  onOpenQr: () => void;
}

export function Header({
  query,
  onQueryChange,
  counts,
  apiConnected,
  notify,
  onSelectAll,
  onClear,
  onRefresh,
  onOpenQr,
}: HeaderProps) {
  return (
    <header className="sticky top-0 z-20 flex items-center justify-between px-6 py-3.5 bg-slate-900/90 backdrop-blur border-b border-slate-800/70 shadow-sm">
      <div className="flex items-center gap-3">
        <span className="flex items-center justify-center w-9 h-9 rounded-xl bg-linear-to-br from-blue-500/20 to-indigo-500/10 border border-blue-500/20 text-blue-400">
          <MapPinIcon />
        </span>
        <div className="flex flex-col leading-tight">
          <span className="text-sm font-bold text-slate-100 tracking-tight">
            Lead <span className="text-blue-400">Generator</span>
          </span>
          <span className="text-[10px] text-slate-500 font-medium tracking-wide uppercase">
            Google Places · España
          </span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <SearchInput variant="header" value={query} onChange={onQueryChange} />
        <SelectionActions onSelectAll={onSelectAll} onClear={onClear} onRefresh={onRefresh} />
        <LaunchButtons
          selectedCount={counts.selected}
          selectedWithEmail={counts.selectedWithEmail}
          selectedWithInstagram={counts.selectedWithInstagram}
          notify={notify}
          onOpenQr={onOpenQr}
        />
        <ApiStatusBadge connected={apiConnected} />
      </div>
    </header>
  );
}
