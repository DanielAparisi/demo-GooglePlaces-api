// Reglas de dominio. Son una copia de app/comun/comun/dominio.py: si cambias
// una, cambia la otra. Los tests de ambos lados usan los mismos casos para detectarlo.

// Los datos del negocio vienen de Google Maps y los controla su dueño: se limpian
// (una sola línea, longitud acotada) para que no puedan colar instrucciones al modelo.
function limpiarDato(valor, max = 100) {
    return String(valor ?? '').replace(/[\u0000-\u001f\u007f"`]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, max);
}

function soloDigitos(telefono) {
    return String(telefono ?? '').replace(/[^\d+]/g, '');
}

// Número local español (9 dígitos) sin prefijo internacional.
function numeroLocal(telefono) {
    const limpio = soloDigitos(telefono);
    if (limpio.startsWith('+34')) return limpio.slice(3);
    if (limpio.startsWith('34') && limpio.length === 11) return limpio.slice(2);
    return limpio.replace(/^\+/, '');
}

// En España los móviles empiezan por 6xx o 7xx. Los fijos (9xx, 8xx) no tienen WhatsApp.
function esMovil(telefono) {
    return /^[67]/.test(numeroLocal(telefono));
}

// Forma canónica de un número: "612 345 678", "+34612345678" y "34612345678" → "34612345678".
// Es la clave para no escribir dos veces al mismo número.
function numeroCanonico(telefono) {
    const limpio = soloDigitos(telefono);
    if (!limpio) return '';
    if (limpio.startsWith('+')) return limpio.slice(1);
    if (limpio.startsWith('34') && limpio.length === 11) return limpio;
    return '34' + limpio;
}

// Ciudad de una dirección de Google Maps: va justo detrás del código postal.
// "C. Delicias, 5, Arganzuela, 28005 Madrid, Spain" → "Madrid"
function ciudadDe(ubicacion) {
    const partes = String(ubicacion ?? '').split(',').map(p => p.trim()).filter(Boolean);
    for (let i = partes.length - 1; i >= 0; i--) {
        const m = /^\d{5}\s+(.+)$/.exec(partes[i]);
        if (m) return m[1];
    }
    if (partes.length >= 2) return partes[partes.length - 2];
    return partes[0] ?? '';
}

function estaSeleccionado(valor) {
    return ['true', '1', 'yes'].includes(String(valor ?? '').trim().toLowerCase());
}

module.exports = { limpiarDato, numeroLocal, esMovil, numeroCanonico, ciudadDe, estaSeleccionado };
