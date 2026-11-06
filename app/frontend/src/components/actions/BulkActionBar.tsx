import { useState, type ReactNode } from 'react';
import { useLaunch } from '../../hooks/useLaunch';
import type { LeadCounts } from '../../lib/leads';
import { btn } from '../../lib/ui';
import type { Canal, Notify } from '../../types/lead';
import { InstagramIcon, MailIcon, WhatsAppIcon, XIcon } from '../ui/icons';
import { ConfirmSendDialog } from './ConfirmSendDialog';

interface BulkActionBarProps {
  counts: LeadCounts;
  notify: Notify;
  onClear: () => void;
  onWhatsappLaunched: () => void;
}

interface CanalInfo {
  canal: Canal;
  label: string;
  icon: ReactNode;
  destinatarios: number;
  sinDestinatarios: string;
}

/** Aparece solo con leads seleccionados: es el único sitio desde el que se envía. */
export function BulkActionBar({ counts, notify, onClear, onWhatsappLaunched }: BulkActionBarProps) {
  const [confirmando, setConfirmando] = useState<CanalInfo | null>(null);
  const lanzadores = {
    whatsapp: useLaunch('whatsapp', notify, onWhatsappLaunched),
    email: useLaunch('email', notify),
    instagram: useLaunch('instagram', notify),
  };

  const canales: CanalInfo[] = [
    { canal: 'whatsapp', label: 'WhatsApp', icon: <WhatsAppIcon />, destinatarios: counts.selectedWithMobile,
      sinDestinatarios: 'Ningún seleccionado tiene móvil' },
    { canal: 'email', label: 'Email', icon: <MailIcon />, destinatarios: counts.selectedWithEmail,
      sinDestinatarios: 'Ningún seleccionado tiene email' },
    { canal: 'instagram', label: 'Instagram', icon: <InstagramIcon />, destinatarios: counts.selectedWithInstagram,
      sinDestinatarios: 'Ningún seleccionado tiene Instagram' },
  ];

  if (counts.selected === 0) return null;

  return (
    <>
      <div className="fixed inset-x-0 bottom-4 z-40 flex justify-center px-4">
        <div
          role="toolbar"
          aria-label="Acciones sobre los seleccionados"
          className="flex w-full max-w-2xl flex-wrap items-center gap-2 rounded-card border border-slate-700 bg-slate-900/95 p-2 pl-4 shadow-card backdrop-blur"
        >
          <span className="mr-auto text-sm text-slate-300">
            <span className="font-semibold tabular-nums text-slate-100">{counts.selected}</span>{' '}
            {counts.selected === 1 ? 'seleccionado' : 'seleccionados'}
          </span>
          {canales.map((c) => (
            <button
              key={c.canal}
              type="button"
              disabled={c.destinatarios === 0 || lanzadores[c.canal].launching}
              title={c.destinatarios === 0 ? c.sinDestinatarios : `Enviar a ${c.destinatarios}`}
              onClick={() => setConfirmando(c)}
              className={btn('secondary', 'sm')}
            >
              {c.icon}
              {lanzadores[c.canal].launching ? 'Lanzando…' : c.label}
              <span className="tabular-nums text-slate-400">{c.destinatarios}</span>
            </button>
          ))}
          <button type="button" onClick={onClear} className={btn('ghost', 'icon')} aria-label="Quitar selección" title="Quitar selección">
            <XIcon />
          </button>
        </div>
      </div>

      <ConfirmSendDialog
        canal={confirmando}
        onCancel={() => setConfirmando(null)}
        onConfirm={() => {
          if (confirmando) void lanzadores[confirmando.canal].launch();
          setConfirmando(null);
        }}
      />
    </>
  );
}

export type { CanalInfo };
