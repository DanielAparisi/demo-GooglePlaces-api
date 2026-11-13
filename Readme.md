# Lead Generator — Google Places

Herramienta para **encontrar negocios locales sin página web, decidir a cuáles merece la pena
contactar y convertirlos en clientes**. Sirve para dos negocios a la vez:

1. **Vender webs** (de 90 a 300 €, más mantenimiento opcional) a talleres, reformas, clínicas… que
   aún no tienen web, y **apps móviles** a medida (desde 2.000 €). Ver [Precios](#9-precios-webs-mantenimiento-y-apps).
2. **Vender listas de esos negocios** por suscripción mensual a agencias de marketing y diseño web.

Todo corre en tu ordenador: un panel web para trabajar los leads y unos scripts que buscan,
enriquecen y contactan. Aparte hay una **landing pública** para darte a conocer como agencia, con
los paquetes y precios publicados. Todos los encargos se cierran **con contrato firmado y se
cobran por Bizum**.

## Índice

1. [Cómo funciona](#1-cómo-funciona)
2. [Qué hay en cada carpeta](#2-qué-hay-en-cada-carpeta)
3. [Puesta en marcha](#3-puesta-en-marcha)
4. [Guía de uso: el día a día](#4-guía-de-uso-el-día-a-día)
5. [Listas para agencias](#5-listas-para-agencias)
6. [Landing pública](#6-landing-pública)
7. [Datos y ficheros](#7-datos-y-ficheros)
8. [Tests, seguridad y privacidad](#8-tests-seguridad-y-privacidad)
9. [Precios: webs, mantenimiento y apps](#9-precios-webs-mantenimiento-y-apps)
10. [Modelo de negocio](#10-modelo-de-negocio--venta-de-listas-a-agencias)

---

## 1. Cómo funciona

```text
            ┌──────────────┐   ┌────────────────────┐   ┌───────────────────────────┐
 Google ──▶ │  script.py   │──▶│ Leads Google Maps  │──▶│  enrich_emails.py         │
 Places     │ busca negocios│   │      .csv          │◀──│  añade email y redes      │
            │  sin web      │   │ (base de datos)    │   │  (scrape.do)              │
            └──────────────┘   └─────────┬──────────┘   └───────────────────────────┘
                                         │
                       ┌─────────────────┴──────────────────┐
                       ▼                                    ▼
          ┌──────────────────────────┐        ┌──────────────────────────────┐
          │ PANEL · Leads  (/)       │        │ PANEL · Listas  (/listas)    │
          │ puntuación de oportunidad│        │ pedido por plan → CSV para   │
          │ guion, maqueta, llamadas │        │ la agencia, sin repetir leads│
          │ envíos WhatsApp/email/IG │        │ suscripciones y muestras     │
          └────────────┬─────────────┘        └──────────────────────────────┘
                       │ resultado de las llamadas
                       ▼
          calibrar: el modelo aprende qué leads acaban interesados

 Landing pública (landing/) ── WhatsApp / email ──▶ tú ──▶ trabajas desde el panel
```

**La idea en una frase:** el CSV es la base de datos; los scripts la llenan, el panel la trabaja.

- **Buscar** (`script.py`): pregunta a Google Places por un sector en una ciudad
  ("taller mecánico en Murcia"), se queda solo con los negocios **sin web propia** y los añade al
  CSV sin duplicados.
- **Enriquecer** (`enrich_emails.py`): para cada lead busca su email y sus redes sociales.
- **Puntuar**: cada lead recibe una **puntuación de oportunidad de 0 a 100** (Alta ≥ 70,
  Media ≥ 45, Baja) que estima si comprará una web. Suma siete señales: presencia web, demanda
  (reseñas), reputación, ficha de Google, datos de contacto, sector y redes. Cada lead muestra el
  *porqué* de su nota. Los que ya tienen web propia o están cerrados quedan fuera.
- **Contactar** desde el panel: llamar con un guion generado por IA, enseñar una maqueta de su
  futura web y enviar mensajes por WhatsApp, email o Instagram.
- **Aprender**: al marcar el resultado de cada llamada, el modelo se puede **recalibrar** para
  dar más peso a las señales que de verdad predicen interés.
- **Vender listas**: con los mismos leads se crean listas para agencias (sección 5).

---

## 2. Qué hay en cada carpeta

| Carpeta | Qué es |
| ------- | ------ |
| `app/scraper-python/` | Scripts de línea de comandos: buscar, enriquecer, enviar emails e Instagram, calibrar y crear listas. |
| `app/comun/` | Paquete Python `comun`, compartido por el backend y los scripts (ver abajo). |
| `app/backend/` | API FastAPI que usa el panel (`localhost:8000`). |
| `app/frontend/` | Panel en Astro + React (`localhost:4321`). |
| `app/whatsApp_node/` | Envío de WhatsApp con whatsapp-web.js. Se lanza desde el panel. |
| `landing/` | Web pública de la agencia (Astro estático, `localhost:4400` en local). |
| `maquetas/` | Maquetas HTML generadas para enseñar a los negocios. |
| `listas/`, `entregas.json` | Listas entregadas a agencias y su registro (fuera de git). |
| `docs/` | Documentación ampliada: [precios de webs y apps](docs/precios-webs.md) y [el paquete `comun`](docs/paquete-comun.md). |

### Lógica compartida: el paquete `comun`

Las reglas que usan **a la vez el backend y los scripts** viven en un paquete de Python instalable,
[`app/comun/`](app/comun/):

| Módulo | Qué hace |
| ------ | -------- |
| `dominio.py` | Reglas de negocio: sector, ciudad, nombre comercial, tipo de teléfono |
| `oportunidad.py`, `calibracion.py` | Puntuación de oportunidad y su recalibración con tus llamadas |
| `listas.py`, `planes.json` | Listas para agencias y sus planes |
| `leads_csv.py`, `ficheros.py` | Lectura y escritura del CSV con bloqueo entre procesos y escritura atómica |
| `envios.py` | Logs de envíos y texto de baja |
| `ia.py` | Cliente de Groq |
| `entorno.py` | Carga el `.env` y `requerir()` para las claves obligatorias |
| `rutas.py` | Rutas de todos los ficheros de datos |

```text
backend  ──┐
           ├──▶  comun   (comun no importa nada del backend ni de los scripts)
scripts  ──┘
```

- Se instala en el venv del backend en **modo editable** (`-e ../comun` en
  [`app/backend/requirements.txt`](app/backend/requirements.txt)): editas un archivo de `comun` y
  el backend y los scripts usan la versión nueva sin reinstalar.
- Así se importa igual desde cualquier sitio (`from comun import listas`), sin tocar `sys.path`, y
  el editor lo encuentra para el autocompletado.
- Instálalo siempre en modo editable y lanzando `pip` desde `app/backend`: `rutas.py` calcula la
  raíz del proyecto desde su propia ubicación y `../comun` es relativo a esa carpeta.
- [`app/whatsApp_node/lib/dominio.js`](app/whatsApp_node/lib/dominio.js) es una copia en JavaScript
  de `dominio.py`: si cambias una regla de dominio, cámbiala en los dos.

Por qué se hizo así y qué problemas resolvía: [`docs/paquete-comun.md`](docs/paquete-comun.md).

Estructura del backend (`app/backend/`):

| Carpeta / archivo | Responsabilidad |
| ----------------- | --------------- |
| `main.py`         | `create_app()`: monta middlewares, routers y el manejo de errores |
| `core/`           | Configuración y rutas (`settings`), errores de negocio, seguridad (CORS/Origin/Host) y el puente al paquete compartido `comun` (`app/comun/`) |
| `repositories/`   | Acceso al CSV de leads (candado + escritura atómica) y a los logs JSON de envíos |
| `services/`       | Casos de uso: leads, envíos, guion, maqueta, IA, estado, modelo de oportunidad y listas para agencias |
| `routers/`, `schemas/` | Endpoints HTTP y modelos de entrada (Pydantic) |
| `tests/`          | Tests con datos sintéticos en un directorio temporal (nunca tocan el CSV real) |

---

## 3. Puesta en marcha

### Requisitos

- Python 3.10+ y Node.js 22.12+
- Cuentas y claves: Google Places API, scrape.do, Groq (IA) y Gmail con contraseña de aplicación.
  Instagram es opcional.

### Claves (`.env`)

Copia la plantilla y rellénala. Todos los scripts y el backend leen este único fichero:

```bash
cp .env.example .env
```

| Variable | Para qué | Dónde conseguirla |
| -------- | -------- | ----------------- |
| `GOOGLE_PLACES_API_KEY` | Buscar negocios (`script.py`) | Google Cloud Console → Credenciales |
| `SCRAPEDO_TOKEN` | Buscar emails y redes (`enrich_emails.py`) | scrape.do |
| `GROQ_API_KEY` | Guiones, maquetas y mensajes con IA | console.groq.com → API Keys |
| `GMAIL_USER`, `GMAIL_PASSWORD` | Enviar emails | Google → Seguridad → Contraseñas de aplicación |
| `IG_USER`, `IG_PASS` | Mensajes de Instagram (opcional) | Tu cuenta de Instagram |
| `LANDING_URL` | Enlace público de las maquetas (opcional) | Tu dominio, p. ej. `https://barriodigital.es` |

Si la IA falla o no hay clave de Groq, guiones, maquetas y mensajes salen igualmente con plantillas.

### Arrancar todo con un comando

```bash
./start.sh
```

La primera vez crea el entorno de Python e instala las dependencias de Node. Luego levanta:

| Servicio                  | URL                                       | Log                  |
| ------------------------- | ----------------------------------------- | -------------------- |
| Backend FastAPI           | [localhost:8000](http://localhost:8000)   | `.logs/backend.log`  |
| Panel (frontend Astro)    | [localhost:4321](http://localhost:4321)   | `.logs/frontend.log` |
| Landing pública (Astro)   | [localhost:4400](http://localhost:4400)   | `.logs/landing.log`  |

`Ctrl+C` lo detiene todo. WhatsApp **no** se arranca aquí porque envía mensajes reales: se lanza
desde el panel.

<details>
<summary>Arrancar cada servicio por separado</summary>

```bash
# Backend (requirements.txt instala también el paquete comun: lánzalo desde app/backend)
cd app/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Panel
cd app/frontend && npm install && npm run dev

# Landing
cd landing && npm install && npm run dev   # http://localhost:4400

# WhatsApp (solo instalar)
cd app/whatsApp_node && npm install
```

</details>

Los scripts de `app/scraper-python/` usan el mismo entorno de Python que el backend (ahí está
instalado `comun`):

```bash
cd app/scraper-python
source ../backend/.venv/bin/activate
```

---

## 4. Guía de uso: el día a día

### Paso 1 · Conseguir leads

```bash
cd app/scraper-python
python script.py          # una búsqueda nueva
python script.py --cola   # termina de revisar lo que quedó pendiente (no gasta búsqueda)
```

- Cada ejecución elige al azar un **sector** (reformas, taller mecánico, fisioterapia; talleres y
  fisios salen el doble porque dan más negocios sin web) y una de 30 **ciudades** grandes, sin
  repetir combinaciones ya hechas.
- Límite de **10 búsquedas al día** (`LIMITE_DIARIO` en `script.py`) para no salirte de la
  capa gratuita de Google.
- Si la API falla a mitad, lo encontrado se guarda y el resto queda en cola para `--cola`.
- Sectores y ciudades se cambian en `TIPOS_NEGOCIO`, `PESOS` y `CIUDADES` de `script.py`.

### Paso 2 · Enriquecer con email y redes

```bash
python enrich_emails.py                  # todos los leads sin enriquecer
python enrich_emails.py --solo-sectores  # solo talleres, fisios y reformas (ahorra créditos)
```

Guarda cada lead en cuanto lo procesa, así que puedes usar el panel mientras corre. Si se acaban
los créditos de scrape.do, se para sin marcar como hechos los que no ha podido buscar.

### Paso 3 · Trabajar los leads en el panel (`localhost:4321`)

**Arriba**: contadores (leads, con WhatsApp, por llamar, mensajes enviados, interesados) y el panel plegable
*Modelo de oportunidad* (paso 5).

**Pestañas** para filtrar:

| Pestaña | Qué muestra |
| ------- | ----------- |
| Todos | Todo el CSV, los más recientes primero |
| Prioritarios | Oportunidad **Alta** y aún sin llamar: **empieza por aquí** |
| WhatsApp | Leads con móvil |
| Por llamar | Sin llamar o que no contestaron |
| Con email | Leads con email |
| Interesados | Los que marcaste como interesados: tu cartera |

La caja de búsqueda (atajo `/`) filtra por nombre, categoría, dirección, teléfono o email.

**Ficha del lead** (clic en una fila):

- **Oportunidad**: nota, nivel y por qué (p. ej. "No tiene página web · Móvil: contactable por
  WhatsApp").
- **Contacto**: teléfono (clic para llamar), email, redes, dirección.
- **Preparar contacto**:
  - **Generar guion**: guion de llamada con IA adaptado al negocio y su sector.
  - **Generar maqueta**: crea una web de ejemplo para ese negocio, lista para enseñar. Usa sus
    datos reales (nombre, ciudad, teléfono, botón de WhatsApp si es móvil, su valoración de Google
    si es buena) y el tema de su sector: reformas, taller, fisioterapia o uno genérico para el resto.
    Lleva el aviso "no es su web oficial" y no aparece en Google. Si tienes `LANDING_URL`
    configurada, aparecen **Copiar enlace** y **Enviar por WhatsApp** para mandársela (ver más abajo).
- **Resultado del contacto**: marca **No contesta**, **Interesado** o **Descartado**. Queda
  guardado con fecha y alimenta la calibración del modelo.

**Envíos masivos**: marca leads con las casillas (o *Seleccionar no contactados*) y usa la barra
inferior para enviar por **WhatsApp**, **Email** o **Instagram**. Cada botón dice a cuántos
llegará y pide confirmación, porque los mensajes son reales.

- **WhatsApp**: la primera vez pulsa *Vincular WhatsApp* y escanea el QR con tu móvil
  (WhatsApp → Dispositivos vinculados). La sesión se recuerda.
- Los mensajes los redacta la IA para cada negocio.
- Nunca se escribe dos veces al mismo número, email o cuenta, ni a quien pidió la baja
  (`bajas.txt`, uno por línea).

Para probar sin enviar nada, todos los scripts de envío aceptan `--dry-run`:

```bash
python send_emails.py --dry-run
python send_instagram.py --dry-run
node app/whatsApp_node/send_whatsapp.js --dry-run
```

> ⚠ Lanzados a mano sin `--selected-only`, escriben a **todos** los pendientes del CSV.
> Desde el panel siempre van solo a los seleccionados.

### Mandar la maqueta al negocio

Cada maqueta se guarda en `maquetas/` (para verla tú) y una copia en `landing/public/m/` con un
código en el nombre que no se puede adivinar (`taller-pepe-3f9a1c0b7e2d.html`). Para que el enlace
funcione:

1. Pon tu dominio en `LANDING_URL` del `.env` y reinicia `./start.sh`.
2. Genera (o regenera) la maqueta: el enlace es siempre el mismo para ese negocio.
3. Despliega la landing **subiendo la carpeta** (las maquetas no van a git porque son datos de
   negocios): `cd landing && npm run build && npx wrangler pages deploy dist`
   (o arrastra `dist/` en Netlify).
4. En la ficha del lead: **Enviar por WhatsApp** abre WhatsApp con el mensaje y el enlace.

Las maquetas publicadas llevan `noindex` y `/m/` está bloqueado en `robots.txt`: no salen en Google.
Las reglas de diseño de las maquetas están en `.claude/skills/maquetas/SKILL.md`.

### Paso 4 · Cerrar la venta

Con los **Interesados** (la pestaña *Interesados* es tu lista de seguimiento):

1. **Enséñales su maqueta** (enlace por WhatsApp o en persona).
2. **Recomiéndales un paquete según su sector**, no la tabla entera (ver
   [Precios](#9-precios-webs-mantenimiento-y-apps)). Si piden algo más, ofrece extras o el paquete
   superior. Si lo que quieren es una app, presupuesto cerrado tras una llamada.
3. **Firmad el contrato** antes de empezar, siempre, también en el Esencial.
4. **Cobra por Bizum** según los plazos de [Pago y contrato](#pago-y-contrato): el Esencial al
   publicar, y el resto 50 % al firmar y 50 % al publicar.
5. **Ofrece el mantenimiento al cerrar** (15 €/mes o, mejor, 150 €/año).
6. **Entrega la web** cuando hayas recibido el pago final.

Los Interesados no entran nunca en las listas que vendes a agencias.

### Paso 5 · Mejorar la puntuación con tus llamadas

La puntuación arranca con pesos razonables, pero aprende de ti. Cuando tengas **al menos 20
llamadas marcadas como Interesado o Descartado (mínimo 3 de cada)**:

- En el panel: *Modelo de oportunidad* → **Recalibrar con mis llamadas**. Verás la tasa de
  interés por prioridad (si el modelo acierta, la Alta debe tener más interesados que la Media
  y la Baja) y cómo cambia el peso de cada señal. *Volver a los pesos de partida* lo deshace.
- O por consola:

```bash
python calibrar.py            # muestra cómo va y recalibra
python calibrar.py --simular  # enseña los pesos nuevos sin guardarlos
python calibrar.py --reset    # vuelve a los pesos de partida
```

Los pesos se guardan en `pesos_oportunidad.json` y el panel los usa al momento.

### Rutina recomendada

| Cuándo | Qué |
| ------ | --- |
| Cada día | `script.py` (hasta 10 búsquedas) → `enrich_emails.py --solo-sectores` |
| Cada día | Panel → *Prioritarios* → guion → llamar → marcar resultado |
| Al haber interés | Generar maqueta → enseñarla → proponer paquete → contrato → Bizum → entregar |
| Cada mes | Recordar el Bizum del mantenimiento a quien paga mensual |
| Cada semana | Envío de WhatsApp/email a los no contactados · recalibrar si hay datos nuevos |
| Cada mes | Preparar la lista de cada agencia suscrita (sección 5) |

---

## 5. Listas para agencias

Las listas se venden por suscripción mensual (ver sección 9). Se gestionan desde el panel, en
**Listas para agencias** (`localhost:4321/listas`), o por consola con `crear_lista.py`.

**Desde el panel:**

1. Elige plan (Básico, Estándar, Premium) o un pedido a medida, la agencia, los sectores, las
   ciudades (también barrios o provincias), los datos de contacto obligatorios (móvil, teléfono,
   email, redes) y la puntuación de oportunidad mínima.
2. **Previsualizar lista**: muestra cuántos leads salen, el reparto por prioridad y por
   sector × ciudad, por qué se quedan leads fuera y, si faltan, qué búsquedas lanzar con
   `script.py`. No guarda nada.
3. **Crear lista y descargar CSV**: exporta el CSV (se abre bien en Excel) a `listas/` y registra
   la entrega en `entregas.json`.

Reglas que se cumplen siempre:

- A una agencia **nunca se le repite un lead**: cada mes recibe negocios nuevos.
- Los leads de un pedido **exclusivo** (plan Premium) no se venden a nadie más, y un pedido
  exclusivo solo lleva leads que no se han vendido nunca.
- Los leads se ordenan por oportunidad y se reparten por turnos entre los grupos
  sector × ciudad, para que la lista no salga entera de un solo grupo.
- Tus **Interesados**, los negocios con web propia y los cerrados no entran nunca.

En la misma página:

- **Suscripciones**: cada agencia con su plan, entregas, leads recibidos y la fecha de la
  próxima lista (un mes después de la última), con aviso cuando toca o va atrasada.
  **Preparar lista** rellena el pedido con lo que pidió la última vez: solo queda previsualizar
  y crear.
- **Muestra gratis (10 leads)**: descarga los 10 mejores leads con los filtros del formulario para
  enseñárselos a una agencia que estás captando. No se registra como entrega.
- **Listas entregadas**: historial con enlace para volver a descargar cada CSV.
- Arriba: agencias, **ingresos al mes**, listas pendientes y leads entregados.

**Por consola:**

```bash
cd app/scraper-python
python crear_lista.py --cliente "Agencia Sol" --plan basico --sector taller --ciudad Murcia
python crear_lista.py --cliente "Agencia Sol" --cantidad 50 --sector reformas --ciudad Getafe \
                      --requiere movil --min 60
python crear_lista.py ... --simular   # solo muestra qué saldría
python crear_lista.py --entregas      # historial de entregas
```

Los planes (cantidad, exclusividad y precio) viven en un único fichero,
[`app/comun/comun/planes.json`](app/comun/comun/planes.json): lo usan el panel,
`crear_lista.py` y la landing. Para cambiar un precio, cámbialo solo ahí.

---

## 6. Landing pública

La carpeta [`landing/`](landing/) es una web estática (Astro + Tailwind), independiente del panel,
para darte a conocer como agencia:

| Página         | Para quién        | Qué ofrece |
| -------------- | ----------------- | ---------- |
| `/`            | Negocios locales  | Webs de 90 a 300 € en pago único, mantenimiento opcional, apps desde 2.000 € y maqueta gratis en 48 h |
| `/agencias`    | Agencias          | Planes de listas (de `planes.json`) y muestra gratis de 10 leads |
| `/aviso-legal` | —                 | Aviso legal (LSSI) y privacidad |

**No está conectada al panel, a propósito.** Sus botones abren WhatsApp o el email con el mensaje
ya escrito. El resto (maqueta, muestra, lista) lo haces desde el panel en local. Así el backend,
que envía mensajes reales, nunca queda expuesto a internet.

**Antes de publicarla**, rellena los `TODO` de [`landing/src/config.ts`](landing/src/config.ts):
nombre de la agencia (ahora provisional: *Barrio Digital*), WhatsApp, teléfono, email, dominio,
ciudad, y titular y NIF para el aviso legal. Ahí también están los paquetes, los extras, el mantenimiento, la oferta de apps y las condiciones
de pago y contrato (`WEB`, `APPS` y `PAGO`). Si cambias un precio, cámbialo también en la sección 9.

**Publicarla gratis** (Cloudflare Pages o Netlify): conecta el repositorio con carpeta raíz
`landing`, comando de build `npm run build` y carpeta de salida `dist`.

---

## 7. Datos y ficheros

Todo vive en la raíz del proyecto. Los que contienen datos de negocios están fuera de git.

| Fichero | Qué guarda |
| ------- | ---------- |
| `Leads Google Maps.csv` | La base de datos de leads (una fila por negocio) |
| `.env` | Tus claves (nunca se sube) |
| `bajas.txt` | Quien pidió no recibir más mensajes (email, teléfono o usuario, uno por línea) |
| `whatsapp_log.json`, `email_log.json`, `instagram_log.json` | A quién se ha escrito, para no repetir |
| `pesos_oportunidad.json` | Pesos calibrados del modelo de oportunidad |
| `entregas.json` | Listas vendidas: qué leads recibió cada agencia (no repetir, exclusividad) |
| `listas/` | CSV entregados a agencias |
| `maquetas/` | Maquetas HTML generadas (para verlas en local) |
| `landing/public/m/`, `.maquetas_secret` | Copias publicables de las maquetas y la clave de sus códigos |
| `qr.png`, `.wwebjs_auth/` | QR y sesión de WhatsApp. Si falla la vinculación, borra `.wwebjs_auth/` y vuelve a escanear |
| `app/scraper-python/usage.json`, `search_state.json` | Límite diario y búsquedas ya hechas |
| `.logs/` | Logs de los servicios de `start.sh` |

El CSV se escribe con bloqueo y de forma atómica: scripts y panel pueden usarlo a la vez sin
pisarse ni corromperlo.

---

## 8. Tests, seguridad y privacidad

### Tests (ninguno toca tus datos reales)

```bash
cd app/backend && pip install -r requirements-dev.txt && python -m pytest
cd ../scraper-python && ../backend/.venv/bin/python -m pytest   # scripts y paquete comun
cd ../whatsApp_node && npm test
cd ../frontend && npx astro check
cd ../../landing && npx astro check
```

### Seguridad

- El backend solo escucha en `127.0.0.1` y solo acepta peticiones del panel local (Origin y Host
  comprobados): ninguna web externa puede lanzar envíos.
- Los envíos piden confirmación, solo van a los seleccionados y nunca repiten destinatario.
- `start.sh` crea los ficheros con permisos solo para tu usuario.

### Privacidad

- Todos los emails llevan la línea para darse de baja, y las bajas se respetan en todos los canales.
- Muchos de estos negocios son autónomos: su móvil y su email cuentan como **datos personales**
  según el RGPD aunque estén publicados. Antes de vender listas a agencias, consúltalo con un
  asesor.

---

## 9. Precios: webs, mantenimiento y apps

Son los mismos que publica la landing ([`landing/src/config.ts`](landing/src/config.ts)). Si cambias
uno, cámbialo allí también. La explicación completa (por qué estos importes, horas por paquete,
qué no entra) está en [`docs/precios-webs.md`](docs/precios-webs.md).

### Webs (pago único)

|                                       | **Esencial** | **Profesional** ⭐ | **Completa** |
| ------------------------------------- | ------------ | ----------------- | ------------ |
| **Precio**                            | **90 €**     | **180 €**         | **300 €**    |
| Páginas                               | 1 (hasta 4 secciones) | Hasta 5  | Hasta 8      |
| Móvil, botones de llamar y WhatsApp, mapa, horario y reseñas | ✓ | ✓ | ✓          |
| Revisión de la ficha de Google        | ✓            | ✓                 | ✓            |
| Galería de trabajos / antes-después   | —            | ✓                 | ✓            |
| Formulario de contacto                | —            | ✓                 | ✓            |
| SEO local básico                      | —            | ✓                 | ✓            |
| Correo profesional                    | —            | ✓                 | ✓            |
| Reservas o citas online               | —            | —                 | ✓            |
| Carta o catálogo con precios          | —            | —                 | ✓            |
| Segundo idioma                        | —            | —                 | ✓            |
| Rondas de cambios                     | 2            | 3                 | 4            |
| Plazo                                 | 7 días       | 10 días           | 14 días      |

**Extras sueltos:** sección o página adicional 25 € · galería 30 € · formulario 20 € · correo
profesional 20 € · reservas online 60 € · segundo idioma 50 € · logo sencillo 40 € · ronda de
cambios extra 15 € · entrega urgente (3 días) +30 %. Si alguien suma tres extras o más, ofrécele el
paquete superior.

**Qué recomendar según el sector:** taller → Esencial · reformas → Profesional (galería) ·
peluquería o estética → Profesional + reservas · restaurante → Profesional + carta ·
fisioterapia o clínica → Completa (citas).

### Pago y contrato

**Cómo se cobra y se formaliza (siempre):**

- **Contrato firmado en todos los encargos**, también en el Esencial de 90 €, antes de empezar a
  trabajar. Debe recoger qué incluye el paquete (y qué no), el plazo, el precio y los plazos de
  pago, cuántas rondas de cambios hay y cuánto cuesta una extra, que el dominio queda a nombre del
  cliente y, si hay mantenimiento, su precio y cómo se da de baja.
- **Todos los pagos por Bizum:**

  | Encargo                   | Cuándo se paga                                     |
  | ------------------------- | -------------------------------------------------- |
  | Web Esencial              | 100 % al publicar                                  |
  | Web Profesional / Completa | 50 % al firmar el contrato y 50 % al publicar     |
  | Extras                    | Junto con el pago final                            |
  | Mantenimiento de web      | Cada mes (15 €) o de una vez al año (150 €)        |
  | App móvil                 | 50 % al firmar y 50 % al publicar                  |
  | Mantenimiento de app      | Cada mes                                           |

- **No se publica nada sin el pago final recibido.**
- **Bizum tiene límites por operación y por día**, y dependen del banco (lo habitual es hasta
  1.000 € por envío). El 50 % de una app de 2.000 € cabe justo; en una app más cara, parte cada
  pago en varios Bizum o pásate a transferencia para ese encargo.
- **Guarda el justificante de cada Bizum** junto a su factura. Los cobros por Bizum de una
  actividad económica tienen que declararse como cualquier otro ingreso.

### Mantenimiento de webs (opcional)

**15 €/mes o 150 €/año**, sin permanencia. Incluye dominio y alojamiento gestionados, 30 minutos
de cambios al mes y copias de seguridad. A ti te cuesta unos 10 €/año (el dominio `.es`; el
alojamiento estático es gratis). Ofrécelo al cerrar la venta, no antes. Sin mantenimiento, el
dominio queda a nombre del cliente y los cambios se cobran como ronda extra.

### Aplicaciones móviles

**Desde 2.000 €**, con presupuesto cerrado tras una llamada. Incluye app para iPhone y Android,
diseño a medida, panel para gestionar contenidos, reservas o pedidos, publicación en App Store y
Google Play y 3 meses de soporte. Las cuentas de desarrollador las paga el cliente (Apple 99 $/año,
Google 25 $ una vez). Contrato con el presupuesto cerrado por escrito y pago por Bizum: 50 % al
firmar y 50 % al publicar.

**Mantenimiento de apps: desde 60 €/mes.** Incluye actualizaciones para las nuevas versiones de
iOS y Android y la corrección de errores. Una app sin mantener deja de funcionar bien en uno o dos años.

### Lo que no entra

Tiendas online (mínimo 500–800 € o derivar a Shopify), webs que el cliente edita él solo
(WordPress con panel), redacción completa o fotos profesionales, y prometer posicionamiento en Google.

### Cuentas para el objetivo de Navidad (~300 €)

| Combinación                    | Total |
| ------------------------------ | ----- |
| 4 × Esencial                   | 360 € |
| 1 × Profesional + 2 × Esencial | 360 € |
| 2 × Profesional                | 360 € |
| 1 × Completa                   | 300 € |

Una venta del Profesional equivale a dos Esenciales: en diciembre lo que escasea es el tiempo para
contactar y cerrar, así que empuja el paquete del medio.

---

## 10. Modelo de negocio — venta de listas a agencias

### Idea

Vender listas de negocios locales enriquecidas (nombre, teléfono, email, redes sociales) a agencias de marketing, diseño web y publicidad en España mediante una suscripción mensual.

Las agencias necesitan prospectar constantemente pero no tienen tiempo ni herramientas para hacerlo. Este pipeline automatiza ese trabajo y entrega listas listas para usar, segmentadas por sector y ciudad.

### Cliente objetivo

- Agencias de diseño web (buscan negocios sin web o con web antigua)
- Agencias de marketing digital y SEO (necesitan pipeline de clientes)
- Agencias de publicidad en Meta/Google Ads (buscan negocios locales activos)
- Agencias de reputación online (buscan negocios con pocas reseñas)

### Propuesta de valor

> "Cada mes te entrego una lista fresca de negocios en tu sector y ciudad, con email, teléfono y redes sociales verificadas. Tú solo tienes que cerrar la venta."

Lo que diferencia estas listas de las bases de datos genéricas del mercado:

- Segmentación a medida (sector + ciudad específica)
- Datos enriquecidos con email y redes sociales reales
- Listas frescas cada mes, no datos desactualizados
- Precio asequible para agencias pequeñas

### Modelo de precios

| Plan     | Contenido                                    | Precio    |
| -------- | -------------------------------------------- | --------- |
| Básico   | 100 leads/mes (sector + ciudad)              | 80€/mes   |
| Estándar | 300 leads/mes + segmentación avanzada        | 150€/mes  |
| Premium  | 500 leads/mes + exclusividad por zona        | 300€/mes  |

Los planes (cantidad, exclusividad y precio) viven en un único fichero,
[`app/comun/comun/planes.json`](app/comun/comun/planes.json): lo usan el panel,
`crear_lista.py` y la landing. Para cambiar un precio, cámbialo solo ahí.

### Objetivo de ingresos

Meta: **600-800€/mes** en 5 meses.

| Mes | Acción                                                          | Clientes | Ingresos estimados |
| --- | --------------------------------------------------------------- | -------- | ------------------ |
| 1   | Montar el pipeline, generar listas de muestra                   | 0        | 0€                 |
| 2   | Contactar 50-100 agencias en LinkedIn, cerrar primeros clientes | 2-3      | 160-450€           |
| 3   | Iterar con feedback, crecer cartera                             | 4-5      | 320-750€           |
| 4-5 | Cartera estable, referidos                                      | 6-8      | 600-800€           |

### Canal de captación

LinkedIn: buscar "agencia marketing" + ciudad española y contactar con una muestra de lista gratuita como demostración.

### Costes operativos

| Herramienta                        | Coste                                          |
| ---------------------------------- | ---------------------------------------------- |
| Google Places API                  | ~0€ (dentro del free tier para volumen bajo)   |
| scrape.do (enriquecimiento)        | 0€/mes (1.000 créditos gratis = ~250 negocios) |
| scrape.do plan de pago (si escala) | $29/mes                                        |

Con el plan gratuito de scrape.do se pueden enriquecer ~250 negocios al mes, suficiente para los primeros clientes sin coste.

### Escalado — giro a SaaS

Cuando la cartera llegue a **8-10 agencias** pagando manualmente y gestionar los pedidos empiece a consumir tiempo, el siguiente paso es convertir el pipeline en un SaaS donde cada agencia se autogestiona:

- Panel web propio por cliente (sector, ciudad, cantidad de leads)
- El pipeline corre automáticamente y entrega el CSV en su panel
- Cobro por suscripción mensual via Stripe

Lo que ya está construido cubre el 80% de la base técnica. Lo que faltaría añadir:

| Ya existe                 | Por construir                           |
| ------------------------- | --------------------------------------- |
| Scraper de negocios       | Panel web por cliente                   |
| Enriquecimiento de emails | Sistema de pagos (Stripe)               |
| Frontend Astro            | Autenticación de usuarios               |
| Backend FastAPI           | Cola de trabajos (evitar solapamientos) |

Modelo de precios objetivo para el SaaS:

| Plan    | Leads/mes  | Precio    |
| ------- | ---------- | --------- |
| Starter | 100        | 29€/mes   |
| Pro     | 500        | 79€/mes   |
| Agency  | ilimitado  | 199€/mes  |

Con 50 clientes en plan Starter son **1.450€/mes recurrentes y automáticos sin intervención manual**.
