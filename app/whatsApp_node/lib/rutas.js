// Rutas absolutas: el script funciona igual lo lance el panel (cwd = raíz) o se
// ejecute a mano desde app/whatsApp_node/.
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..', '..');

module.exports = {
    ROOT,
    ENV_FILE: path.join(ROOT, '.env'),
    CSV_FILE: path.join(ROOT, 'Leads Google Maps.csv'),
    LOG_FILE: path.join(ROOT, 'whatsapp_log.json'),
    BAJAS_FILE: path.join(ROOT, 'bajas.txt'),
    QR_FILE: path.join(ROOT, 'qr.png'),
};
