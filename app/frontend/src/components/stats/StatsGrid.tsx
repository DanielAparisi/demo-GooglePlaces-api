import type { LeadCounts } from '../../lib/leads';

interface StatsGridProps {
  counts: LeadCounts;
  /** false mientras se cargan los leads */
  ready: boolean;
  emailsSent: number | null;
  instagramSent: number | null;
}

interface StatCardProps {
  label: string;
  value: number | null;
  color: string;
}

function StatCard({ label, value, color }: StatCardProps) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
      <p className="text-xs text-slate-500 uppercase tracking-widest mb-1">{label}</p>
      <p className={`text-2xl font-bold ${color}`}>{value ?? '—'}</p>
    </div>
  );
}

export function StatsGrid({ counts, ready, emailsSent, instagramSent }: StatsGridProps) {
  const v = (n: number) => (ready ? n : null);
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 px-6 py-5">
      <StatCard label="Total leads" value={v(counts.total)} color="text-slate-100" />
      <StatCard label="Seleccionados" value={v(counts.selected)} color="text-sky-400" />
      <StatCard label="Con teléfono" value={v(counts.withPhone)} color="text-green-400" />
      <StatCard label="Emails enviados" value={emailsSent} color="text-blue-400" />
      <StatCard label="Con email" value={v(counts.withEmail)} color="text-purple-400" />
      <StatCard label="DMs Instagram" value={instagramSent} color="text-pink-400" />
    </div>
  );
}
