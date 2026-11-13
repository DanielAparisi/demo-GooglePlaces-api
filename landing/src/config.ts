/**
 * Todo lo que cambia de la agencia vive aquí: nombre, contacto, precios.
 * ⚠ Antes de publicar, rellena los marcadores marcados con TODO.
 */
import planes from '../../app/scraper-python/comun/planes.json';

export const SITIO = {
  marca: 'Barrio Digital', // TODO: nombre definitivo
  lema: 'Webs para negocios de barrio',
  url: 'https://barriodigital.es', // TODO: tu dominio
  ciudad: 'Murcia', // TODO: tu ciudad / zona de trabajo
  /** Solo dígitos con prefijo de país, sin "+": 34600111222 */
  whatsapp: '34600000000', // TODO
  telefono: '600 000 000', // TODO
  email: 'hola@barriodigital.es', // TODO
  titular: 'Nombre y apellidos', // TODO: datos del aviso legal (LSSI)
  nif: '00000000X', // TODO
};

/** Oferta para negocios locales (página principal). */
export const WEB = {
  precio: 90,
  plazoDias: 7,
  incluye: [
    'Diseño a medida, pensado para el móvil',
    'Hasta 4 secciones: inicio, servicios, sobre ti y contacto',
    'Botones de llamar y de WhatsApp siempre a mano',
    'Mapa, horario y reseñas de Google',
    'Revisión de tu ficha de Google Business',
    'Dos rondas de cambios antes de publicar',
  ],
  /** TODO: confirma qué cubres tú y qué paga el cliente aparte */
  nota: 'Pago único. Dominio y alojamiento aparte, desde unos 10 €/año: te lo dejamos montado a tu nombre.',
};

/**
 * Suscripciones de listas para agencias (/agencias). Precio, cantidad y exclusividad salen
 * de app/scraper-python/comun/planes.json, el mismo fichero que usa el panel: cámbialos allí.
 * Aquí solo va el texto comercial de cada plan.
 */
const TEXTOS_PLAN: Record<string, { extras: string[]; destacado?: boolean }> = {
  basico: { extras: ['1 sector + 1 ciudad', 'CSV listo para Excel o tu CRM'] },
  estandar: { extras: ['Varios sectores y ciudades', 'Filtro por canal (móvil, email, redes)'], destacado: true },
  premium: { extras: ['Todo lo del Estándar', 'Exclusividad: nadie más recibe esos leads'] },
};

type PlanJson = { nombre: string; cantidad: number; exclusivo: boolean; precio: number };

export const PLANES_LISTAS = Object.entries(planes as Record<string, PlanJson | string>)
  .filter((e): e is [string, PlanJson] => !e[0].startsWith('_'))
  .map(([id, p]) => ({
    id,
    nombre: p.nombre,
    leads: p.cantidad,
    precio: p.precio,
    extras: TEXTOS_PLAN[id]?.extras ?? [],
    destacado: TEXTOS_PLAN[id]?.destacado ?? false,
  }));

export const waLink = (texto: string) =>
  `https://wa.me/${SITIO.whatsapp}?text=${encodeURIComponent(texto)}`;
export const mailLink = (asunto: string) =>
  `mailto:${SITIO.email}?subject=${encodeURIComponent(asunto)}`;
