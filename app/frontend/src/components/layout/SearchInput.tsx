import { SearchIcon } from '../ui/icons';

interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  variant: 'header' | 'mobile';
}

const STYLES = {
  header: {
    wrapper: 'hidden sm:flex relative',
    icon: 'absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500',
    input:
      'pl-8 pr-3 py-1.5 text-xs w-52 bg-slate-800 border border-slate-700 rounded-lg text-slate-200 placeholder-slate-500 outline-none focus:border-blue-500 focus:w-64 transition-all duration-200',
  },
  mobile: {
    wrapper: 'sm:hidden relative',
    icon: 'absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500',
    input:
      'w-full pl-9 pr-4 py-2 text-sm bg-slate-900 border border-slate-700 rounded-lg text-slate-200 placeholder-slate-500 outline-none focus:border-blue-500 transition-colors',
  },
} as const;

export function SearchInput({ value, onChange, variant }: SearchInputProps) {
  const s = STYLES[variant];
  return (
    <div className={s.wrapper}>
      <SearchIcon className={s.icon} />
      <input
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Buscar leads..."
        aria-label="Buscar leads"
        className={s.input}
      />
    </div>
  );
}
