# Plan para mejorar la captación de leads

Este documento junta dos cosas: el análisis del buscador actual (`app/scraper-python/script.py`)
y las fuentes alternativas de [`CrappingDatos.md`](CrappingDatos.md). Para cada idea dice si la
haría, cuándo y por qué, con un orden pensado para vender antes de Navidad.

**Resumen:** antes de buscar fuentes nuevas, conviene arreglar la que ya tienes. Google Places
rinde poco por cómo se está usando, no porque esté agotado. Después, lo que más encaja con lo que
vendes son **Páginas Amarillas como segunda fuente** y **Milanuncios a mano** para oficios.
**BORME** queda para enero. **Facebook, los agregadores y Supabase**, por ahora no.

---

## 1. Dónde estamos

| Dato | Valor |
| ---- | ----- |
| Búsquedas hechas | 9 (por ejemplo, "reformas en Bilbao", "taller mecánico en Sevilla") |
| Leads útiles de tus sectores | 11 (5 talleres, 3 reformas, 3 fisios) |
| **Rendimiento** | **~1,2 leads por búsqueda** |
| Leads totales en el CSV | 81 (unos 70 son de búsquedas antiguas de otros sectores) |
| Con email / con Instagram | 8 / 11 |
| Móvil / fijo | 38 / 40 |

### Por qué rinde tan poco

1. **Solo se revisan los 20 primeros resultados.** Google Places da hasta 60 por búsqueda en
   3 páginas, pero el script no pide las páginas 2 y 3. Además, esos 20 primeros son los negocios
   más conocidos, que son justo los que ya tienen web.
2. **Busca en ciudades grandes** (Madrid, Barcelona, Sevilla…), donde casi todo negocio bien
   posicionado ya tiene web. Además, están lejos de ti y no puedes ir a verlos.
3. **Pide los detalles negocio a negocio:** 1 búsqueda + 20 peticiones de detalles. Es lento y,
   con los precios de Google desde marzo de 2025, probablemente se sale del cupo gratis (más abajo).

---

## 2. Qué opino de cada fuente de `CrappingDatos.md`

| Fuente | Encaje con lo que vendes | Datos de contacto | Dificultad técnica | Riesgo legal / ToS | Veredicto |
| ------ | ------------------------ | ----------------- | ------------------ | ------------------ | --------- |
| Google Places (mejorado) | Alto | Teléfono, a veces web | Baja (ya existe) | Medio (ver §6) | ✅ **Ya, prioridad 1** |
| Páginas Amarillas | Alto (oficios, talleres) | Teléfono, a veces web | Baja (ya usas scrape.do con ella) | Medio | ✅ **Diciembre** |
| Milanuncios / Wallapop | Muy alto (reformas, oficios) | Teléfono a veces oculto | Alta para automatizar | Alto (son personas físicas) | ✅ **Diciembre, a mano** |
| BORME (empresas nuevas) | Medio-alto (más presupuesto) | **Ninguno** | Media | Bajo para la fuente, medio para el contacto | ⏳ **Enero** |
| Facebook | Ya cubierto | — | Muy alta | Alto (Meta demanda a los scrapers) | ❌ No |
| Agregadores (Just Eat, Glovo, Playtomic…) | Bajo para 90–300 € | Casi nunca | Alta (antibots) | Alto | ❌ No |
| Supabase / PostgreSQL | — | — | Días de migración | — | ❌ Ahora no |

### Google Maps "saturado de agencias"

Es verdad a medias. Lo que está saturado es el email masivo desde Google Maps a ciudades grandes.
Un negocio de Molina de Segura al que llamas o visitas con su maqueta ya hecha no recibe eso cada
semana. **Tu ventaja no es la fuente, es la maqueta personalizada y la cercanía.** Por eso Google
Places sigue siendo la fuente principal, bien usado.

### BORME: buena señal, pero llega sin teléfono

- **A favor:** son empresas recién constituidas, con presupuesto inicial y sin proveedor digital.
  Los datos son públicos y el BOE tiene **datos abiertos** (el sumario diario del BORME en XML), así
  que no hace falta scrapear HTML.
- **En contra:**
  - Solo trae **nombre de la sociedad, domicilio, objeto social y administradores**: ni teléfono
    ni email. Habría que cruzar cada empresa con Google Places, y una empresa recién creada a
    menudo aún no tiene ficha.
  - Solo salen **sociedades** (SL, SA). Los **autónomos**, que son la mayoría de tus clientes de
    90 €, no aparecen nunca.
  - Muchas constituciones son sociedades patrimoniales, holdings o empresas sin local: hay que
    filtrar mucho por el objeto social.
- **Cuándo:** en enero, como fuente de leads para los paquetes **Profesional, Completa y apps**,
  no para el Esencial. Filtrando por provincias de Murcia y Alicante y por palabras del objeto
  social (hostelería, reformas, estética, clínica, taller…).

### Directorios sectoriales: sí a Páginas Amarillas, no a los agregadores

