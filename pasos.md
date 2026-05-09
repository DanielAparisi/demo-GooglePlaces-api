El flujo es en dos pasos desde terminal:

Paso 1 — Buscar más negocios en Google Maps:


cd /home/danielaparisi/projects/demo-GooglePlaces-api/app/scraper-python
source ../backend/.venv/bin/activate
python script.py
Añade negocios nuevos al CSV (hasta 10 búsquedas por día).

Paso 2 — Buscar emails de esos negocios:


python enrich_emails.py
Scrapeа Google y Páginas Amarillas buscando el email de cada negocio sin email.

Paso 3 — Refrescar la landing:
Pulsa el botón ↻ Actualizar en localhost:4321 y aparecen los nuevos datos.