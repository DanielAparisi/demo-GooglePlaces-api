import { PAGE_SIZE } from '../../lib/config';

interface PaginationProps {
  page: number;
  totalPages: number;
  total: number;
  onPageChange: (page: number) => void;
}

const BTN =
  'px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors';

export function Pagination({ page, totalPages, total, onPageChange }: PaginationProps) {
  if (totalPages <= 1) return null;

  const from = page * PAGE_SIZE + 1;
  const to = Math.min((page + 1) * PAGE_SIZE, total);

  return (
    <div className="flex items-center justify-between gap-4 pt-4 pb-2 text-sm text-slate-400">
      <span>{from}–{to} de {total} leads</span>
      <div className="flex items-center gap-2">
        <button type="button" className={BTN} disabled={page === 0} onClick={() => onPageChange(page - 1)}>
          ← Anterior
        </button>
        <span className="text-slate-500">Página {page + 1} / {totalPages}</span>
        <button type="button" className={BTN} disabled={page >= totalPages - 1} onClick={() => onPageChange(page + 1)}>
          Siguiente →
        </button>
      </div>
    </div>
  );
}