- **Páginas Amarillas** ya la usas, pero solo para encontrar el email de un lead que ya tienes.
  Usarla también como **fuente** (listado por categoría y municipio) es poco trabajo porque
  `enrich_emails.py` ya habla con ella a través de scrape.do. Tiene muchos oficios (fontaneros,
  electricistas, cerrajeros) que no se cuidan en Google Maps.
- **Los agregadores (Just Eat, Glovo, Playtomic) no encajan.** El argumento "una plataforma propia
  sin comisiones" es un sistema de pedidos o reservas, que es un proyecto de app (2.000 € o más),
  no una web de 90–300 €. Además, esos negocios no van a dejar la plataforma, que es la que les trae
  clientes, y estas webs tienen antibots fuertes y términos de uso que prohíben el scraping.

### Milanuncios y Wallapop: el mejor encaje, pero a mano

- **A favor:** un autónomo que paga por destacar su anuncio de reformas o fontanería ya invierte
  en captar clientes y no tiene web. Es exactamente tu cliente de Esencial o Profesional.
- **En contra de automatizarlo:**
  - Milanuncios tiene un antibot fuerte, y el teléfono a menudo solo se ve tras iniciar sesión.
  - Sus términos de uso prohíben el scraping.
  - Casi todos son **personas físicas**: su teléfono es un dato personal (RGPD).
- **Propuesta:** **20 minutos al día de captación a mano.** Navegas las categorías de Servicios de
  tu zona y añades al CSV los que encajan. Para eso falta una forma rápida de **añadir un lead a
  mano** (un formulario en el panel o un `anadir_lead.py`). Pocos leads, pero muy buenos.

### Facebook: ya lo tienes cubierto

`necesita_web()` en [`comun/oportunidad.py`](../app/comun/comun/oportunidad.py) ya trata como "sin
web" a los negocios cuya web en Google es un Facebook, un Instagram o un directorio, y
`enrich_emails.py` ya guarda sus redes. Lo que sí vale la pena es **subirles la puntuación**:
alguien que ha puesto su Facebook como web ya sabe que necesita estar en internet. Scrapear
Facebook directamente no merece la pena: hace falta iniciar sesión, Meta lo prohíbe y demanda a
quien lo hace.

### Supabase / PostgreSQL: ahora no

- Con 81 leads y una sola persona, el CSV con bloqueo y escritura atómica funciona bien, y ya
  descarta duplicados al añadir.
- Migrar supondría días de trabajo (repositorio, scripts, panel, tests) sin ninguna venta a cambio
  antes de Navidad.
- **Cuándo tendría sentido:** con varios miles de leads, más de una persona trabajando o si se da el
  paso al SaaS para agencias. Incluso entonces, el paso intermedio razonable es **SQLite** (un
  fichero, sin servidor).
- Lo que sí hace falta ya, con o sin base de datos: **descartar duplicados entre fuentes** (§3.5).

---

## 3. El plan que yo seguiría

### Fase 1 · Esta semana (antes de finales de noviembre)

#### 3.1 Pasar a Places API (New) con paginación

- Usar **Text Search (New)** con *field mask*: la propia búsqueda devuelve web, teléfono,
  valoración, número de reseñas, estado y horario. **Se eliminan las 20 peticiones de detalles.**
- Pedir las **3 páginas** (`pageToken`): hasta 60 negocios por búsqueda en lugar de 20.
- Filtrar a los que no tienen web **sin gastar ninguna petición más**.
- **Coste:** desde marzo de 2025, Google ya no da 200 $ de crédito al mes, sino un cupo gratis por
  tipo de petición. Si los cupos son los que creo (unas **1.000 peticiones gratis al mes** para las
  que piden teléfono o web), el sistema actual (unas 21 peticiones por búsqueda) se pasa del cupo
  en unas 50 búsquedas. El nuevo (3 por búsqueda) cabe holgado: 10 búsquedas al día durante un mes
  son unas 900. **Compruébalo en Google Cloud Console → Facturación → Informes** antes de seguir
  buscando.
- **Esfuerzo:** medio. Es un solo archivo (`script.py`) y sus tests (`test_places.py`).

#### 3.2 Buscar cerca de ti

Cambiar las 30 ciudades grandes por **municipios y barrios a los que puedas ir en coche**. Por
ejemplo, para Murcia:

- **Región:** Molina de Segura, Alcantarilla, Lorca, Cieza, Yecla, Jumilla, Torre Pacheco,
  San Javier, San Pedro del Pinatar, Águilas, Mazarrón, Totana, Caravaca, Las Torres de Cotillas,
  Alhama, Archena, Mula, Santomera, Los Alcázares, La Unión.
- **Barrios y pedanías de Murcia y Cartagena:** El Palmar, Espinardo, Puente Tocinos, Beniaján,
  El Ranero, Santiago el Mayor, Los Dolores, San Antonio Abad, Barrio Peral…

Ventajas:

- Más negocios sin web.
- Puedes **visitarlos con la maqueta en el móvil**, que cierra mucho más que un WhatsApp.
- Encaja con la landing, que ya dice "Murcia".

