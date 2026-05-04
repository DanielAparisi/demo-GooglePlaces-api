# Lead Generator — Google Places + WhatsApp

Pipeline automatizado de captación de leads para negocios locales en España sin presencia digital. Busca negocios en Google Maps, enriquece los datos con emails y envía mensajes de WhatsApp personalizados generados con IA.

## Flujo

```text
script.py  →  Leads Google Maps.csv  →  enrich_emails.py  →  send_whatsapp.js
   │                  │                          │                    │
   │           (nombres, teléfonos)        (añade emails)    (envía mensajes IA)
   │
Google Places API
```

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
