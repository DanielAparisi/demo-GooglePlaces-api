---
name: ui-design
description: Guía de diseño visual para crear o rediseñar interfaces bonitas y coherentes con Astro + Tailwind v4 (jerarquía, espaciado, color, tipografía, tokens, modo oscuro, micro-interacciones). Úsala siempre que vayas a crear o modificar componentes, páginas, layouts o estilos del frontend (app/frontend), o cuando el usuario pida que algo "se vea mejor", "más moderno", "más profesional" o "más guapo".
---

# UI Design — interfaces bonitas con Astro + Tailwind v4

Objetivo: que cada pantalla parezca diseñada por una sola persona con criterio. Coherencia > originalidad.

## 0. Antes de tocar nada

1. Lee `app/frontend/src/styles/global.css` y `src/layouts/Layout.astro` para conocer tokens y clases existentes.
2. Mira 2-3 componentes similares al que vas a crear y **copia su lenguaje** (radios, tamaños de texto, colores, sombras).
3. Si vas a introducir un valor nuevo (color, radio, sombra), pregúntate si ya existe uno equivalente. Si se repite 3+ veces, conviértelo en token.

## 1. Tokens (Tailwind v4 usa `@theme` en CSS, no `tailwind.config.js`)

Centraliza decisiones en `global.css`:

```css
@import "tailwindcss";

@theme {
  --color-brand-400: oklch(0.72 0.15 255);
  --color-brand-500: oklch(0.63 0.19 258);
  --color-brand-600: oklch(0.55 0.20 262);
  --radius-card: 0.875rem;
  --shadow-card: 0 1px 2px rgb(0 0 0 / .3), 0 8px 24px -12px rgb(0 0 0 / .5);
  --font-sans: "Inter Variable", ui-sans-serif, system-ui, sans-serif;
}
```

Esto genera utilidades `bg-brand-500`, `rounded-card`, `shadow-card`, `font-sans`. Usa clases semánticas en vez de repetir `blue-500` por todas partes.

## 2. Jerarquía visual

- **Una sola acción primaria por zona.** El resto: secundarias (`bg-slate-800`) o terciarias (texto/ghost).
- Jerarquía por **peso y color** antes que por tamaño: `text-slate-100 font-semibold` (título) → `text-slate-400` (secundario) → `text-slate-500` (meta).
- Escala tipográfica limitada: `text-xs`, `text-sm`, `text-base`, `text-lg`, `text-2xl`. No inventes `text-[13px]` salvo casos justificados.
- Títulos grandes: `tracking-tight`. Etiquetas en mayúsculas: `text-[11px] uppercase tracking-wider font-medium text-slate-500`.
- Números en tablas/métricas: `tabular-nums`.

## 3. Espaciado y layout

- Escala de 4px: usa `1, 1.5, 2, 3, 4, 6, 8, 12, 16`. Evita valores sueltos (`p-[13px]`).
- **Más espacio entre grupos que dentro de grupos** (ley de proximidad): `gap-2` dentro de un grupo, `gap-6` entre grupos.
- Preferir `flex`/`grid` + `gap` en vez de márgenes en hijos.
- Contenedores: `max-w-7xl mx-auto px-4 sm:px-6`. Texto largo: `max-w-prose`.
- Mobile-first: diseña a 375px y escala con `sm: md: lg:`. Nada de scroll horizontal accidental.

## 4. Color (tema oscuro slate actual)

| Rol | Clases |
|---|---|
| Fondo app | `bg-slate-950` |
| Superficie (card/panel) | `bg-slate-900` + `border border-slate-800` |
| Superficie elevada (popover/modal) | `bg-slate-900/95 backdrop-blur` + `border-slate-700` + sombra |
| Hover de fila/ítem | `hover:bg-slate-800/50` |
| Texto | `slate-100` / `slate-300` / `slate-400` / `slate-500` |
| Acento | `blue-500` (o `brand-*`) |
| Éxito / aviso / error | `green-400` / `amber-400` / `red-400` sobre fondos `*-500/10` con borde `*-500/20` |

Reglas:
- 90% neutros, 10% color. El color comunica estado o acción, no decora.
- Badges/alerts de color: `bg-green-500/10 text-green-400 ring-1 ring-inset ring-green-500/20` (más elegante que fondos sólidos).
- Contraste mínimo WCAG AA: 4.5:1 texto normal. `slate-500` sobre `slate-950` es el mínimo para texto pequeño; no bajes de ahí.
- Degradados: sutiles y con propósito (`bg-linear-to-br from-blue-500/20 to-indigo-500/5`). Nunca arcoíris.

## 5. Profundidad y detalle ("lo que hace que se vea caro")

- Bordes de 1px semitransparentes (`border-white/5`, `border-slate-800`) en lugar de sombras duras en tema oscuro.
- Highlight interior en superficies: `shadow-[inset_0_1px_0_0_rgb(255_255_255/0.04)]`.
- Radios consistentes: inputs/botones `rounded-lg`, cards `rounded-xl`, modales `rounded-2xl`. Elementos anidados: radio interior = radio exterior − padding.
- Iconos: un solo set (stroke 1.5–2, `w-4 h-4` junto a texto `text-sm`), `currentColor`, alineados con `items-center`.
- `antialiased` en `<html>` (ya está).

## 6. Movimiento

- Transiciones cortas: `transition-colors duration-150` para hover; `duration-200 ease-out` para entrada de paneles.
- Anima solo `opacity` y `transform` (rendimiento).
- Respeta `motion-reduce:transition-none` / `motion-safe:animate-*`.
- Feedback táctil en botones: `active:scale-[0.98]`.
- Skeletons con `animate-pulse bg-slate-800 rounded` en vez de spinners para cargas de contenido.

## 7. Componentes base (patrones de referencia)

**Botón primario**
```html
<button class="inline-flex items-center gap-1.5 h-9 px-3.5 rounded-lg text-sm font-semibold
  bg-blue-600 text-white shadow-sm hover:bg-blue-500 active:scale-[0.98]
  focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500
  disabled:opacity-40 disabled:pointer-events-none transition">
```

**Card**
```html
<section class="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-card">
```

**Input**
```html
<input class="h-9 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 text-sm text-slate-100
  placeholder:text-slate-500 outline-none focus:border-blue-500 focus:ring-3 focus:ring-blue-500/20 transition">
```

## 8. Astro específico

- Extrae a `src/components/*.astro` todo bloque que se repita o pase de ~60 líneas. Props tipadas con `interface Props`.
- Usa `class:list={[base, cond && 'x']}` para variantes.
- HTML generado con JS (`innerHTML`) no ve clases nuevas si no aparecen en el código fuente: declara sus clases en `@layer components` de `global.css` (patrón ya usado) o usa `@source` / clases completas literales.
- Fuentes: `@fontsource-variable/inter` importado en Layout, no `<link>` a terceros si se puede evitar.

## 9. Checklist final

- [ ] ¿Hay una sola acción primaria clara?
- [ ] ¿Espaciado consistente con la escala?
- [ ] ¿Colores sólo de la paleta / tokens?
- [ ] ¿Se ve bien a 375px, 768px y 1440px?
- [ ] ¿Estados hover, focus-visible, active, disabled definidos?
- [ ] ¿Coherente con el resto de la app?

Para estados vacíos, carga, errores, formularios y flujos, aplica también la skill `ux-patterns`. Para auditar algo existente, usa `ui-review`.
