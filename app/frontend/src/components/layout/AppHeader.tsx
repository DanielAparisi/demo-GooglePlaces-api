import { btn } from '../../lib/ui';
import { MapPinIcon, QrIcon } from '../ui/icons';
import { ApiStatusBadge } from './ApiStatusBadge';
import { SearchInput } from './SearchInput';

type Seccion = 'leads' | 'listas';

interface AppHeaderProps {
  seccion?: Seccion;
  query?: string;
  onQueryChange?: (q: string) => void;
  apiConnected: boolean | null;
  onOpenQr?: () => void;
}

const SECCIONES: { id: Seccion; label: string; href: string }[] = [
  { id: 'leads', label: 'Leads', href: '/' },
  { id: 'listas', label: 'Listas para agencias', href: '/listas' },
];

export function AppHeader({ seccion = 'leads', query, onQueryChange, apiConnected, onOpenQr }: AppHeaderProps) {
  return (
    <header className="sticky top-0 z-30 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-x-4 gap-y-3 px-4 py-3 sm:px-6">
        <div className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-500/15 text-brand-400 ring-1 ring-inset ring-brand-500/25">
            <MapPinIcon className="h-4 w-4" />
          </span>
          <span className="hidden text-sm font-semibold tracking-tight text-slate-100 sm:inline">Lead Generator</span>
        </div>

        <nav aria-label="Secciones" className="flex items-center gap-1">
          {SECCIONES.map((s) => (
            <a
              key={s.id}
              href={s.href}
              aria-current={s.id === seccion ? 'page' : undefined}
              className={`rounded-lg px-2.5 py-1.5 text-sm font-medium transition-colors ${
                s.id === seccion ? 'bg-slate-800/80 text-slate-100' : 'text-slate-400 hover:text-slate-100'
              }`}
            >
              {s.label}
            </a>
          ))}
        </nav>

        <div className="ml-auto flex items-center gap-2 sm:order-last">
          <ApiStatusBadge connected={apiConnected} />
          {onOpenQr && (
            <button type="button" onClick={onOpenQr} className={btn('ghost', 'sm')} title="Vincular WhatsApp con un QR">
              <QrIcon />
              <span className="hidden sm:inline">Vincular WhatsApp</span>
            </button>
          )}
        </div>

        {onQueryChange && (
          <div className="w-full sm:w-auto sm:flex-1 sm:max-w-md">
            <SearchInput value={query ?? ''} onChange={onQueryChange} />
          </div>
        )}
      </div>
    </header>
  );
}
