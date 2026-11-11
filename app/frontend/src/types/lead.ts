type Texto = string | null | undefined;

export type LlamadaEstado = '' | 'No contesta' | 'Interesado' | 'No interesado';
export type Sector = 'reformas' | 'taller' | 'fisioterapia';
export type GeneracionTipo = 'guion' | 'maqueta';
export type Canal = 'whatsapp' | 'email' | 'instagram';
export type ToastType = 'info' | 'success' | 'error';
export type NivelOportunidad = 'Alta' | 'Media' | 'Baja';

/** Lead tal y como lo devuelve GET /api/leads (selected puede llegar como "True"). */
export interface RawLead {
  id: number;
  selected: boolean | string;
  email_enviado?: boolean;
  sector?: Texto;
  /** Probabilidad 0-100 de que necesite (y compre) una web, calculada por el backend. */
  oportunidad?: number;
  oportunidad_nivel?: NivelOportunidad;
  oportunidad_motivos?: string[];
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

export interface BloqueModelo {
  id: string;
  nombre: string;
  peso: number;
  peso_base: number;
}

export interface RendimientoNivel {
  nivel: NivelOportunidad;
  leads: number;
  /** Llamadas con resultado (Interesado / No interesado) */
  resultados: number;
  interesados: number;
  /** interesados / resultados, null sin resultados */
  tasa: number | null;
}

export interface ModeloOportunidad {
  bloques: BloqueModelo[];
  calibrado: { fecha: string; resultados: number; interesados: number; confianza: number } | null;
  estado: { resultados: number; interesados: number; no_interesados: number; puede_calibrar: boolean; faltan: number };
  rendimiento: RendimientoNivel[];
}

export type Notify = (msg: string, type?: ToastType) => void;
