import { btn } from '../../lib/ui';
import { MapPinIcon, QrIcon } from '../ui/icons';
import { ApiStatusBadge } from './ApiStatusBadge';
import { SearchInput } from './SearchInput';

interface AppHeaderProps {
  query: string;
  onQueryChange: (q: string) => void;
  apiConnected: boolean | null;
  onOpenQr: () => void;
}

export function AppHeader({ query, onQueryChange, apiConnected, onOpenQr }: AppHeaderProps) {
  return (
    <header className="sticky top-0 z-30 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-x-4 gap-y-3 px-4 py-3 sm:px-6">
        <div className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-500/15 text-brand-400 ring-1 ring-inset ring-brand-500/25">
            <MapPinIcon className="h-4 w-4" />
          </span>
          <span className="text-sm font-semibold tracking-tight text-slate-100">Lead Generator</span>
        </div>

        <div className="ml-auto flex items-center gap-2 sm:order-last">
          <ApiStatusBadge connected={apiConnected} />
          <button type="button" onClick={onOpenQr} className={btn('ghost', 'sm')} title="Vincular WhatsApp con un QR">
            <QrIcon />
            <span className="hidden sm:inline">Vincular WhatsApp</span>
          </button>
        </div>

        <div className="w-full sm:w-auto sm:flex-1 sm:max-w-md">
          <SearchInput value={query} onChange={onQueryChange} />
        </div>
      </div>
    </header>
  );
}
