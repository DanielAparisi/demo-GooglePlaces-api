import type { ReactNode } from 'react';
import { useLaunch } from '../../hooks/useLaunch';
import type { Canal, Notify } from '../../types/lead';
import { InstagramIcon, MailIcon, QrIcon, WhatsAppIcon } from '../ui/icons';

interface LaunchButtonsProps {
  selectedCount: number;
  selectedWithEmail: number;
  selectedWithInstagram: number;
  notify: Notify;
  onOpenQr: () => void;
}

interface ChannelButtonProps {
  canal: Canal;
  label: string;
  icon: ReactNode;
  className: string;
  enabled: boolean;
  notify: Notify;
  onLaunched?: () => void;
}

const BASE =
  'flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg text-white disabled:opacity-30 disabled:cursor-not-allowed transition-all';

function ChannelButton({ canal, label, icon, className, enabled, notify, onLaunched }: ChannelButtonProps) {
  const { launching, launch } = useLaunch(canal, notify, onLaunched);
  return (
    <button
      type="button"
      onClick={() => void launch()}
      disabled={!enabled || launching}
      className={`${BASE} ${className}`}
    >
      {icon}
      {launching ? 'Lanzando...' : label}
    </button>
  );
}

export function LaunchButtons({
  selectedCount,
  selectedWithEmail,
  selectedWithInstagram,
  notify,
  onOpenQr,
}: LaunchButtonsProps) {
  return (
    <div className="flex items-center gap-2">
      <ChannelButton
        canal="whatsapp"
        label="WhatsApp"
        icon={<WhatsAppIcon />}
        className="bg-green-500 hover:bg-green-400"
        enabled={selectedCount > 0}
        notify={notify}
        onLaunched={onOpenQr}
      />
      <button
        type="button"
        onClick={onOpenQr}
        title="Ver QR de vinculación"
        className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-700 text-slate-200 hover:bg-slate-600 transition-all"
      >
        <QrIcon />
        QR
      </button>
      <ChannelButton
        canal="email"
        label="Email"
        icon={<MailIcon />}
        className="bg-blue-600 hover:bg-blue-500"
        enabled={selectedWithEmail > 0}
        notify={notify}
      />
      <ChannelButton
        canal="instagram"
        label="Instagram"
        icon={<InstagramIcon />}
        className="bg-linear-to-r from-purple-600 to-pink-500 hover:from-purple-500 hover:to-pink-400"
        enabled={selectedWithInstagram > 0}
        notify={notify}
      />
    </div>
  );
}
