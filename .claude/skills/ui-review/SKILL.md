---
name: ui-review
description: Audita una página o componente del frontend (Astro + Tailwind) en diseño visual, UX, accesibilidad, responsive y rendimiento percibido, y devuelve una lista priorizada de mejoras con el código para aplicarlas. Úsala cuando el usuario pida revisar, auditar, pulir o "dar una vuelta" a la interfaz, o antes de dar por terminado un cambio grande de UI.
---

# UI Review — auditoría de interfaz

Aplica los criterios de las skills `ui-design` y `ux-patterns`. Léelas si no están ya cargadas.

## Proceso

1. **Alcance**: identifica el archivo/página objetivo (por defecto `app/frontend/src/pages/index.astro`) y sus componentes, `global.css` y `Layout.astro`.
2. **Lee el código completo**, incluido el `<script>` (los estados de carga/error/vacío suelen estar en el JS).
3. **Si es posible, mírala renderizada**: `cd app/frontend && npm run dev` y abre `http://localhost:4321` con el navegador disponible; revisa a 375px, 768px y 1440px. Si no hay navegador, indícalo y audita sólo el código.
4. **Evalúa** cada categoría de abajo.
5. **Informa** con el formato de salida. No apliques cambios salvo que el usuario lo pida; si lo pide, empieza por los de severidad alta.

## Categorías y qué buscar

**Jerarquía y layout**
- Varias acciones primarias compitiendo (muchos botones de color al mismo nivel).
- Espaciados fuera de escala, alineaciones rotas, densidad excesiva.
- Archivos monolíticos (> ~300 líneas de markup) → proponer componentes.

**Consistencia visual**
- Colores, radios, sombras o tamaños de texto que se salen del patrón dominante.
- Valores arbitrarios repetidos (`text-[10px]`, `#22c55e`) que deberían ser tokens en `@theme`.
- Mezcla de sets de iconos o grosores.

**Estados y feedback**
- Falta alguno de: cargando, vacío, sin resultados, error, éxito.
- Botones async sin loading / sin protección de doble click.
- Botones `disabled` sin explicación.
- Acciones masivas sin confirmación ni resumen.

**Accesibilidad**
- `div`/`span` con `onclick`; botones sólo-icono sin `aria-label`.
- Sin `focus-visible`; `outline-none` sin alternativa.
- Contraste < 4.5:1 (ojo con `slate-600`/`slate-500` sobre fondos oscuros, y `opacity-30` en disabled).
- Inputs sin label; errores sin `aria-describedby`.
- Información transmitida sólo por color.

**Responsive**
- Header/toolbars que desbordan en móvil (muchos botones en fila → menú o barra inferior).
- Tablas sin `overflow-x-auto` o sin vista alternativa en cards.
- Elementos `hidden sm:flex` que dejan funcionalidad inaccesible en móvil.

**Seguridad / robustez de UI**
- `innerHTML` con datos externos sin escapar.
- Enlaces externos sin `rel="noopener noreferrer"` o sin validar protocolo.

**Rendimiento percibido**
- Spinners donde iría un skeleton; layout shift al cargar datos.
- Re-render completo de listas grandes en cada tecla de búsqueda (falta debounce).
- Animaciones de propiedades caras (`width`, `top`) en vez de `transform`/`opacity`.

## Formato de salida

```
## Resumen
2-3 frases: impresión general y las 3 mejoras de mayor impacto.

## Hallazgos
### 🔴 Alta — <título>
[archivo.astro:123](ruta#L123) — qué pasa y por qué importa al usuario.
**Arreglo:** snippet concreto (antes → después).

### 🟡 Media — ...
### 🟢 Pulido — ...

## Lo que ya está bien
Bullets breves (para no romperlo al refactorizar).
```

Severidad:
- 🔴 Alta: bloquea o confunde al usuario, problema de accesibilidad grave, riesgo de XSS o de acción masiva accidental.
- 🟡 Media: inconsistencia visible, falta de un estado, mala experiencia móvil.
- 🟢 Pulido: detalles estéticos, microcopy, tokens.

Máximo ~15 hallazgos; agrupa los repetidos ("12 botones sin `focus-visible`") en vez de listarlos uno a uno.
