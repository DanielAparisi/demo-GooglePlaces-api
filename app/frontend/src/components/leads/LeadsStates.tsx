import { btn } from '../../lib/ui';
import { EmptyIcon, RefreshIcon } from '../ui/icons';

/** Esqueleto con la forma de la tabla: la página no "salta" al llegar los datos. */
export function LoadingState() {
  return (
    <div className="divide-y divide-slate-800/70" aria-busy="true" aria-label="Cargando leads">
      {Array.from({ length: 6 }, (_, i) => (
        <div key={i} className="flex items-center gap-4 px-4 py-4">
          <div className="h-4 w-4 rounded bg-slate-800" />
          <div className="flex-1 space-y-2">
            <div className="h-3.5 w-48 animate-pulse rounded bg-slate-800" />
            <div className="h-3 w-32 animate-pulse rounded bg-slate-800/70" />
          </div>
          <div className="hidden h-3.5 w-28 animate-pulse rounded bg-slate-800 md:block" />
          <div className="h-5 w-20 animate-pulse rounded-md bg-slate-800" />
        </div>
      ))}
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="flex flex-col items-center gap-3 px-4 py-16 text-center">
      <p className="text-sm font-medium text-slate-200">No se han podido cargar los leads</p>
      <p className="max-w-sm text-sm text-slate-500">
        {message}. Comprueba que el backend está arrancado en el puerto 8000.
      </p>
      <button type="button" onClick={onRetry} className={btn('secondary', 'sm')}>
        <RefreshIcon /> Reintentar
      </button>
    </div>
  );
}

interface EmptyStateProps {
  query: string;
  onClearQuery: () => void;
}

export function EmptyState({ query, onClearQuery }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center gap-3 px-4 py-16 text-center">
      <EmptyIcon />
      {query ? (
        <>
          <p className="text-sm text-slate-300">Ningún lead coincide con «{query}»</p>
          <button type="button" onClick={onClearQuery} className={btn('secondary', 'sm')}>
            Limpiar búsqueda
          </button>
        </>
      ) : (
        <p className="text-sm text-slate-400">No hay leads en este filtro.</p>
      )}
    </div>
  );
}
