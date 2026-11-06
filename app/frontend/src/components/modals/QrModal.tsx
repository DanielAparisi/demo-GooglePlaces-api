import { useQrCode } from '../../hooks/useQrCode';
import { btn } from '../../lib/ui';
import { Modal } from '../ui/Modal';

interface QrModalProps {
  open: boolean;
  onClose: () => void;
}

export function QrModal({ open, onClose }: QrModalProps) {
  const src = useQrCode(open);

  return (
    <Modal open={open} onClose={onClose} label="Vincular WhatsApp" className="flex w-full max-w-sm flex-col items-center gap-4 text-center">
      <h2 className="text-base font-semibold text-slate-100">Vincular WhatsApp</h2>
      <p className="text-sm leading-relaxed text-slate-400">
        En el móvil: <span className="text-slate-200">Ajustes → Dispositivos vinculados → Vincular un dispositivo</span>, y escanea el código.
      </p>
      <div className="flex h-64 w-64 items-center justify-center rounded-xl bg-white p-2">
        {src ? (
          <img src={src} alt="Código QR de WhatsApp" className="max-h-full max-w-full" />
        ) : (
          <span className="px-6 text-sm text-slate-500">
            El QR aparece aquí cuando lanzas un envío de WhatsApp.
          </span>
        )}
      </div>
      <p className="text-xs text-slate-500">Se renueva solo cada pocos segundos.</p>
      <button type="button" onClick={onClose} className={btn('secondary')} autoFocus>
        Cerrar
      </button>
    </Modal>
  );
}
