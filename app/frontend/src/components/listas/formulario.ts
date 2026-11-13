import type { CanalLista, Pedido, PlanId } from '../../types/lista';

/** Estado del formulario: las listas se escriben como texto separado por comas. */
export interface FormPedido {
  cliente: string;
  plan: PlanId | null;
  cantidad: string;
  sectores: string;
  ciudades: string;
  requiere: CanalLista[];
  puntuacion_min: number;
  exclusivo: boolean;
}

export const FORM_VACIO: FormPedido = {
  cliente: '',
  plan: 'basico',
  cantidad: '',
  sectores: '',
  ciudades: '',
  requiere: [],
  puntuacion_min: 0,
  exclusivo: false,
};

const lista = (texto: string) => texto.split(',').map((s) => s.trim()).filter(Boolean);

export function aPedido(f: FormPedido): Pedido {
  const cantidad = Number.parseInt(f.cantidad, 10);
  return {
    cliente: f.cliente.trim(),
    plan: f.plan,
    cantidad: Number.isFinite(cantidad) && cantidad > 0 ? cantidad : null,
    sectores: lista(f.sectores),
    ciudades: lista(f.ciudades),
    requiere: f.requiere,
    puntuacion_min: f.puntuacion_min,
    exclusivo: f.exclusivo,
  };
}

/** Rellena el formulario con el último pedido de una agencia (la entrega de este mes). */
export function desdePedido(p: Pedido): FormPedido {
  return {
    cliente: p.cliente,
    plan: p.plan ?? null,
    // Si venía de un plan, la cantidad la fija el plan
    cantidad: p.plan ? '' : String(p.cantidad ?? ''),
    sectores: p.sectores.join(', '),
    ciudades: p.ciudades.join(', '),
    requiere: p.requiere,
    puntuacion_min: p.puntuacion_min,
    exclusivo: p.plan === 'premium' ? false : p.exclusivo,
  };
}

export const CANALES: { id: CanalLista; label: string }[] = [
  { id: 'movil', label: 'Móvil' },
  { id: 'telefono', label: 'Teléfono' },
  { id: 'email', label: 'Email' },
  { id: 'redes', label: 'Redes sociales' },
];

const FECHA = new Intl.DateTimeFormat('es-ES', { day: 'numeric', month: 'short' });
export const fechaCorta = (iso: string) => {
  const d = new Date(`${iso}T00:00:00`);
  return Number.isNaN(d.getTime()) ? iso : FECHA.format(d);
};

export const euros = (n: number) =>
  new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(n);
