---
name: maquetas
description: Guía de patrones de diseño para las maquetas de web que se enseñan a los negocios (app/backend/services/maqueta.py, carpeta maquetas/). Estructura de secciones, sistema visual por sector (reformas, taller, fisioterapia y genérico), uso de los datos reales del lead, textos con IA, imágenes, honestidad, rendimiento y checklist. Úsala siempre que vayas a crear, rediseñar o añadir un sector a las maquetas, cambiar su plantilla o su prompt, o cuando el usuario diga que las maquetas "no convencen", "se ven genéricas" o quiera "maquetas mejores".
---

# Maquetas — una web de ejemplo que vende en 5 segundos

La maqueta no es una web: es **una herramienta de venta**. Se enseña durante una llamada o por
WhatsApp a un dueño de taller, de empresa de reformas o de clínica que no tiene web. Funciona si
al abrirla en el móvil piensa **"esto es mi negocio"** y pregunta **"¿y cuánto cuesta?"**.

Todas las decisiones de esta guía salen de tres principios:

1. **Personal antes que bonito.** Su nombre, su ciudad y su teléfono valen más que cualquier efecto.
2. **Móvil primero.** El 90 % la verá en un móvil, abierta desde WhatsApp.
3. **Honesta.** Nada inventado que pueda comprobarse. Lo que es de ejemplo se dice.

---

## 1. La prueba de los 5 segundos

Abre la maqueta en un móvil (375 px) sin hacer scroll. En la primera pantalla tiene que verse:

- [ ] El **nombre del negocio**, grande, tal y como lo conoce el cliente (`nombre_comercial`).
- [ ] **Qué hace y dónde**: "Taller mecánico en Cartagena".
- [ ] Una **acción** clara: *Llamar* y, si el teléfono es móvil, *WhatsApp*.
- [ ] Si existe, la **prueba social real**: "★ 4,7 · 38 reseñas en Google".

Si falta algo de esto, el resto da igual.

---

## 2. Anatomía: el esqueleto común

Todas las maquetas comparten el mismo orden. Lo que cambia por sector son los textos, el color y
alguna sección concreta (ver sección 4).

| # | Sección | Contenido | Reglas |
|---|---------|-----------|--------|
| 0 | **Franja de aviso** | "Propuesta de diseño para {negocio}. No es su web oficial." | Siempre. Fija arriba, discreta, nunca se quita. |
| 1 | **Cabecera** | Nombre + botón *Llamar* | Fija (`sticky`). En móvil, sin menú: solo nombre y teléfono. |
| 2 | **Hero** | Eslogan (≤ 8 palabras) + "{Sector} en {ciudad}" + 2 botones | Ocupa como mucho el 80 % del alto en móvil. Botón principal = acción del sector (ver 4). |
| 3 | **Prueba social** | Valoración y nº de reseñas de Google | **Solo si es real**: valoración ≥ 4,0 y ≥ 5 reseñas. Si no, la sección no existe. |
| 4 | **Servicios** | 4-6 tarjetas: título + 1 frase | Icono SVG por servicio. Lo más pedido primero. |
| 5 | **Específica del sector** | Antes/después, horario, primera visita… | Ver tabla de sectores. |
| 6 | **Por qué elegirnos** | 3 ventajas | Promesas de trato, nunca cifras inventadas. |
| 7 | **Galería** | 3-6 huecos para fotos | Marcados "Aquí irán tus fotos". Ver sección 6. |
| 8 | **Contacto** | Teléfono, WhatsApp, dirección, mapa | Botones grandes. El formulario es opcional y de demostración. |
| 9 | **Pie** | Nombre, ciudad, enlaces a sus redes reales | Si tiene Instagram/Facebook en el CSV, enlázalos aquí. |
| — | **Barra fija inferior (móvil)** | *Llamar* · *WhatsApp* | Siempre visible en móvil. Es lo que más convierte en webs locales. |

Menos es más: **una maqueta corta y personal convence más que una larga y genérica**. Si una
sección no tiene nada propio del negocio ni del sector, quítala.

---

## 3. Datos del lead: qué usar y cómo

La maqueta solo puede usar lo que hay en `Leads Google Maps.csv`. Cada dato real que aparece la
hace más creíble.

