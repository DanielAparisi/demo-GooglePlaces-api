import type { NivelOportunidad } from './lead';

export type PlanId = 'basico' | 'estandar' | 'premium';
export type CanalLista = 'movil' | 'telefono' | 'email' | 'redes';

export interface Plan {
  id: PlanId;
  nombre: string;
  cantidad: number;
  exclusivo: boolean;
  /** €/mes */
  precio: number;
}

/** Lo que se pide a POST /api/listas y /api/listas/simular. */
export interface Pedido {
  cliente: string;
  plan: PlanId | null;
  cantidad?: number | null;
  sectores: string[];
  ciudades: string[];
  requiere: CanalLista[];
  puntuacion_min: number;
  exclusivo: boolean;
}

export interface ResumenLista {
  pedidos: number;
  entregados: number;
  faltan: number;
  disponibles: number;
  descartes: Record<string, number>;
  por_nivel: Record<NivelOportunidad, number>;
  por_grupo: Record<string, number>;
  puntuacion_media: number;
}

export type FilaEntrega = Record<string, string | number>;

export interface ResultadoLista {
  pedido: Pedido & { cantidad: number };
  resumen: ResumenLista;
  sugerencias: string[];
  muestra: FilaEntrega[];
  /** Solo al crear */
  entrega?: string;
  archivo?: string;
}

export interface Suscripcion {
  cliente: string;
  plan: PlanId | null;
  entregas: number;
  leads: number;
  ultima: string;
  proxima: string;
  /** Días hasta la próxima entrega (negativo = atrasada). */
  dias: number;
  ultimo_pedido: Pedido;
}

export interface Entrega {
  id: string;
  cliente: string;
  fecha: string;
  exclusivo: boolean;
  archivo: string;
  pedido: Pedido;
  n_leads: number;
  descargable: boolean;
}

export interface ResumenListas {
  planes: Plan[];
  clientes: Suscripcion[];
  entregas: Entrega[];
}
