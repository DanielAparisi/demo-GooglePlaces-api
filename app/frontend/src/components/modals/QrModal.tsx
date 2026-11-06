import { useQrCode } from '../../hooks/useQrCode';
import { Modal } from '../ui/Modal';

interface QrModalProps {
  open: boolean;
  onClose: () => void;
}

export function QrModal({ open, onClose }: QrModalProps) {
  const src = useQrCode(open);

  return (
    <Modal open={open} onClose={onClose} label="Vincular WhatsApp" className="flex flex-col items-center gap-4 max-w-sm text-center">
      <h2 className="text-slate-100 font-bold text-lg">Vincular WhatsApp</h2>
      <p className="text-slate-400 text-sm leading-relaxed">
        En tu móvil:{' '}
        <span className="text-slate-200 font-medium">
          WhatsApp → Ajustes → Dispositivos vinculados → Vincular un dispositivo
        </span>{' '}
        y escanea este código.
      </p>
      <div className="w-64 h-64 flex items-center justify-center rounded-xl bg-white p-2">
        {src ? (
          <img src={src} alt="QR de WhatsApp" className="max-w-full max-h-full" />
        ) : (
          <span className="text-slate-500 text-sm px-4">Esperando a que el script genere el QR…</span>
        )}
      </div>
      <p className="text-xs text-slate-500">
        El código caduca y se renueva solo — la imagen se actualiza cada 3 s.
      </p>
      <button
        type="button"
        onClick={onClose}
        className="px-4 py-2 text-sm font-semibold rounded-lg bg-slate-700 text-slate-200 hover:bg-slate-600 transition-colors"
      >
        Cerrar
      </button>
    </Modal>
  );
}
