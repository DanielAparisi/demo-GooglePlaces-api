---
name: ux-patterns
description: Patrones de experiencia de usuario para interfaces web - estados (vacío, carga, error, éxito), feedback, formularios, tablas de datos, modales, acciones masivas, navegación por teclado y accesibilidad. Úsala al diseñar o implementar cualquier flujo interactivo del frontend (búsquedas, listados de leads, envíos de email/WhatsApp, formularios, diálogos), o cuando el usuario diga que algo es "confuso", "poco intuitivo" o pida mejorar la UX.
---

# UX Patterns — que la interfaz se entienda sola

Principio: el usuario siempre debe saber **dónde está, qué está pasando y qué puede hacer después**.

## 1. Los 5 estados de toda vista con datos

Implementa SIEMPRE los cinco, no sólo el "feliz":

| Estado | Qué mostrar |
|---|---|
| **Cargando** | Skeleton con la forma real del contenido (filas de tabla grises `animate-pulse`). Spinner sólo para acciones puntuales < 2s. |
| **Vacío (primera vez)** | Icono suave + título + una frase + CTA primaria ("Haz tu primera búsqueda"). |
| **Vacío (sin resultados)** | "Ningún lead coincide con «{query}»" + botón "Limpiar filtros". |
| **Error** | Qué falló en lenguaje humano + cómo arreglarlo + botón "Reintentar". Nunca un stack trace ni `[object Object]`. |
| **Con datos** | El contenido. Si es parcial (paginación, límite), dilo: "Mostrando 50 de 312". |

## 2. Feedback de acciones

- **< 100 ms**: respuesta visual inmediata (estado pressed, fila marcada).
- **Acciones async**: el botón pasa a loading (spinner + texto "Enviando…"), queda `disabled` y `aria-busy="true"`. Evita dobles envíos.
- **Resultado**: toast breve (3–5 s) para éxito; los errores se quedan hasta que el usuario los cierre.
- **Optimistic UI** cuando sea seguro (marcar, seleccionar); revierte con aviso si falla.
- **Progreso en lotes** (envío masivo): "Enviando 12/40…" con barra, y resumen final "38 enviados · 2 fallidos (ver)".
- Toasts con `role="status"` (éxito) o `role="alert"` (error) para lectores de pantalla.

## 3. Acciones destructivas o irreversibles

- Enviar emails/WhatsApp masivos, borrar, etc. → **confirmación con resumen concreto**: "Vas a enviar un email a **24 leads**. ¿Continuar?"
- El botón de confirmar repite el verbo ("Enviar 24 emails"), nunca "OK" / "Sí".
- Si es posible, ofrece **deshacer** en el toast en vez de un modal.
- Color rojo sólo para destruir datos; enviar no es destructivo pero sí irreversible → confirmación neutra.

## 4. Tablas y listados de datos

- Cabecera sticky; columnas numéricas alineadas a la derecha con `tabular-nums`.
- Fila entera clicable/seleccionable con checkbox visible; `Shift+click` para rango.
- **Barra de acciones masivas** contextual: aparece al seleccionar ("3 seleccionados · Email · WhatsApp · Limpiar"). Los botones de acción no deberían estar deshabilitados sin explicación: usa `title`/tooltip "Selecciona al menos un lead".
- Búsqueda con debounce (~200 ms), resalta coincidencias, y conserva filtros en la URL (`?q=&city=`) para poder compartir/recargar.
- Texto largo truncado con `truncate` + `title` con el valor completo.
- Datos ausentes: "—" en `text-slate-600`, no celdas vacías ni "null".
- Más de ~100 filas: paginación o virtualización.

## 5. Formularios

- Label siempre visible (el placeholder no es un label). `<label for>` enlazado.
- Validación al salir del campo (`blur`) y al enviar, no en cada tecla. Mensaje de error bajo el campo, en rojo, con `aria-describedby` y `aria-invalid="true"`.
- Mensajes que dicen cómo arreglarlo: "Introduce un email válido, p. ej. nombre@empresa.com".
- Tipos correctos: `type="email"`, `type="tel"`, `inputmode="numeric"`, `autocomplete`.
- Enter envía; el foco va al primer campo con error tras un envío fallido.
- Valores por defecto sensatos; agrupa campos relacionados; una columna en móvil.

## 6. Modales y paneles

- Usa `<dialog>` nativo (`showModal()`): da foco atrapado, `Esc` para cerrar y backdrop (`::backdrop`).
- Al abrir, foco al primer elemento útil; al cerrar, devuelve el foco al botón que lo abrió.
- Para detalles de un ítem en una lista, mejor **panel lateral (drawer)** que modal: mantiene el contexto.
- No apiles modales.

## 7. Teclado y accesibilidad (no negociable)

- Todo accionable es `<button>` o `<a href>`, nunca `<div onclick>`.
- `focus-visible:` con anillo claro en todos los interactivos.
- Atajos útiles: `/` enfoca búsqueda, `Esc` limpia/cierra, `Ctrl/⌘+A` en tabla selecciona todo (sólo si la tabla tiene foco).
- Botones con sólo icono → `aria-label`.
- No comuniques sólo con color (añade icono o texto: "✓ Con teléfono").
- Área táctil mínima 40×40 px en móvil.
- `lang="es"` en `<html>` (ya está) y textos en un mismo idioma.

## 8. Microcopy

- Verbos concretos en botones: "Buscar leads", "Enviar email", no "Procesar" / "Submit".
- Tono cercano y breve; tutea de forma consistente.
- Números con formato local: `new Intl.NumberFormat('es-ES').format(n)`; fechas relativas ("hace 3 min") con tooltip de fecha exacta.
- Pluraliza bien: "1 lead" / "2 leads" (`Intl.PluralRules`).

## 9. Seguridad en la UI

- Contenido que viene del scraper/API se inserta con `textContent` o escapado; nunca `innerHTML` con datos sin sanear (XSS). Si se construye HTML, escapa cada valor.
- URLs externas (webs, redes sociales): valida protocolo `http(s):` y añade `rel="noopener noreferrer" target="_blank"`.

## 10. Checklist

- [ ] Los 5 estados implementados
- [ ] Cada acción async tiene loading, éxito y error
- [ ] Acciones masivas/irreversibles confirman con números concretos
- [ ] Navegable entero con teclado, foco visible
- [ ] Mensajes de error accionables
- [ ] Funciona en móvil

Para el aspecto visual, combínala con la skill `ui-design`.
