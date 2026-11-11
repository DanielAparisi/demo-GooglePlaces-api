"""Ajusta los pesos del modelo de oportunidad con el resultado de tus llamadas.

    python calibrar.py            → muestra cómo va el modelo y, si hay datos, recalibra y guarda
    python calibrar.py --simular  → enseña los pesos nuevos sin guardarlos
    python calibrar.py --reset    → vuelve a los pesos de partida

Cuenta solo las llamadas marcadas como "Interesado" o "No interesado" en el panel.
Los pesos se guardan en pesos_oportunidad.json; el panel los usa al momento.
"""
import argparse
import sys

from comun import calibracion, leads_csv, rutas
from comun.oportunidad import NOMBRES_BLOQUE, PESOS_BASE, cargar_pesos


def _tabla_rendimiento(leads, pesos):
    print("\nTasa de interés por prioridad (pesos actuales):")
    for f in calibracion.rendimiento(leads, pesos):
        tasa = f"{f['tasa']:.0%}" if f['tasa'] is not None else '—'
        print(f"  {f['nivel']:<6} {f['leads']:>4} leads · {f['resultados']:>3} con resultado · "
              f"{f['interesados']:>3} interesados · tasa {tasa}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--simular', action='store_true', help='calcular sin guardar')
    parser.add_argument('--reset', action='store_true', help='borrar la calibración y volver a los pesos de partida')
    args = parser.parse_args(argv)

    if args.reset:
        rutas.PESOS_FILE.unlink(missing_ok=True)
        print("Pesos de partida restaurados.")
        return 0

    leads = leads_csv.leer().to_dict('records') if rutas.CSV_FILE.exists() else []
    actuales = cargar_pesos(rutas.PESOS_FILE)
    _tabla_rendimiento(leads, actuales)

    try:
        nueva = calibracion.calibrar(leads)
    except ValueError as e:
        print(f"\n{e}")
        return 0

    print(f"\nCalibración con {nueva['resultados']} llamadas "
          f"({nueva['interesados']} interesados) · confianza {nueva['confianza']:.0%}")
    print(f"  {'Bloque':<20}{'antes':>7}{'ahora':>7}   interesados vs no")
    for b in PESOS_BASE:
        d = nueva['detalle'][b]
        print(f"  {NOMBRES_BLOQUE[b]:<20}{actuales[b]:>7.1f}{nueva['pesos'][b]:>7.1f}   "
              f"{d['media_interesados']:.2f} vs {d['media_no_interesados']:.2f}")

    if args.simular:
        print("\n(simulación: no se ha guardado nada)")
        return 0
    calibracion.guardar(rutas.PESOS_FILE, nueva)
    print(f"\nGuardado en '{rutas.PESOS_FILE.name}'.")
    _tabla_rendimiento(leads, nueva['pesos'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
