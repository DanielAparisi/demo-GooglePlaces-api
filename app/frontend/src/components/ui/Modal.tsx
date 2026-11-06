import { useEffect, type ReactNode } from 'react';

interface ModalProps {
  open: boolean;
  onClose: () => void;
  /** Clases del panel (ancho, layout interno…) */
  className?: string;
  label: string;
  children: ReactNode;
}

/** Overlay con cierre por clic en el fondo o con Escape. */
export function Modal({ open, onClose, className = '', label, children }: ModalProps) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label={label}
        className={`bg-slate-900 border border-slate-700 rounded-2xl p-6 mx-4 shadow-2xl ${className}`}
      >
        {children}
      </div>
    </div>
  );
}
