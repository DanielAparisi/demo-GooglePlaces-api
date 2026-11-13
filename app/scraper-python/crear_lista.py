"""Crea una lista de leads para una agencia y la exporta a CSV.

    python crear_lista.py --cliente "Agencia Sol" --plan basico --sector taller --ciudad Murcia
    python crear_lista.py --cliente "Agencia Sol" --cantidad 50 --sector reformas --sector fisioterapia \\
                          --ciudad Getafe --ciudad Madrid --requiere movil --min 60
    python crear_lista.py ... --simular      → solo muestra qué saldría, no exporta ni registra
    python crear_lista.py --entregas         → historial de listas entregadas

Planes: basico (100), estandar (300), premium (500 + exclusividad: esos leads no se
vuelven a vender a nadie). A un mismo cliente nunca se le repite un lead.
Cada entrega queda apuntada en entregas.json y el CSV se guarda en listas/.
"""
import argparse
import sys

from comun import leads_csv, listas, rutas
from comun.oportunidad import cargar_pesos
from script import cargar_estado


def _historial():
    entregas = listas.leer_entregas(rutas.ENTREGAS_FILE)
    if not entregas:
        print("Aún no hay listas entregadas.")
    for e in entregas:
        excl = ' · exclusiva' if e.get('exclusivo') else ''
        print(f"  {e['fecha']}  {e['cliente']:<25} {len(e['leads']):>4} leads{excl}  {e.get('archivo', '')}")
    return 0


def _imprimir(lista):
    r, p = lista['resumen'], lista['pedido']
    print(f"Lista para {p['cliente']}: {r['entregados']}/{r['pedidos']} leads "
          f"(de {r['disponibles']} disponibles) · puntuación media {r['puntuacion_media']}")
    print(f"  Prioridad: {r['por_nivel']['Alta']} alta · {r['por_nivel']['Media']} media · {r['por_nivel']['Baja']} baja")
    for grupo, n in list(r['por_grupo'].items())[:10]:
        print(f"    {n:>4}  {grupo}")
    motivos = {k: v for k, v in r['descartes'].items() if v and k != 'no_encajan'}
    if motivos:
        print("  Descartados: " + ', '.join(f"{v} {k.replace('_', ' ')}" for k, v in motivos.items()))
    if r['faltan']:
        print(f"\n⚠ Faltan {r['faltan']} leads. Búsquedas que conviene lanzar con script.py:")
        for s in lista['sugerencias']:
            print(f"    · {s}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--cliente', help='nombre de la agencia')
    parser.add_argument('--plan', choices=listas.PLANES, help='fija cantidad y exclusividad')
    parser.add_argument('--cantidad', type=int, help='nº de leads (manda sobre el plan)')
    parser.add_argument('--sector', action='append', default=[], help='repetible; texto libre (taller, panadería...)')
    parser.add_argument('--ciudad', action='append', default=[], help='repetible; ciudad, barrio o provincia')
    parser.add_argument('--requiere', action='append', default=[], choices=listas.CANALES, help='canal obligatorio')
    parser.add_argument('--min', type=int, default=0, dest='minimo', help='puntuación de oportunidad mínima')
    parser.add_argument('--exclusivo', action='store_true', help='no volver a vender estos leads a nadie')
    parser.add_argument('--simular', action='store_true', help='no exportar ni registrar')
    parser.add_argument('--entregas', action='store_true', help='ver el historial de entregas')
    args = parser.parse_args(argv)

    if args.entregas:
        return _historial()
    if not args.cliente:
        parser.error('falta --cliente')
    plan = listas.PLANES.get(args.plan, {})
    cantidad = args.cantidad or plan.get('cantidad')
    if not cantidad:
        parser.error('indica --plan o --cantidad')

    pedido = {'cliente': args.cliente, 'plan': args.plan, 'cantidad': cantidad, 'sectores': args.sector, 'ciudades': args.ciudad,
              'requiere': args.requiere, 'puntuacion_min': args.minimo,
              'exclusivo': args.exclusivo or plan.get('exclusivo', False)}
    leads = leads_csv.leer().to_dict('records') if rutas.CSV_FILE.exists() else []
    try:
        lista = listas.crear_lista(leads, pedido, listas.leer_entregas(rutas.ENTREGAS_FILE),
                                   pesos=cargar_pesos(rutas.PESOS_FILE),
                                   busquedas_hechas=cargar_estado().get('hechas', []))
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    _imprimir(lista)
    if args.simular or not lista['leads']:
        print("\n(no se ha exportado ni registrado nada)")
        return 0

    ruta = listas.exportar(lista, rutas.LISTAS_DIR)
    entrega = listas.registrar_entrega(rutas.ENTREGAS_FILE, lista, archivo=ruta.name)
    print(f"\n✓ Exportado a {ruta} · entrega '{entrega}' registrada")
    return 0


if __name__ == '__main__':
    sys.exit(main())
