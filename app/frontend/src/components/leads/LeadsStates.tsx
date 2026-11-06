import { EmptyIcon, SpinnerIcon } from '../ui/icons';

export function LoadingState() {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-slate-500 gap-3">
      <SpinnerIcon />
      <span className="text-sm">Cargando leads...</span>
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-3">
      <p className="text-red-400 text-sm">Error: {message}</p>
    </div>
  );
}

export function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-slate-500 gap-3">
      <EmptyIcon />
      <p className="text-sm">No se encontraron leads que coincidan.</p>
    </div>
  );
}
