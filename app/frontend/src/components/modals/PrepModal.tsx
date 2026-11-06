import { useState } from 'react';
import { maquetaUrl } from '../../lib/api';
import { ciudad, telHref } from '../../lib/format';
import type { GeneracionTipo, Lead } from '../../types/lead';
import { Modal } from '../ui/Modal';

interface PrepModalProps {
  /** null = modal cerrado */
  lead: Lead | null;
  onClose: () => void;
  onGenerate: (id: number, tipo: GeneracionTipo) => Promise<void>;
}

const GEN_BTN = 'px-3 py-2 text-sm font-semibold rounded-lg text-white disabled:opacity-40 transition-colors';

export function PrepModal({ lead, onClose, onGenerate }: PrepModalProps) {
  const [generating, setGenerating] = useState<GeneracionTipo | null>(null);

  const generar = async (tipo: GeneracionTipo) => {
    if (!lead) return;
    setGenerating(tipo);
    try {
      await onGenerate(lead.id, tipo);
    } finally {
      setGenerating(null);
    }
  };

  const tel = lead?.['Teléfono'] ?? '';
  const maqueta = lead?.Maqueta ?? '';

  return (
    <Modal
      open={lead !== null}
      onClose={onClose}
      label="Preparar contacto"
      className="flex flex-col gap-4 w-full max-w-2xl max-h-[90vh]"
    >
      {lead && (
        <>
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-slate-100 font-bold text-lg">{lead['Nombre del negocio']}</h2>
              <p className="text-slate-400 text-sm">
                {lead['Categoría'] ?? ''} · {ciudad(lead['Ubicación'])}
              </p>
            </div>
            <a
              href={tel ? telHref(tel) : undefined}
              className="shrink-0 px-3 py-2 text-sm font-semibold rounded-lg bg-green-600 text-white hover:bg-green-500 transition-colors"
            >
              {tel ? `📞 ${tel}` : 'Sin teléfono'}
            </a>
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              disabled={generating !== null}
              onClick={() => void generar('guion')}
              className={`${GEN_BTN} bg-blue-600 hover:bg-blue-500`}
            >
              {generating === 'guion' ? 'Generando…' : 'Generar guion'}
            </button>
            <button
              type="button"
              disabled={generating !== null}
              onClick={() => void generar('maqueta')}
              className={`${GEN_BTN} bg-amber-600 hover:bg-amber-500`}
            >
              {generating === 'maqueta' ? 'Generando…' : 'Generar maqueta'}
            </button>
            {maqueta && (
              <a
                href={maquetaUrl(maqueta)}
                target="_blank"
                rel="noopener"
                className="px-3 py-2 text-sm font-semibold rounded-lg bg-slate-700 text-slate-100 hover:bg-slate-600 transition-colors"
              >
                Abrir maqueta ↗
              </a>
            )}
          </div>

          <pre className="flex-1 overflow-y-auto whitespace-pre-wrap font-sans text-sm leading-relaxed text-slate-200 bg-slate-950/60 border border-slate-800 rounded-xl p-4 min-h-40">
            {lead.Guion || 'Pulsa "Generar guion" para preparar la llamada.'}
          </pre>

          <button
            type="button"
            onClick={onClose}
            className="self-end px-4 py-2 text-sm font-semibold rounded-lg bg-slate-700 text-slate-200 hover:bg-slate-600 transition-colors"
          >
            Cerrar
          </button>
        </>
      )}
    </Modal>
  );
}
