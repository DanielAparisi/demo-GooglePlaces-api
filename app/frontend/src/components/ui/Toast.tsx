import type { ToastState } from '../../hooks/useToast';

export function Toast({ toast }: { toast: ToastState }) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={`toast-base ${toast.visible ? 'show' : ''} ${toast.type}`}
    >
      {toast.msg}
    </div>
  );
}
