import { useCallback, useEffect, useRef, useState } from 'react';
import type { Notify, ToastType } from '../types/lead';

const DURATION_MS = 3500;

export interface ToastState {
  msg: string;
  type: ToastType;
  visible: boolean;
}

export function useToast() {
  const [toast, setToast] = useState<ToastState>({ msg: '', type: 'info', visible: false });
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined);

  const notify: Notify = useCallback((msg, type = 'info') => {
    clearTimeout(timer.current);
    setToast({ msg, type, visible: true });
    timer.current = setTimeout(() => setToast((t) => ({ ...t, visible: false })), DURATION_MS);
  }, []);

  useEffect(() => () => clearTimeout(timer.current), []);

  return { toast, notify };
}
