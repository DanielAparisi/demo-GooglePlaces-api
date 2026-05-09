# Lead Generator — Google Places + WhatsApp

Pipeline automatizado de captación de leads para negocios locales en España sin presencia digital. Busca negocios en Google Maps, enriquece los datos con emails y envía mensajes de WhatsApp personalizados generados con IA.

---

## Modelo de negocio — Venta de listas de leads a agencias

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

---

## Arrancar el monorepo

### Requisitos previos

- Python 3.10+
- Node.js 18+
- Las claves de API configuradas (ver sección Configuración)

### Inicio rápido — un solo comando

```bash
./start.sh
```

Levanta los tres servicios en paralelo y redirige sus logs a `.logs/`:

| Servicio        | URL / acceso                              | Log                  |
| --------------- | ----------------------------------------- | -------------------- |
| Backend FastAPI | [localhost:8000](http://localhost:8000)   | `.logs/backend.log`  |
| Frontend Astro  | [localhost:4321](http://localhost:4321)   | `.logs/frontend.log` |
| WhatsApp Node   | escanea QR en terminal                    | `.logs/whatsapp.log` |

Pulsa `Ctrl+C` para detener todos los servicios a la vez.

### Si prefieres arrancar cada servicio por separado

**Backend (FastAPI):**

```bash
cd app/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend (Astro):**

```bash
cd app/frontend
npm install
npm run dev
```

**WhatsApp Node:**

```bash
cd app/whatsApp_node
npm install
node index.js
```

**Scraper de emails (se ejecuta aparte, no forma parte del servidor):**

```bash
cd app/scraper-python
pip install requests pandas
python enrich_emails.py
```

---

## Evolución del pipeline — Email vs WhatsApp

El canal de contacto depende de si el scraper consigue emails de los negocios:

**Si se obtienen emails (objetivo principal):**

```text
script.py  →  Leads Google Maps.csv  →  enrich_emails.py  →  send_email.py
   │                  │                          │                  │
   │           (nombres, teléfonos)        (añade emails)   (email profesional con IA)
   │
Google Places API
```

El envío se haría mediante email profesional generado con IA, que tiene mayor tasa de respuesta y es más escalable que WhatsApp.

**Si no se consiguen emails (fallback actual):**

```text
script.py  →  Leads Google Maps.csv  →  send_whatsapp.js
   │                  │                        │
   │           (nombres, teléfonos)     (WhatsApp con IA)
   │
Google Places API
```

WhatsApp se mantiene como opción de respaldo para negocios sin email localizable, pero **el objetivo es reemplazarlo por email** una vez el scraper esté operativo.

## Flujo

## Requisitos

### Python

```bash
pip install requests pandas
```

### Node.js

```bash
npm install
```

## Configuración

Antes de ejecutar, configura tus claves de API en cada fichero:

| Fichero             | Variable          | Dónde conseguirla                        |
|---------------------|-------------------|------------------------------------------|
| `script.py`         | `API_KEY`         | Google Cloud Console → Places API        |
| `enrich_emails.py`  | `SCRAPEDO_TOKEN`  | scrape.do                                |
| `send_whatsapp.js`  | `GROQ_API_KEY`    | console.groq.com → API Keys              |

## Uso

### 1. Buscar negocios sin web

```bash
python script.py
```

- Elige aleatoriamente un tipo de negocio y una ciudad de España
- Consulta Google Places Text Search + Place Details
- Filtra solo negocios **sin página web**
- Acumula resultados en `Leads Google Maps.csv` (sin duplicados)
- Límite: **10 búsquedas por día** (configurable con `LIMITE_DIARIO`)

### 2. Enriquecer con emails

```bash
python enrich_emails.py
```

- Lee el CSV y busca emails para los negocios que no los tienen
- Busca en Google y Páginas Amarillas mediante scrape.do
- Filtra dominios genéricos (redes sociales, Google, etc.)
- Actualiza el CSV progresivamente

### 3. Enviar mensajes de WhatsApp

```bash
node send_whatsapp.js
```

- Lee los negocios pendientes del CSV (los que aún no han recibido mensaje)
- Genera un mensaje personalizado por negocio usando **Llama 3.3** via Groq
- Conecta a WhatsApp Web escaneando un QR con tu móvil
- Envía los mensajes con un delay de 8 segundos entre cada uno
- Registra enviados y fallidos en `whatsapp_log.json`

## Archivos generados

| Fichero                 | Descripción                                    |
|-------------------------|------------------------------------------------|
| `Leads Google Maps.csv` | Base de datos de leads acumulada               |
| `whatsapp_log.json`     | Historial de mensajes enviados y fallidos      |
| `usage.json`            | Control del límite diario de búsquedas         |
| `search_state.json`     | Estado de paginación de la búsqueda actual     |
| `qr.png`                | Código QR para conectar WhatsApp (se regenera) |

## Notas

- La sesión de WhatsApp se guarda en `.wwebjs_auth/` — no es necesario escanear el QR cada vez.
- Si falla la autenticación de WhatsApp, borra la carpeta `.wwebjs_auth/` y vuelve a escanear.
- El script de WhatsApp pre-genera todos los mensajes con IA antes de conectar, para minimizar el tiempo de sesión abierta.
