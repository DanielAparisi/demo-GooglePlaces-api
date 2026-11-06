// Envía mensajes de WhatsApp a los leads con móvil.
//
//   node send_whatsapp.js                   → todos los pendientes
//   node send_whatsapp.js --selected-only   → solo los marcados en el panel
//   node send_whatsapp.js --dry-run         → redacta y muestra los mensajes, no conecta ni envía
//
// Nunca escribe dos veces al mismo número (log), ni a quien ha pedido la baja (bajas.txt).
// Si en QR_TIMEOUT_MS nadie vincula la cuenta, o WhatsApp se desconecta, el proceso
// termina: así el panel puede volver a lanzarlo.
const fs = require('fs');

const rutas = require('./lib/rutas');
const { cargarEnv } = require('./lib/ficheros');
const { esMovil, numeroCanonico } = require('./lib/dominio');
const { LogEnvios, cargarBajas, leerCSV, seleccionarPendientes } = require('./lib/envios');
const { redactar } = require('./lib/mensaje');

const DELAY_MS = 8000;
const QR_TIMEOUT_MS = 3 * 60 * 1000;

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

function borrarQR() {
    fs.rmSync(rutas.QR_FILE, { force: true });
}

async function prepararEnvios(args) {
    const filas = leerCSV(rutas.CSV_FILE);
    const log = new LogEnvios(rutas.LOG_FILE);
    const pendientes = seleccionarPendientes(filas, {
        enviados: log.numerosEnviados(),
        bajas: cargarBajas(rutas.BAJAS_FILE),
        soloSeleccionados: args.soloSeleccionados,
    });

    if (args.soloSeleccionados) console.log('Modo: solo leads seleccionados desde la web');
    console.log(`Total en CSV: ${filas.length}`);
    console.log(`Fijos (sin WhatsApp, omitidos): ${filas.filter(f => f['Teléfono'] && !esMovil(f['Teléfono'])).length}`);
    console.log(`Ya enviados:  ${log.datos.enviados.length}`);
    console.log(`Pendientes:   ${pendientes.length}\n`);

    // Los mensajes se redactan antes de conectar WhatsApp
    console.log('Preparando mensajes...');
    const envios = [];
    for (const fila of pendientes) {
        envios.push({ fila, mensaje: await redactar(fila) });
        process.stdout.write('.');
    }
    console.log(' ✓\n');
    return { log, envios };
}

async function enviarTodos(client, log, envios) {
    for (let i = 0; i < envios.length; i++) {
        const { fila, mensaje } = envios[i];
        const nombre = fila['Nombre del negocio'];
        const telefono = String(fila['Teléfono']).trim();
        const numero = numeroCanonico(telefono);

        console.log(`[${i + 1}/${envios.length}] ${nombre} (${telefono})`);
        console.log(`  Mensaje: ${mensaje.slice(0, 80)}...`);
        try {
            // WhatsApp ya no acepta enviar a "<número>@c.us" si nunca habéis hablado
            // ("No LID for user"): hay que resolver antes el id real del número.
            const numberId = await client.getNumberId(numero);
            if (!numberId) throw new Error('El número no tiene WhatsApp');
            await client.sendMessage(numberId._serialized, mensaje);
            log.enviado({ nombre, telefono, chatId: `${numero}@c.us`, mensaje });
            console.log('  Enviado');
        } catch (err) {
            log.fallido({ nombre, telefono, error: err.message });
            console.log(`  Error: ${err.message}`);
        }
        if (i < envios.length - 1) {
            console.log(`  ⏳ Esperando ${DELAY_MS / 1000}s...`);
            await sleep(DELAY_MS);
        }
    }
}

function conectarYEnviar(log, envios) {
    // Import aquí: arranca Chromium y no hace falta en --dry-run
    const { Client, LocalAuth } = require('whatsapp-web.js');
    const qrcode = require('qrcode-terminal');
    const QRCode = require('qrcode');

    const client = new Client({ authStrategy: new LocalAuth({ clientId: 'leads-bot' }) });

    const terminar = async (codigo, motivo) => {
        clearTimeout(limiteQR);
        borrarQR();
        if (motivo) console.error(motivo);
        try { await client.destroy(); } catch { /* ya cerrado */ }
        process.exit(codigo);
    };

    const limiteQR = setTimeout(
        () => terminar(1, `⏱ Nadie ha vinculado WhatsApp en ${QR_TIMEOUT_MS / 60000} min. Vuelve a lanzarlo desde el panel.`),
        QR_TIMEOUT_MS,
    );

    client.on('qr', async (qr) => {
        qrcode.generate(qr, { small: true });
        await QRCode.toFile(rutas.QR_FILE, qr, { width: 400 });
        fs.chmodSync(rutas.QR_FILE, 0o600);
        console.log(`\nQR guardado en ${rutas.QR_FILE}: escanéalo desde el panel.\n`);
    });

    client.on('ready', async () => {
        clearTimeout(limiteQR);
        borrarQR(); // ya no sirve: que el panel no siga mostrándolo
        console.log('✅ WhatsApp conectado. Iniciando envíos...\n');
        await enviarTodos(client, log, envios);
        console.log(`\nCompletado. ${log.resumen()}`);
        await terminar(0);
    });

    client.on('auth_failure', () =>
        terminar(1, '❌ Fallo de autenticación. Borra la carpeta .wwebjs_auth y vuelve a intentarlo.'));

    client.on('disconnected', (motivo) =>
        terminar(1, `❌ WhatsApp se ha desconectado (${motivo}). Lo ya enviado está en el log; vuelve a lanzarlo para seguir.`));

    client.initialize();
}

async function main(argv = process.argv.slice(2)) {
    cargarEnv(rutas.ENV_FILE);
    const args = { soloSeleccionados: argv.includes('--selected-only'), dryRun: argv.includes('--dry-run') };

    const { log, envios } = await prepararEnvios(args);
    if (envios.length === 0) {
        console.log('No hay mensajes pendientes.');
        return 0;
    }
    if (args.dryRun) {
        for (const { fila, mensaje } of envios) {
            console.log(`── ${fila['Nombre del negocio']} (${fila['Teléfono']})\n${mensaje}\n`);
        }
        console.log('Modo --dry-run: no se ha enviado nada.');
        return 0;
    }
    conectarYEnviar(log, envios);
    return null; // el proceso termina desde los eventos del cliente
}

if (require.main === module) {
    main()
        .then(codigo => { if (codigo !== null) process.exit(codigo); })
        .catch(err => { console.error(err); process.exit(1); });
}

module.exports = { main };
