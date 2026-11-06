type Texto = string | null | undefined;

export type LlamadaEstado = '' | 'No contesta' | 'Interesado' | 'No interesado';
export type Sector = 'reformas' | 'taller' | 'fisioterapia';
export type GeneracionTipo = 'guion' | 'maqueta';
export type Canal = 'whatsapp' | 'email' | 'instagram';
export type ToastType = 'info' | 'success' | 'error';

/** Lead tal y como lo devuelve GET /api/leads (selected puede llegar como "True"). */
export interface RawLead {
  id: number;
  selected: boolean | string;
  email_enviado?: boolean;
  sector?: Texto;
  'Nombre del negocio'?: Texto;
  'Categoría'?: Texto;
  'Ubicación'?: Texto;
  'Teléfono'?: Texto;
  'Tipo teléfono'?: Texto;
  Email?: Texto;
  Facebook?: Texto;
  Instagram?: Texto;
  LinkedIn?: Texto;
  Twitter?: Texto;
  TikTok?: Texto;
  YouTube?: Texto;
  Mensaje?: Texto;
  Guion?: Texto;
  Maqueta?: Texto;
  Llamada?: Texto;
  'Fecha llamada'?: Texto;
}

/** Lead normalizado para el frontend. */
export type Lead = Omit<RawLead, 'selected' | 'email_enviado'> & {
  selected: boolean;
  email_enviado: boolean;
};

export type RedSocial = 'Facebook' | 'Instagram' | 'LinkedIn' | 'Twitter' | 'TikTok' | 'YouTube';

export interface ApiStatus {
  enviados: number;
  emails_enviados: number;
  ig_enviados: number;
}

export interface LaunchResult {
  selected: number;
  pid: number;
}

export type Notify = (msg: string, type?: ToastType) => void;
