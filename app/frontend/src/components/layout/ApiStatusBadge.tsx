export function ApiStatusBadge({ connected }: { connected: boolean | null }) {
  const dot =
    connected === null ? 'bg-slate-600 animate-pulse' : connected ? 'bg-green-400' : 'bg-red-400';
  const text =
    connected === null ? 'text-slate-400' : connected ? 'text-green-400' : 'text-red-400';
  const label = connected === null ? '...' : connected ? 'conectado' : 'sin conexión';

  return (
    <div className="flex items-center gap-1.5 text-xs text-slate-500 border-l border-slate-700 pl-4">
      <span className={`w-1.5 h-1.5 rounded-full ${dot}`} />
      <span className={text}>{label}</span>
    </div>
  );
}
