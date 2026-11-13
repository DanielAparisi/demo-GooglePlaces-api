/**
 * Todo lo que cambia de la agencia vive aquí: nombre, contacto, precios.
 * ⚠ Antes de publicar, rellena los marcadores marcados con TODO.
 */
import planes from '../../app/comun/comun/planes.json';

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

/**
 * Oferta para negocios locales (página principal). Mismos precios que el README
 * (sección "Precios") y docs/precios-webs.md: si cambias uno, cambia los tres.
 */
type Paquete = {
  id: string;
  nombre: string;
  precio: number;
  plazoDias: number;
  resumen: string;
  incluye: string[];
  destacado?: boolean;
};

const PAQUETES: Paquete[] = [
  {
    id: 'esencial',
    nombre: 'Esencial',
    precio: 90,
    plazoDias: 7,
    resumen: 'Para estar en Google y que te llamen.',
    incluye: [
      'Una página con hasta 4 secciones',
      'Diseño a medida, pensado para el móvil',
      'Botones de llamar y de WhatsApp',
      'Mapa, horario y reseñas de Google',
      'Revisión de tu ficha de Google Business',
      '2 rondas de cambios',
    ],
  },
  {
    id: 'profesional',
    nombre: 'Profesional',
    precio: 180,
    plazoDias: 10,
    resumen: 'Para enseñar tus trabajos y recibir peticiones.',
    incluye: [
      'Todo lo del Esencial',
      'Hasta 5 páginas',
      'Galería de trabajos o antes/después',
      'Formulario de contacto',
      'SEO local básico',
      'Correo profesional (hola@tunegocio.es)',
      '3 rondas de cambios',
    ],
    destacado: true,
  },
  {
    id: 'completa',
    nombre: 'Completa',
    precio: 300,
    plazoDias: 14,
    resumen: 'Para que tus clientes reserven sin llamarte.',
    incluye: [
      'Todo lo del Profesional',
      'Hasta 8 páginas',
      'Reservas o citas online',
      'Carta o catálogo de servicios con precios',
      'Segundo idioma',
      '4 rondas de cambios',
    ],
  },
];

export const WEB = {
  /** Precio más bajo: lo usan el título, el hero y los pasos. */
  desde: Math.min(...PAQUETES.map((p) => p.precio)),
  plazoDias: Math.min(...PAQUETES.map((p) => p.plazoDias)),
  paquetes: PAQUETES,
  extras: [
    { nombre: 'Sección o página adicional', precio: '25 €' },
    { nombre: 'Galería de trabajos', precio: '30 €' },
    { nombre: 'Formulario de contacto', precio: '20 €' },
    { nombre: 'Correo profesional', precio: '20 €' },
    { nombre: 'Reservas o citas online', precio: '60 €' },
    { nombre: 'Segundo idioma', precio: '50 €' },
    { nombre: 'Logo sencillo', precio: '40 €' },
    { nombre: 'Ronda de cambios extra', precio: '15 €' },
    { nombre: 'Entrega urgente (3 días)', precio: '+30 %' },
  ],
  mantenimiento: {
    mes: 15,
    anio: 150,
    incluye: [
      'Dominio y alojamiento gestionados por nosotros',
      '30 minutos de cambios al mes (horario, fotos, precios…)',
      'Copias de seguridad',
      'Sin permanencia: lo dejas cuando quieras',
    ],
  },
  nota: 'Pago único por Bizum. Sin mantenimiento, el dominio y el alojamiento van aparte (desde unos 10 €/año) y te los dejamos montados a tu nombre.',
};

/** Cómo se cobra y se formaliza cada encargo (webs, mantenimiento y apps). */
export const PAGO = {
  metodo: 'Bizum',
  contrato:
    'Antes de empezar firmamos un contrato sencillo con lo que incluye, el plazo, el precio y los cambios. Así los dos sabemos a qué atenernos.',
  plazos:
    'Esencial: al publicar. Profesional y Completa: 50 % al firmar y 50 % al publicar. Mantenimiento: cada mes o un único pago al año.',
};

/** Aplicaciones móviles: proyecto a medida, presupuesto cerrado tras una llamada. */
export const APPS = {
  desde: 2000,
  incluye: [
    'App para iPhone y Android',
    'Diseño a medida de todas las pantallas',
    'Panel para gestionar contenidos, reservas o pedidos',
    'Publicación en App Store y Google Play',
    '3 meses de soporte tras el lanzamiento',
  ],
  mantenimientoMes: 60,
  nota: 'Contrato con presupuesto cerrado. Pago por Bizum: 50 % al firmar y 50 % al publicar. Las cuentas de desarrollador las paga el cliente (Apple 99 $/año, Google 25 $ una vez).',
};

/** "2.000 €" en vez de "2000 €" (es-ES no agrupa los números de 4 cifras). */
export const euros = (n: number) => `${String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.')} €`;

/**
 * Suscripciones de listas para agencias (/agencias). Precio, cantidad y exclusividad salen
 * de app/comun/comun/planes.json, el mismo fichero que usa el panel: cámbialos allí.
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
