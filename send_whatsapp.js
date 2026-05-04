const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const { parse } = require('csv-parse/sync');
const Groq = require('groq-sdk');

const CSV_FILE = 'Leads Google Maps.csv';
const DELAY_MS = 8000;
const LOG_FILE = 'whatsapp_log.json';
const GROQ_API_KEY = '***GROQ_KEY_ROTADA***';

// ─── Groq (Llama 3.3): generar mensaje personalizado ─────────────────────────

const groq = new Groq({ apiKey: GROQ_API_KEY });

async function generarMensaje(nombre, categoria, ubicacion) {
    const ciudad = ubicacion.split(',').slice(-2, -1)[0]?.trim() || ubicacion;

    const prompt = `Eres un consultor de marketing digital. Escribe un mensaje de WhatsApp corto y profesional en español para contactar a un negocio local que NO tiene página web ni presencia digital.

Datos del negocio:
- Nombre: ${nombre}
- Categoría: ${categoria}
- Ciudad: ${ciudad}

Requisitos del mensaje:
- Tono cercano pero profesional
- Máximo 5 líneas
- Menciona explícitamente el nombre del negocio y su ciudad
- Ofrece una primera consulta gratuita para mejorar su presencia en Google
- Termina con una pregunta para abrir conversación
- Usa emojis con moderación (máximo 2)
- NO uses asteriscos para negritas, solo texto plano`;

    const response = await groq.chat.completions.create({
        model: 'llama-3.3-70b-versatile',
        messages: [{ role: 'user', content: prompt }],
        temperature: 0.8,
        max_tokens: 300,
    });

    return response.choices[0].message.content.trim();
}

// ─── Utilidades ──────────────────────────────────────────────────────────────

function formatearTelefono(telefono) {
    const limpio = telefono.replace(/\s+/g, '').replace(/[^\d+]/g, '');
    if (limpio.startsWith('+')) return limpio.slice(1) + '@c.us';
    if (limpio.startsWith('34')) return limpio + '@c.us';
    return '34' + limpio + '@c.us';
}

function cargarLog() {
    if (fs.existsSync(LOG_FILE)) return JSON.parse(fs.readFileSync(LOG_FILE, 'utf8'));
    return { enviados: [], fallidos: [] };
}

function guardarLog(log) {
    fs.writeFileSync(LOG_FILE, JSON.stringify(log, null, 2));
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function leerCSV() {
    const contenido = fs.readFileSync(CSV_FILE, 'utf8').replace(/^﻿/, '');
    return parse(contenido, { columns: true, skip_empty_lines: true });
}

// ─── Main ─────────────────────────────────────────────────────────────────────

async function main() {
    if (!GROQ_API_KEY || GROQ_API_KEY === 'SU_GROQ_API_KEY') {
        console.error('❌ Añade tu GROQ_API_KEY en la línea 10 del script.');
        console.error('   Consíguela gratis en: console.groq.com → API Keys');
        process.exit(1);
    }

    const filas = leerCSV();
    const log = cargarLog();
    const yaEnviados = new Set(log.enviados.map(e => e.telefono));

    const pendientes = filas.filter(f =>
        f['Teléfono'] && f['Teléfono'].trim() !== '' && !yaEnviados.has(f['Teléfono'].trim())
    );

    console.log(`Total en CSV: ${filas.length}`);
    console.log(`Ya enviados:  ${log.enviados.length}`);
    console.log(`Pendientes:   ${pendientes.length}\n`);

    if (pendientes.length === 0) {
        console.log('No hay mensajes pendientes.');
        process.exit(0);
    }

    // Pre-generar todos los mensajes con Groq antes de conectar WhatsApp
    console.log('Generando mensajes con IA...');
    const mensajes = [];
    for (const fila of pendientes) {
        const msg = await generarMensaje(
            fila['Nombre del negocio'],
            fila['Categoría'] || 'Negocio local',
            fila['Ubicación'] || ''
        );
        mensajes.push(msg);
        process.stdout.write('.');
    }
    console.log(' ✓\n');

    const client = new Client({
        authStrategy: new LocalAuth({ clientId: 'leads-bot' }),
        puppeteer: { args: ['--no-sandbox', '--disable-setuid-sandbox'] }
    });

    client.on('qr', (qr) => {
        console.log('\n📱 Escanea este QR con tu WhatsApp (Ajustes → Dispositivos vinculados):\n');
        qrcode.generate(qr, { small: true });
    });

    client.on('ready', async () => {
        console.log('✅ WhatsApp conectado. Iniciando envíos...\n');

        for (let i = 0; i < pendientes.length; i++) {
            const fila = pendientes[i];
            const nombre = fila['Nombre del negocio'];
            const telefonoRaw = fila['Teléfono'].trim();
            const chatId = formatearTelefono(telefonoRaw);
            const mensaje = mensajes[i];

            console.log(`[${i + 1}/${pendientes.length}] ${nombre} (${telefonoRaw})`);
            console.log(`  Mensaje: ${mensaje.slice(0, 80)}...`);

            try {
                await client.sendMessage(chatId, mensaje);
                log.enviados.push({ nombre, telefono: telefonoRaw, chatId, mensaje, fecha: new Date().toISOString() });
                guardarLog(log);
                console.log(`  ✓ Enviado`);
            } catch (err) {
                log.fallidos.push({ nombre, telefono: telefonoRaw, error: err.message, fecha: new Date().toISOString() });
                guardarLog(log);
                console.log(`  ✗ Error: ${err.message}`);
            }

            if (i < pendientes.length - 1) {
                console.log(`  ⏳ Esperando ${DELAY_MS / 1000}s...`);
                await sleep(DELAY_MS);
            }
        }

        console.log(`\n🎉 Completado. Enviados: ${log.enviados.length} | Fallidos: ${log.fallidos.length}`);
        await client.destroy();
        process.exit(0);
    });

    client.on('auth_failure', () => {
        console.error('❌ Fallo de autenticación. Borra la carpeta .wwebjs_auth y vuelve a intentarlo.');
        process.exit(1);
    });

    client.initialize();
}

main();