| Columna del CSV | Dónde va | Regla |
|-----------------|----------|-------|
| `Nombre del negocio` | Cabecera, hero, título, pie | Pasar por `nombre_comercial()`: quita el SEO ("TALLER PEPE - Mecánica en Murcia" → "Taller Pepe"). |
| `Categoría` + nombre | Elegir sector y tema | `sector_de()`. Sin sector conocido → tema **genérico** con la categoría de Google. |
| `Ubicación` | Hero ("en {ciudad}"), contacto, mapa | `ciudad_de()` para la ciudad, dirección completa solo en contacto. |
| `Teléfono` | Botón *Llamar*, cabecera, barra fija | `tel:` solo con dígitos y `+`. |
| `Tipo teléfono` = Móvil | Botón *WhatsApp* | `https://wa.me/34{número}`. Si es fijo, no hay botón de WhatsApp. |
| `Valoración`, `Reseñas` | Prueba social | Solo con ≥ 4,0 y ≥ 5 reseñas. Formato español: "4,7". |
| `Horario` | Sección horario | Hoy solo indica si tiene horario en Google: muestra "Consulta nuestro horario" o un horario **marcado como ejemplo**. |
| `Instagram`, `Facebook`… | Pie y contacto | Solo URLs `http(s)` válidas (`safeUrl`). |
| `Email` | Contacto | Si existe. Nunca inventes uno. |

Seguridad de datos (ya resuelto en `maqueta.py`, mantenlo así):

- **Todo** dato del CSV pasa por `limpiar_dato()` y se escapa con `html.escape()` al insertarlo.
- Los datos que se mandan a la IA van **marcados como datos, no instrucciones** (el nombre de un
  negocio podría contener texto malicioso).

---

## 4. Patrones por sector

Cada sector define **tema visual, acción principal, servicios por defecto y una sección propia**.
Así es como debe quedar la configuración en código (un diccionario por sector, una sola plantilla).

| | Reformas | Taller mecánico | Fisioterapia | Genérico |
|---|---|---|---|---|
| **Sensación** | Solidez, obra bien hecha | Confianza, rapidez, honradez | Calma, cuidado, profesionalidad | Cercanía |
| **Acento** | Terracota / ámbar `#c2410c` | Azul acero `#1d4ed8` + rojo puntual | Verde salvia `#0f766e` | Azul pizarra `#334155` |
| **Fondo** | Piedra cálido `#fafaf9` | Gris frío `#f8fafc` | Blanco roto `#f7faf9` | `#f8fafc` |
| **Acción principal** | **Pide presupuesto gratis** | **Pide cita** | **Reserva tu cita** | **Llámanos** |
| **Servicios típicos** | Reformas integrales, cocinas, baños, pintura, fontanería y electricidad, locales | Revisión y mantenimiento, pre-ITV, frenos, neumáticos, diagnosis, aire acondicionado | Fisioterapia deportiva, dolor de espalda, rehabilitación de lesiones, punción seca, masaje terapéutico, suelo pélvico | Los 3-6 de la categoría (IA) |
| **Sección propia** | **Antes / después** (huecos dobles) y "Zona de trabajo: {ciudad} y alrededores" | **Horario bien visible** y "Trae tu coche: pide cita por WhatsApp" | **Tu primera visita** en 3 pasos (valoración, tratamiento, seguimiento) | — |
| **Iconos** | Casa, rodillo, llave inglesa | Coche, llave, neumático | Manos, columna, calendario | Tienda, teléfono |
| **Evitar** | Fotos de lujo irreales | Tono "barato" o de chatarrería | Lenguaje médico que prometa curas | Textos que podrían ser de cualquiera |

**Para añadir un sector nuevo** basta con: claves en `_SECTORES` de `comun/dominio.py`, una
entrada en el diccionario de temas (colores, acción, servicios, sección propia) y sus textos de
respaldo. La plantilla no se toca.

---

## 5. Sistema visual

Mismas reglas para todos los sectores; solo cambian los tokens de color.

**Tokens** (variables CSS en `:root`, nada de colores sueltos en el HTML):

```css
:root {
  --acento: #c2410c;        /* botones, iconos, detalles */
  --acento-oscuro: #9a3412; /* hover y texto sobre fondo claro */
  --acento-suave: #fff7ed;  /* fondos de iconos y tarjetas destacadas */
  --tinta: #1c1917;         /* títulos */
  --texto: #44403c;         /* párrafos */
  --fondo: #fafaf9;
  --borde: #e7e5e4;
  --radio: 12px;
}
```

**Tipografía**: una sola familia del sistema (`system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`):
carga al instante y no depende de Google Fonts. Escala: 14 · 16 · 18 · 22 · 28 · `clamp(32px, 7vw, 52px)` (hero).
Títulos con peso 700-800 y `letter-spacing: -0.02em`; texto a 16-18 px con `line-height: 1.6`.

**Espaciado**: múltiplos de 4 (8, 12, 16, 24, 32, 48, 64, 96). Secciones con 64 px arriba y abajo
en móvil y 96 px en escritorio. Contenido a un máximo de 1100 px de ancho.

**Botones**: alto mínimo **48 px** (se tocan con el pulgar), texto de 16 px en negrita. Uno
principal relleno de `--acento` por pantalla; el secundario con borde. Estados `:hover`,
`:focus-visible` y `:active` siempre.

