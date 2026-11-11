import { useEffect, useRef, useState } from 'react';
import { maquetaUrl } from '../../lib/api';
import { telHref } from '../../lib/format';
import { ESTADOS_LLAMADA } from '../../lib/leads';
import { btn } from '../../lib/ui';
import type { GeneracionTipo, Lead, LlamadaEstado } from '../../types/lead';
import { ExternalIcon, PhoneIcon, SparklesIcon, XIcon } from '../ui/icons';
import { ContactChannels, LeadTitle, PhoneCell, StatusBadge } from './LeadBits';

interface LeadDrawerProps {
  /** null = cerrado */
  lead: Lead | null;
  onClose: () => void;
  onGenerate: (id: number, tipo: GeneracionTipo) => Promise<void>;
  onMarkCall: (id: number, estado: LlamadaEstado) => void;
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-3 border-t border-slate-800 px-5 py-5">
      <h3 className="text-xs font-medium uppercase tracking-wider text-slate-500">{title}</h3>
      {children}
    </section>
  );
}

/** Panel lateral con todo lo de un lead: contacto, resultado de la llamada, guion y maqueta. */
export function LeadDrawer({ lead, onClose, onGenerate, onMarkCall }: LeadDrawerProps) {
  const [generating, setGenerating] = useState<GeneracionTipo | null>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const abierto = lead !== null;

  useEffect(() => {
    if (!abierto) return;
    const volverA = document.activeElement as HTMLElement | null;
    closeRef.current?.focus();
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('keydown', onKey);
      volverA?.focus(); // el foco vuelve a la fila que lo abrió
    };
  }, [abierto, onClose]);

  if (!lead) return null;

  const generar = async (tipo: GeneracionTipo) => {
    setGenerating(tipo);
    try {
      await onGenerate(lead.id, tipo);
    } finally {
      setGenerating(null);
    }
  };

  const tel = lead['Teléfono'] ?? '';
  const estado = lead.Llamada ?? '';

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-[2px]" onClick={onClose} aria-hidden="true" />
      <aside
        role="dialog"
        aria-modal="true"
        aria-label={`Lead: ${lead['Nombre del negocio'] ?? ''}`}
        className="relative flex h-full w-full max-w-lg flex-col overflow-y-auto border-l border-slate-800 bg-slate-900 shadow-card"
      >
        <header className="flex items-start gap-3 px-5 py-5">
          <div className="min-w-0 flex-1 space-y-2">
            <LeadTitle lead={lead} />
            <StatusBadge lead={lead} />
          </div>
          <button ref={closeRef} type="button" onClick={onClose} className={btn('ghost', 'icon')} aria-label="Cerrar">
            <XIcon />
          </button>
        </header>

        {lead.oportunidad != null && (
          <Section title={`Oportunidad web · ${lead.oportunidad}/100 (${lead.oportunidad_nivel ?? ''})`}>
            <div className="h-1.5 overflow-hidden rounded-full bg-slate-800" aria-hidden="true">
              <div className="h-full rounded-full bg-brand-500" style={{ width: `${lead.oportunidad}%` }} />
            </div>
            {lead.oportunidad_motivos && lead.oportunidad_motivos.length > 0 && (
              <ul className="list-disc space-y-1 pl-5 text-sm text-slate-300">
                {lead.oportunidad_motivos.map((m) => <li key={m}>{m}</li>)}
              </ul>
            )}
          </Section>
        )}

        <Section title="Contacto">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <PhoneCell lead={lead} />
            <ContactChannels lead={lead} vacio={null} />
          </div>
          {lead.Email && <p className="truncate text-sm text-slate-400">{lead.Email}</p>}
          {tel && (
            <a href={telHref(tel)} className={`${btn('success')} w-full`}>
              <PhoneIcon /> Llamar
            </a>
          )}
        </Section>

        {/* Vale para cualquier canal (llamada, WhatsApp, email, Instagram): alimenta la calibración del modelo */}
        <Section title="Resultado del contacto">
          <div className="grid grid-cols-3 gap-1 rounded-lg bg-slate-950/60 p-1 ring-1 ring-inset ring-slate-800">
            {ESTADOS_LLAMADA.map(({ valor, texto }) => {
              const activo = estado === valor;
              return (
                <button
                  key={valor}
                  type="button"
                  aria-pressed={activo}
                  onClick={() => onMarkCall(lead.id, activo ? '' : valor)}
                  className={`h-8 rounded-md text-xs font-medium transition-colors focus-visible:outline-2 focus-visible:outline-brand-500 ${
                    activo ? 'bg-slate-700 text-slate-100 shadow-sm' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {texto}
                </button>
              );
            })}
          </div>
          {lead['Fecha llamada'] && (
            <p className="text-xs text-slate-500">Último contacto: {lead['Fecha llamada']} · pulsa el estado activo para deshacerlo</p>
          )}
        </Section>

        <Section title="Preparar contacto">
          <div className="flex flex-wrap gap-2">
            <button type="button" disabled={generating !== null} onClick={() => void generar('guion')} className={btn('primary', 'sm')}>
              <SparklesIcon className="h-3.5 w-3.5" />
              {generating === 'guion' ? 'Generando…' : lead.Guion ? 'Regenerar guion' : 'Generar guion'}
            </button>
            <button type="button" disabled={generating !== null} onClick={() => void generar('maqueta')} className={btn('secondary', 'sm')}>
              {generating === 'maqueta' ? 'Generando…' : lead.Maqueta ? 'Regenerar maqueta' : 'Generar maqueta'}
            </button>
            {lead.Maqueta && (
              <a href={maquetaUrl(lead.Maqueta)} target="_blank" rel="noopener" className={btn('ghost', 'sm')}>
                Abrir maqueta <ExternalIcon />
              </a>
            )}
          </div>
          {lead.Guion ? (
            <pre className="whitespace-pre-wrap rounded-lg bg-slate-950/60 p-4 font-sans text-sm leading-relaxed text-slate-200 ring-1 ring-inset ring-slate-800">
              {lead.Guion}
            </pre>
          ) : (
            <p className="text-sm text-slate-500">Genera un guion para tener a mano qué decir en la llamada.</p>
          )}
        </Section>

        {lead.Mensaje && (
          <Section title="Mensaje preparado">
            <p className="whitespace-pre-wrap text-sm text-slate-300">{lead.Mensaje}</p>
          </Section>
        )}
      </aside>
    </div>
  );
}