#### 3.3 Más sectores de oficios

Añadir a `TIPOS_NEGOCIO`: **electricista, fontanero, cerrajero, carpintería, pintor, cristalería,
peluquería, centro de estética, autoescuela, academia**. Son de los que más a menudo no tienen web
o solo tienen un Facebook. Las maquetas ya tienen un tema genérico para los sectores sin tema
propio.

#### 3.4 Medir qué rinde

Guardar en `search_state.json`, por cada búsqueda: resultados, sin web, con móvil y nuevos de
verdad. Con 2–3 semanas de datos se ajustan los `PESOS` de los sectores con números, no a ojo.
Más adelante, el propio script puede ajustarlos solo.

### Fase 2 · Diciembre (si hay tiempo entre ventas)

#### 3.5 Columna `Fuente` y duplicados entre fuentes

- **Nueva columna `Fuente`** en el CSV (`google`, `paginas_amarillas`, `milanuncios`, `manual`).
  Así sabrás de qué fuente salen los Interesados de verdad.
- **Duplicados por teléfono normalizado** (solo dígitos y sin prefijo `+34`), además de por nombre.
  Es imprescindible en cuanto haya dos fuentes.

#### 3.6 Páginas Amarillas como segunda fuente

- Un script `buscar_paginas_amarillas.py`, con el mismo esquema que `script.py`: sector +
  municipio, se queda con los que no tienen web y los añade con `Fuente = paginas_amarillas`.
- Reutiliza el cliente de scrape.do de `enrich_emails.py` y lo que haya en común se mueve al
  paquete `comun`.
- Vigila los créditos de scrape.do: el plan gratis da unos 1.000 al mes.

#### 3.7 Alta manual de leads (para Milanuncios y para lo que veas por la calle)

- Un formulario "Añadir lead" en el panel: nombre, teléfono, sector, municipio, fuente y una nota.
- Con eso, los 20 minutos diarios en Milanuncios o un negocio que ves al pasar acaban en el mismo
  flujo de guion, maqueta y llamada.

### Fase 3 · Enero

#### 3.8 BORME para clientes con más presupuesto

- Leer cada día el sumario del BORME desde los datos abiertos del BOE: actos de **constitución**
  en las provincias de Murcia y Alicante.
- Filtrar por palabras del objeto social y cruzar con Google Places para conseguir el teléfono.
- Marcar como `Fuente = borme` y ofrecerles **Profesional, Completa o app**, no el Esencial.

#### 3.9 Revisar la base de datos

Si para entonces hay varios miles de leads o se retoma el SaaS de agencias, valorar pasar a SQLite
(o a Postgres, si va a haber varios usuarios).

---

## 4. Qué esperar

Son **estimaciones para comprobar con la medición del punto 3.4**, no promesas:

| | Ahora | Tras la fase 1 |
| - | ----- | -------------- |
| Negocios revisados por búsqueda | 20 | hasta 60 |
| Leads sin web por búsqueda | ~1,2 | 4–8 (municipios pequeños y oficios) |
| Peticiones a Google por búsqueda | 21 | 1–3 |
| Leads a los que puedes ir en persona | casi ninguno | la mayoría |

Para el objetivo de Navidad (3–4 ventas) no hacen falta miles de leads, sino **unos 100 buenos
y cercanos**, y llamarlos o visitarlos. Con la fase 1 eso son unas 2–3 semanas de búsquedas.

---

## 5. Lo que no haría

- **Scrapear Facebook, Wallapop o Milanuncios de forma automática**: antibots, inicio de sesión,
  términos de uso y riesgo legal, para pocos leads más que a mano.
- **Ir a por los agregadores de comida o reservas**: no encajan con webs de 90–300 €.
- **Migrar a Supabase ahora**: días de trabajo sin ninguna venta a cambio antes de Navidad.
- **Subir mucho el límite diario de búsquedas**: más volumen sin llamar no es más ventas.

---

## 6. Riesgos legales y de términos de uso (consúltalo)

No es asesoramiento legal: son los puntos que conviene revisar con una gestoría o un abogado.

- **Términos de Google Maps Platform:** limitan guardar el contenido de Places (nombre, teléfono…)
  de forma indefinida fuera de su servicio. Revender esos datos en las **listas para agencias** es
  justo lo que más choca con esos términos. Una razón más para centrarte en vender webs.
- **RGPD:** el teléfono de un autónomo es un dato personal aunque esté publicado. Si alguien pide
  que lo borres, bórralo (`bajas.txt` ya lo cubre para los envíos).
- **LSSI (email y WhatsApp comerciales sin consentimiento previo):** en España, los mensajes
  comerciales electrónicos no solicitados están restringidos, y la AEPD sanciona también
  envíos a empresas. **Llamar o visitar en persona es el canal más seguro**, y además es el que
  mejor cierra.
- **Scraping de webs de terceros (Páginas Amarillas, Milanuncios):** sus términos suelen
  prohibirlo. Usarlo con poco volumen y para contacto uno a uno es muy distinto de volcar su base
  de datos.
