import { useEffect, useRef } from 'react';
import { SearchIcon } from '../ui/icons';

interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
}

/** Búsqueda global. "/" la enfoca y Escape la limpia. */
export function SearchInput({ value, onChange }: SearchInputProps) {
  const ref = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const escribiendo = e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement;
      if (e.key === '/' && !escribiendo) {
        e.preventDefault();
        ref.current?.focus();
      }
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, []);

  return (
    <div className="relative">
      <SearchIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
      <input
        ref={ref}
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => e.key === 'Escape' && onChange('')}
        placeholder="Buscar por nombre, ciudad, teléfono…"
        aria-label="Buscar leads"
        className="h-9 w-full rounded-lg border border-slate-800 bg-slate-900 pl-9 pr-10 text-sm text-slate-100 placeholder:text-slate-500 outline-none transition focus:border-brand-500 focus:ring-3 focus:ring-brand-500/20"
      />
      <kbd className="pointer-events-none absolute right-2.5 top-1/2 hidden -translate-y-1/2 rounded border border-slate-700 px-1.5 text-[11px] text-slate-500 sm:block">
        /
      </kbd>
    </div>
  );
}
