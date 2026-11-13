# El paquete `comun`

La lógica que comparten el backend y los scripts de línea de comandos vive en un paquete de
Python instalable: `comun`, en [`app/comun/`](../app/comun/).

## Qué hay dentro

| Módulo           | Para qué sirve                                                                 |
| ---------------- | ------------------------------------------------------------------------------ |
| `dominio.py`     | Reglas de negocio: sector, ciudad, nombre comercial, tipo de teléfono          |
| `oportunidad.py` | Puntuación de oportunidad de cada lead                                         |
| `calibracion.py` | Ajuste de los pesos de la puntuación con los resultados de las llamadas        |
| `listas.py`      | Creación de las listas que se venden a agencias (+ `planes.json`)              |
| `leads_csv.py`   | Lectura y escritura del CSV de leads con bloqueo entre procesos                |
| `envios.py`      | Logs de envíos y texto de baja                                                 |
| `ficheros.py`    | Escritura atómica de ficheros                                                  |
| `ia.py`          | Cliente de Groq                                                                |
| `entorno.py`     | Carga el `.env` de la raíz y `requerir()` para las claves obligatorias         |
| `rutas.py`       | Rutas de todos los ficheros de datos (CSV, logs, listas…)                      |

```
app/comun/
├── pyproject.toml      ← lo que lo convierte en paquete: nombre, dependencias, ficheros de datos
└── comun/              ← el código que importas con `from comun import …`
    ├── __init__.py
    ├── dominio.py
    └── …
```

La carpeta doble (`comun/comun`) es la estructura estándar: la de fuera es el *proyecto* del
paquete y la de dentro es el *código* que se importa.

## Cómo estaba antes

`comun/` era una subcarpeta de `app/scraper-python/`. Los scripts la encontraban porque se
ejecutaban desde esa carpeta. El backend, que vive en otra carpeta, no la encontraba, así que
[`core/domain.py`](../app/backend/core/domain.py) hacía esto:

```python
sys.path.insert(0, str(ROOT / 'app' / 'scraper-python'))   # "busca módulos también aquí"
import config   # solo para que se cargue el .env como efecto secundario
from comun import ...
```

Funcionaba, pero tenía cuatro problemas:

1. **Dependía de dónde arrancaras.** `comun` solo se encontraba si estabas en la carpeta adecuada
   o si antes se había pasado por `core/domain.py`. Un script nuevo, una consola de Python o un
   test en otra carpeta fallaban con `ModuleNotFoundError: No module named 'comun'`.
2. **El orden de los imports importaba.** Si algún archivo importaba `comun` antes que
   `core/domain.py`, fallaba.
3. **El editor no lo veía.** Pylance o mypy no sabían dónde estaba `comun`, así que el
   autocompletado y "ir a la definición" fallaban a veces.
4. **La librería dependía de los scripts.** `comun/ia.py` hacía `from config import requerir`,
   y `config.py` era un archivo de los scripts. La pieza compartida dependía de una de las piezas
   que la usan, que es justo al revés de como debe ser.

## Cómo está ahora

- `comun` tiene su propio [`pyproject.toml`](../app/comun/pyproject.toml), que declara su nombre,
  sus dependencias (pandas y groq) y que `planes.json` forma parte de él.
- Está instalado en el venv del backend en **modo editable**. Esa línea va en
  [`app/backend/requirements.txt`](../app/backend/requirements.txt):

  ```
  -e ../comun
  ```

- `config.py` ahora es [`comun/entorno.py`](../app/comun/comun/entorno.py). Los scripts usan
  `from comun.entorno import requerir` y el backend importa `comun.entorno` para cargar el `.env`.
- `core/domain.py` ya no toca `sys.path`: son imports normales.

Las direcciones de dependencia quedan limpias:

```
backend  ──┐
           ├──►  comun   (comun no importa nada del backend ni de los scripts)
scripts  ──┘
```

## Ventajas

1. **Se importa desde cualquier sitio.** Con el venv activo, `from comun import listas` funciona
   en el backend, en los scripts, en los tests y en una consola de Python, desde cualquier carpeta.
2. **Las dependencias están a la vista.** `pyproject.toml` dice qué es `comun` y qué necesita.
   Ya no es "una subcarpeta del scraper que el backend toma prestada".
3. **No hay dependencias circulares.** `comun` no sabe nada de quién lo usa, así que se puede
   cambiar o testear por separado.
4. **Los cambios se ven al momento.** Como está instalado en modo editable (`-e`), pip no copia el
   código: apunta a la carpeta. Editas un archivo de `comun` y el backend y los scripts usan la
   versión nueva sin reinstalar nada.
5. **Facilita separar el proyecto en el futuro.** Si algún día el backend va a un servidor y los
   scripts se quedan en tu máquina, cada parte instala `comun` como una dependencia más.

## Lo que hay que saber

- **Instálalo siempre en modo editable.** `rutas.py` calcula la raíz del proyecto a partir de dónde
  está su propio archivo. Con un `pip install` normal (sin `-e`), el código se copiaría al venv y
  buscaría el CSV en el sitio equivocado.
- **Ejecuta `pip install -r requirements.txt` desde `app/backend`.** La ruta `../comun` es relativa
  a la carpeta desde la que lanzas pip. `start.sh` y el README ya lo hacen así.
- **Si creas un venv nuevo**, basta con:

  ```bash
  cd app/backend
  python3 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt     # instala también comun
  ```

- **La copia en JavaScript no se resuelve con esto.**
  [`whatsApp_node/lib/dominio.js`](../app/whatsApp_node/lib/dominio.js) sigue siendo una copia a mano
  de `dominio.py`, porque es otro lenguaje. Si cambias una regla de dominio, cámbiala en los dos
  archivos.
