export function ApiStatusBadge({ connected }: { connected: boolean | null }) {
  const [dot, label] =
    connected === null
      ? ['bg-slate-500 animate-pulse', 'Conectando…']
      : connected
        ? ['bg-emerald-400', 'API conectada']
        : ['bg-red-400', 'API sin conexión'];

  return (
    <span className="flex items-center gap-2 text-xs text-slate-400" role="status">
      <span className={`h-1.5 w-1.5 rounded-full ${dot}`} />
      <span className="hidden md:inline">{label}</span>
      <span className="sr-only md:hidden">{label}</span>
    </span>
  );
}