**Contraste**: texto normal ≥ 4,5:1 (WCAG AA). Comprueba sobre todo el blanco sobre el acento y el
texto del hero sobre el fondo.

**Detalles que hacen que se vea cara**: bordes de 1 px en vez de sombras fuertes, un solo radio para
todo, iconos SVG en línea del mismo grosor, y mucho aire alrededor de los títulos.

---

## 6. Imágenes

El riesgo número uno de una maqueta es parecer una plantilla. Por orden de preferencia:

1. **Huecos de foto honestos**: degradado con el color del sector + icono SVG + etiqueta
   "Aquí irá la foto de tu taller". Es lo más rápido y lo más sincero, y el dueño se imagina sus fotos.
2. **Ilustraciones SVG** propias del sector en el hero (formas simples con los colores del tema).
3. **Fotos del propio negocio en Google Maps**: solo con la API oficial de Places, mostrando la
   atribución que exige Google, y sabiendo que cuestan llamadas a la API.

**Nunca**: fotos de bancos de imágenes presentadas como trabajos suyos, ni fotos de otros negocios.

---

## 7. Textos con IA

La IA escribe eslogan, introducción, servicios y ventajas (`_textos_ia`). Reglas del prompt:

- Español de España, tú (no usted) salvo en fisioterapia, que admite un tono algo más formal.
- **Prohibido inventar** años de experiencia, número de clientes u obras, premios, certificados,
  garantías concretas o precios. Mantén esta línea en el prompt.
- Mencionar la ciudad en la introducción: es lo que la hace "suya".
- Longitudes cerradas: eslogan ≤ 8 palabras, intro 2 frases, servicio 1 frase (≤ 15 palabras).
- Respuesta en JSON con `response_format` y **validación**: si falta un campo o no hay suficientes
  servicios, se usan los textos de respaldo del sector. La maqueta sale siempre, con o sin IA.
- Cada sector tiene sus **textos de respaldo** escritos a mano y revisados: son la red de seguridad.

---

## 8. Técnica

- **Un solo archivo HTML** con el CSS dentro, sin dependencias externas salvo el iframe del mapa
  (`loading="lazy"`). Objetivo: **< 60 KB** y carga instantánea con 4G.
- `<meta name="robots" content="noindex, nofollow">` siempre: no debe aparecer en Google.
- JavaScript solo para la demo del formulario. La maqueta tiene que funcionar sin JS.
- HTML semántico (`header`, `main`, `section`, `footer`), `lang="es"`, `alt` en imágenes, un solo `h1`.
- Nombre de archivo `{slug-del-negocio}-{id}.html` en `maquetas/`.
- Tests en `app/backend/tests/test_maqueta.py` (plantilla) y `test_contacto_api.py` (API y
  publicación): con y sin IA, `noindex` y aviso, escapado, prueba social, WhatsApp y sectores.

### Cómo llega al cliente

`generar_maqueta()` guarda la maqueta en `maquetas/` y una copia en `landing/public/m/` con un
código HMAC en el nombre (`nombre_publico()`, clave en `.maquetas_secret`): estable para cada
negocio y no adivinable. Con `LANDING_URL` en el `.env`, el panel muestra el enlace y el botón
*Enviar por WhatsApp*. Esas copias están fuera de git: la landing se despliega subiendo `dist/`
(wrangler / Netlify), y `/m/` está en `Disallow` de `robots.txt`.

---

## 9. Cómo usarla en la venta

1. Genera la maqueta **antes** de llamar a un lead prioritario.
2. En la llamada: "Te he preparado cómo quedaría la web de {negocio}, ¿te la mando por WhatsApp?".
3. Mándala y pregunta qué le cambiaría: si propone cambios, ya se la está imaginando como suya.
4. Cierra con el precio de la landing (90 €, pago único) y la maqueta como punto de partida.

---

## 10. Checklist antes de dar una maqueta por buena

- [ ] Pasa la **prueba de los 5 segundos** en un móvil de 375 px.
- [ ] Nombre comercial limpio, ciudad correcta, teléfono que funciona al tocarlo.
- [ ] Botón de WhatsApp solo si el teléfono es móvil.
- [ ] Prueba social solo si es real (≥ 4,0 y ≥ 5 reseñas).
- [ ] Ningún dato inventado: años, clientes, premios, precios, reseñas.
- [ ] Franja de aviso visible y `noindex` puesto.
- [ ] Colores del tema del sector, contraste AA y botones de ≥ 48 px.
- [ ] Barra fija inferior con *Llamar* / *WhatsApp* en móvil.
- [ ] Huecos de foto etiquetados como de ejemplo.
- [ ] Pesa < 60 KB y no carga nada externo salvo el mapa.
- [ ] Se ve bien a 375, 768 y 1280 px sin scroll horizontal.

Para el diseño general del panel usa `ui-design`; para revisar una maqueta ya hecha, `ui-review`.
