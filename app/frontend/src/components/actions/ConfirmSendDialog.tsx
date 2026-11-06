import { btn } from '../../lib/ui';
import { Modal } from '../ui/Modal';
import type { CanalInfo } from './BulkActionBar';

const DETALLE: Record<string, string> = {
  whatsapp: 'Solo se escribe a móviles que no hayan recibido ya un WhatsApp ni hayan pedido la baja.',
  email: 'Solo se escribe a direcciones que no hayan recibido ya un email ni hayan pedido la baja.',
  instagram: 'Solo se escribe a cuentas que no hayan recibido ya un mensaje ni hayan pedido la baja.',
};

interface ConfirmSendDialogProps {
  canal: CanalInfo | null;
  onCancel: () => void;
  onConfirm: () => void;
}

/** Los envíos son reales e irreversibles: siempre se confirman con el número concreto. */
export function ConfirmSendDialog({ canal, onCancel, onConfirm }: ConfirmSendDialogProps) {
  const n = canal?.destinatarios ?? 0;
  const negocios = n === 1 ? 'negocio' : 'negocios';

  return (
    <Modal open={canal !== null} onClose={onCancel} label="Confirmar envío" className="w-full max-w-md space-y-4">
      {canal && (
        <>
          <div className="space-y-2">
            <h2 className="text-base font-semibold text-slate-100">
              ¿Enviar {canal.label} a {n} {negocios}?
            </h2>
            <p className="text-sm text-slate-400">{DETALLE[canal.canal]}</p>
            <p className="text-sm text-slate-400">Los mensajes se envían de verdad y no se pueden deshacer.</p>
          </div>
          <div className="flex justify-end gap-2">
            <button type="button" onClick={onCancel} className={btn('ghost')} autoFocus>
              Cancelar
            </button>
            <button type="button" onClick={onConfirm} className={btn('primary')}>
              {canal.icon} Enviar {n} {canal.label}
            </button>
          </div>
        </>
      )}
    </Modal>
  );
}
