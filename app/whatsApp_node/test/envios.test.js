const { test, beforeEach } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const { LogEnvios, cargarBajas, seleccionarPendientes } = require('../lib/envios');
const { completar, redactar, PIE_BAJA, PORTFOLIO_URL } = require('../lib/mensaje');

let dir;
beforeEach(() => { dir = fs.mkdtempSync(path.join(os.tmpdir(), 'wa-test-')); });

const fila = (nombre, telefono, selected = 'True', extra = {}) =>
    ({ 'Nombre del negocio': nombre, 'Teléfono': telefono, selected, ...extra });

// ── Selección ─────────────────────────────────────────────────────────────────

test('un mensaje por número aunque esté escrito de formas distintas', () => {
    const filas = [fila('A', '612 345 678'), fila('A bis', '+34612345678'), fila('B', '622 000 000')];
    const r = seleccionarPendientes(filas, { enviados: new Set(), bajas: new Set(), soloSeleccionados: false });
    assert.deepEqual(r.map(f => f['Nombre del negocio']), ['A', 'B']);
});

test('no repite números del log aunque el formato haya cambiado', () => {
    const ruta = path.join(dir, 'log.json');
    fs.writeFileSync(ruta, JSON.stringify({ enviados: [{ telefono: '612345678' }] }));
    const enviados = new LogEnvios(ruta).numerosEnviados();

    const r = seleccionarPendientes([fila('A', '+34 612 34 56 78')], { enviados, bajas: new Set(), soloSeleccionados: false });
    assert.equal(r.length, 0);
});

test('omite fijos, bajas y no seleccionados', () => {
    const filas = [
        fila('Fijo', '968 123 456'),
        fila('Baja', '633 333 333'),
        fila('No marcado', '644 444 444', 'False'),
        fila('Sin teléfono', ''),
        fila('OK', '655 555 555'),
    ];
    const bajas = new Set(['34633333333']);
    const r = seleccionarPendientes(filas, { enviados: new Set(), bajas, soloSeleccionados: true });
    assert.deepEqual(r.map(f => f['Nombre del negocio']), ['OK']);
});

// ── Bajas y log ───────────────────────────────────────────────────────────────

test('cargarBajas normaliza teléfonos y comparte formato con email/Instagram', () => {
    const ruta = path.join(dir, 'bajas.txt');
    fs.writeFileSync(ruta, '# bajas\nInfo@Pepe.es\n@Fisio_Mar  # por DM\n+34 633 33 33 33\n\n');
    const bajas = cargarBajas(ruta);
    assert.ok(bajas.has('info@pepe.es'));
    assert.ok(bajas.has('fisio_mar'));
    assert.ok(bajas.has('34633333333'));
    assert.equal(cargarBajas(path.join(dir, 'no-existe.txt')).size, 0);
});

test('el log se guarda completo tras cada envío y sin temporales', () => {
    const ruta = path.join(dir, 'log.json');
    const log = new LogEnvios(ruta);
    log.enviado({ telefono: '612345678' });
    log.fallido({ telefono: '622000000', error: 'x' });

    const guardado = JSON.parse(fs.readFileSync(ruta, 'utf8'));
    assert.equal(guardado.enviados.length, 1);
    assert.equal(guardado.fallidos.length, 1);
    assert.deepEqual(fs.readdirSync(dir), ['log.json']);
});

// ── Mensaje ───────────────────────────────────────────────────────────────────

test('todo mensaje lleva porfolio y baja, una sola vez', () => {
    const m = completar('Hola');
    assert.ok(m.includes(PORTFOLIO_URL) && m.endsWith(PIE_BAJA));
    assert.equal(completar(m), m);
});

test('usa el mensaje del CSV si lo hay', async () => {
    const m = await redactar(fila('A', '6', 'True', { Mensaje: 'Mensaje propio' }), () => assert.fail('no debe llamar a la IA'));
    assert.ok(m.startsWith('Mensaje propio'));
});

test('plantilla si la IA falla', async () => {
    const m = await redactar(fila('TALLER PEPE - Mecánica', '6'), async () => { throw new Error('sin IA'); });
    assert.ok(m.includes('He visto TALLER PEPE en Google Maps'));
    assert.ok(m.endsWith(PIE_BAJA));
});
