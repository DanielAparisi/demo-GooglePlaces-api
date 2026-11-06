import { safeUrl } from '../../lib/format';
import { REDES } from '../../lib/leads';
import type { Lead } from '../../types/lead';

export function SocialLinks({ lead }: { lead: Lead }) {
  const links = REDES.map((red) => ({ ...red, url: safeUrl(lead[red.key]) })).filter((r) => r.url);

  if (links.length === 0) return <span className="text-slate-700">—</span>;

  return (
    <div className="social-links">
      {links.map(({ key, clase, etiqueta, url }) => (
        <a key={key} href={url!} target="_blank" rel="noopener noreferrer" className={clase} title={key}>
          {etiqueta}
        </a>
      ))}
    </div>
  );
}
