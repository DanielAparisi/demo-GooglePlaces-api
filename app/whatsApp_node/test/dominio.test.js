const { test } = require('node:test');
const assert = require('node:assert/strict');
const path = require('path');

const { ciudadDe, esMovil, limpiarDato, numeroCanonico, estaSeleccionado } = require('../lib/dominio');

// Mismos casos que los tests de Python (app/scraper-python/comun/dominio.py)
const CASOS = require(path.join(__dirname, '..', '..', 'scraper-python', 'tests', 'casos_dominio.json'));

test('ciudadDe coincide con Python', () => {
    for (const [ubicacion, ciudad] of CASOS.ciudad) assert.equal(ciudadDe(ubicacion), ciudad, ubicacion);
    assert.equal(ciudadDe(null), '');
});

test('esMovil coincide con Python', () => {
    for (const [telefono, movil] of CASOS.movil) assert.equal(esMovil(telefono), movil, telefono);
});

test('limpiarDato coincide con Python', () => {
    for (const [sucio, limpio] of CASOS.limpiar_dato) assert.equal(limpiarDato(sucio), limpio);
});

test('numeroCanonico unifica formatos del mismo número', () => {
    const formas = ['612 345 678', '612345678', '+34 612 34 56 78', '34612345678', '(+34) 612-345-678'];
    assert.deepEqual(new Set(formas.map(numeroCanonico)), new Set(['34612345678']));
    assert.equal(numeroCanonico(''), '');
});

test('estaSeleccionado', () => {
    for (const v of ['True', 'true', '1', 'yes']) assert.equal(estaSeleccionado(v), true);
    for (const v of ['False', '', undefined, null]) assert.equal(estaSeleccionado(v), false);
});
