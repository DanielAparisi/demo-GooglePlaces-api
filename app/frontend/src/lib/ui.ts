// Variantes de botón y de insignia compartidas: todo el panel usa el mismo lenguaje visual.

type Variante = 'primary' | 'secondary' | 'ghost' | 'success';
type Tamano = 'sm' | 'md' | 'icon';

const BASE =
  'inline-flex items-center justify-center gap-1.5 rounded-lg font-medium whitespace-nowrap transition ' +
  'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500 ' +
  'active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none';

const VARIANTES: Record<Variante, string> = {
  primary: 'bg-brand-600 text-white shadow-sm hover:bg-brand-500',
  secondary: 'bg-slate-800/80 text-slate-200 ring-1 ring-inset ring-slate-700/60 hover:bg-slate-700/80',
  ghost: 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/70',
  success: 'bg-emerald-600 text-white shadow-sm hover:bg-emerald-500',
};

const TAMANOS: Record<Tamano, string> = {
  sm: 'h-8 px-3 text-xs',
  md: 'h-9 px-3.5 text-sm',
  icon: 'h-8 w-8',
};

export const btn = (variante: Variante = 'secondary', tamano: Tamano = 'md') =>
  `${BASE} ${VARIANTES[variante]} ${TAMANOS[tamano]}`;

export type Tono = 'neutral' | 'info' | 'success' | 'warning' | 'danger';

const TONOS: Record<Tono, string> = {
  neutral: 'bg-slate-500/10 text-slate-300 ring-slate-500/20',
  info: 'bg-brand-500/10 text-brand-300 ring-brand-500/25',
  success: 'bg-emerald-500/10 text-emerald-300 ring-emerald-500/20',
  warning: 'bg-amber-500/10 text-amber-300 ring-amber-500/20',
  danger: 'bg-red-500/10 text-red-300 ring-red-500/20',
};

export const badge = (tono: Tono = 'neutral') =>
  `inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${TONOS[tono]}`;

export const formatoNumero = (n: number) => new Intl.NumberFormat('es-ES').format(n);
