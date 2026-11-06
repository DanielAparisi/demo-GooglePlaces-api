import { PAGE_SIZE } from '../../lib/config';
import { btn } from '../../lib/ui';
import { ChevronLeftIcon, ChevronRightIcon } from '../ui/icons';

interface PaginationProps {
  page: number;
  totalPages: number;
  total: number;
  onPageChange: (page: number) => void;
}

export function Pagination({ page, totalPages, total, onPageChange }: PaginationProps) {
  const from = total === 0 ? 0 : page * PAGE_SIZE + 1;
  const to = Math.min((page + 1) * PAGE_SIZE, total);

  return (
    <div className="flex items-center justify-between gap-4 border-t border-slate-800 px-4 py-3 text-xs text-slate-500">
      <span className="tabular-nums">
        {from}–{to} de {total} {total === 1 ? 'lead' : 'leads'}
      </span>
      {totalPages > 1 && (
        <div className="flex items-center gap-1">
          <button type="button" className={btn('ghost', 'icon')} disabled={page === 0}
            onClick={() => onPageChange(page - 1)} aria-label="Página anterior">
            <ChevronLeftIcon />
          </button>
          <span className="px-2 tabular-nums text-slate-400">{page + 1} / {totalPages}</span>
          <button type="button" className={btn('ghost', 'icon')} disabled={page >= totalPages - 1}
            onClick={() => onPageChange(page + 1)} aria-label="Página siguiente">
            <ChevronRightIcon />
          </button>
        </div>
      )}
    </div>
  );
}
