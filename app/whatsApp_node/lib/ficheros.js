const fs = require('fs');
const path = require('path');

// Escribe a un temporal y lo renombra: quien lea el fichero (el panel) nunca ve uno a
// medio escribir, y un corte a mitad no deja el original truncado.
function escribirAtomico(ruta, contenido) {
    const tmp = path.join(path.dirname(ruta), `.${path.basename(ruta)}-${process.pid}-${Date.now()}.tmp`);
    try {
        fs.writeFileSync(tmp, contenido);
        if (fs.existsSync(ruta)) fs.chmodSync(tmp, fs.statSync(ruta).mode & 0o777);
        fs.renameSync(tmp, ruta);
    } catch (err) {
        fs.rmSync(tmp, { force: true });
        throw err;
    }
}

// Carga el .env de la raíz sin dependencias (no pisa variables ya definidas).
function cargarEnv(ruta) {
    if (!fs.existsSync(ruta)) return;
    for (const linea of fs.readFileSync(ruta, 'utf8').split('\n')) {
        const m = linea.match(/^\s*([\w]+)\s*=\s*(.*?)\s*$/);
        if (m && m[2] && !linea.trim().startsWith('#') && !(m[1] in process.env)) {
            process.env[m[1]] = m[2].replace(/^['"]|['"]$/g, '');
        }
    }
}

module.exports = { escribirAtomico, cargarEnv };
