import { useEffect, useRef, type ReactNode } from 'react';

interface ModalProps {
  open: boolean;
  onClose: () => void;
  /** Clases del panel (ancho, layout interno…) */
  className?: string;
  label: string;
  children: ReactNode;
}

/** Diálogo centrado: cierra con Escape o clic fuera y devuelve el foco al cerrar. */
export function Modal({ open, onClose, className = '', label, children }: ModalProps) {
  const panel = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const volverA = document.activeElement as HTMLElement | null;
    // Foco al elemento con autoFocus o, si no hay, al panel
    if (!panel.current?.contains(document.activeElement)) panel.current?.focus();
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('keydown', onKey);
      volverA?.focus();
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-[2px]"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        ref={panel}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
        aria-label={label}
        className={`rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-card outline-none ${className}`}
      >
        {children}
      </div>
    </div>
  );
}
