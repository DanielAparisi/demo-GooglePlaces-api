// Log de envíos, lista de bajas y selección de destinatarios.
const fs = require('fs');
const { parse } = require('csv-parse/sync');

const { escribirAtomico } = require('./ficheros');
const { esMovil, estaSeleccionado, numeroCanonico } = require('./dominio');

class LogEnvios {
    constructor(ruta) {
        this.ruta = ruta;
        this.datos = fs.existsSync(ruta) ? JSON.parse(fs.readFileSync(ruta, 'utf8')) : {};
        this.datos.enviados ??= [];
        this.datos.fallidos ??= [];
    }

    // Números ya escritos, en forma canónica: no importa cómo estuvieran escritos.
    numerosEnviados() {
        return new Set(this.datos.enviados.map(e => numeroCanonico(e.telefono)).filter(Boolean));
    }

    #registrar(lista, entrada) {
        this.datos[lista].push({ ...entrada, fecha: new Date().toISOString() });
        escribirAtomico(this.ruta, JSON.stringify(this.datos, null, 2));
    }

    enviado(entrada) { this.#registrar('enviados', entrada); }
    fallido(entrada) { this.#registrar('fallidos', entrada); }

    resumen() {
        return `Enviados: ${this.datos.enviados.length} | Fallidos: ${this.datos.fallidos.length}`;
    }
}

// bajas.txt: un email, usuario de Instagram o teléfono por línea; "#" inicia un comentario.
// Es el mismo fichero que usan los scripts de email e Instagram.
function cargarBajas(ruta) {
    const bajas = new Set();
    if (!fs.existsSync(ruta)) return bajas;
    for (const linea of fs.readFileSync(ruta, 'utf8').split('\n')) {
        const valor = linea.split('#')[0].trim().toLowerCase().replace(/^@/, '');
        if (!valor) continue;
        bajas.add(valor);
        if (/^[+\d][\d\s().-]{7,}$/.test(valor)) bajas.add(numeroCanonico(valor));
    }
    return bajas;
}

function leerCSV(ruta) {
    const contenido = fs.readFileSync(ruta, 'utf8').replace(/^﻿/, '');
    return parse(contenido, { columns: true, skip_empty_lines: true });
}

// Leads a los que escribir: con móvil, sin envío previo ni baja, un único lead por número.
function seleccionarPendientes(filas, { enviados, bajas, soloSeleccionados }) {
    const vistos = new Set();
    return filas.filter(f => {
        const telefono = String(f['Teléfono'] ?? '').trim();
        if (!telefono || !esMovil(telefono)) return false;
        const numero = numeroCanonico(telefono);
        if (enviados.has(numero) || bajas.has(numero) || vistos.has(numero)) return false;
        if (soloSeleccionados && !estaSeleccionado(f['selected'])) return false;
        vistos.add(numero);
        return true;
    });
}

module.exports = { LogEnvios, cargarBajas, leerCSV, seleccionarPendientes };
