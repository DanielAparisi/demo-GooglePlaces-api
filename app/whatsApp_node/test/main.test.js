const { test, beforeEach, afterEach } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const rutas = require('../lib/rutas');
const { main } = require('../send_whatsapp');

const originales = { ...rutas };
let dir;

beforeEach(() => {
    // Ningún test toca los datos reales ni el .env (que tiene la clave de Groq)
    dir = fs.mkdtempSync(path.join(os.tmpdir(), 'wa-main-'));
    for (const clave of ['ENV_FILE', 'CSV_FILE', 'LOG_FILE', 'BAJAS_FILE', 'QR_FILE']) {
        rutas[clave] = path.join(dir, path.basename(originales[clave]));
    }
    delete process.env.GROQ_API_KEY;
    fs.writeFileSync(rutas.CSV_FILE,
        '﻿Nombre del negocio,Teléfono,Ubicación,selected\n' +
        'Taller Pepe,612 345 678,"C. Sol, 5, 30001 Murcia, Murcia, Spain",True\n' +
        'Fisio Fijo,968 123 456,"Av. Mar, 3, 30500 Molina, Spain",True\n');
});

afterEach(() => Object.assign(rutas, originales));

test('--dry-run redacta pero no conecta ni escribe el log', async (t) => {
    const salida = [];
    t.mock.method(console, 'log', (...a) => salida.push(a.join(' ')));
    t.mock.method(console, 'warn', () => {});
    t.mock.method(process.stdout, 'write', () => true);

    const codigo = await main(['--dry-run', '--selected-only']);

    assert.equal(codigo, 0);
    const texto = salida.join('\n');
    assert.match(texto, /Taller Pepe \(612 345 678\)/);
    assert.doesNotMatch(texto, /Fisio Fijo \(/);
    assert.match(texto, /no se ha enviado nada/);
    assert.equal(fs.existsSync(rutas.LOG_FILE), false);
});

test('sin pendientes termina sin conectar', async (t) => {
    fs.writeFileSync(rutas.LOG_FILE, JSON.stringify({ enviados: [{ telefono: '+34612345678' }] }));
    t.mock.method(console, 'log', () => {});
    t.mock.method(process.stdout, 'write', () => true);

    assert.equal(await main([]), 0);
});
