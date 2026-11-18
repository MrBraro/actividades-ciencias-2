"""
Convex Hull (envolvente convexa) de una nube de puntos
======================================================
Tres algoritmos, todos O(n log n):
  1. Graham Scan
  2. Monotone Chain (Andrew)
  3. Divide and Conquer

Cada algoritmo recibe una lista de puntos (x, y) y devuelve los vértices del
hull en sentido ANTIHORARIO, sin puntos repetidos ni colineales.

Simulación: genera una nube de puntos (por defecto 1 millón), ejecuta los tres
algoritmos, mide sus tiempos, comprueba que den el mismo resultado y dibuja.

Uso:
    python convex_hull.py                       # 1.000.000 puntos en un cuadrado
    python convex_hull.py -n 200000 -d disco    # otra cantidad / distribución
    python convex_hull.py --sin-grafica         # solo tiempos, sin dibujar
"""
import argparse
import math
import random
import sys
import time


# =====================================================================
#  FUNCIONES COMPARTIDAS
# =====================================================================
def cruz(o, a, b):
    """
    Producto cruz de los vectores OA y OB (test de orientación):
      > 0  giro a la izquierda (antihorario)
      < 0  giro a la derecha (horario)
      = 0  los tres puntos son colineales
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def quitar_colineales(hull):
    """Elimina vértices que quedan en medio de una arista (hull cíclico)."""
    res = []
    for p in hull:
        while len(res) >= 2 and cruz(res[-2], res[-1], p) == 0:
            res.pop()
        res.append(p)
    # revisar también la unión entre el final y el inicio
    while len(res) >= 3 and cruz(res[-2], res[-1], res[0]) == 0:
        res.pop()
    while len(res) >= 3 and cruz(res[-1], res[0], res[1]) == 0:
        res.pop(0)
    return res


# #####################################################################
# #####################################################################
#  ALGORITMO 1: GRAHAM SCAN
#  - Pivote: el punto más bajo (menor y; si empata, menor x).
#  - Ordena los demás por ÁNGULO respecto al pivote.
#  - Una sola pasada con una pila: si no hay giro a la izquierda,
#    el último punto de la pila se descarta.
#  - Complejidad: O(n log n) por el ordenamiento; la pasada es O(n).
# #####################################################################
# #####################################################################
def graham_scan(puntos):
    pts = list(set(puntos))                         # sin repetidos
    if len(pts) < 3:
        return sorted(pts)

    # 1. Pivote: el punto más bajo (y si empata, el más a la izquierda)
    pivote = min(pts, key=lambda p: (p[1], p[0]))
    px, py = pivote
    resto = [p for p in pts if p != pivote]

    # 2. Ordenar por ángulo polar respecto al pivote; si empata, por distancia
    resto.sort(key=lambda p: (math.atan2(p[1] - py, p[0] - px),
                              (p[0] - px) ** 2 + (p[1] - py) ** 2))

    # 3. Recorrido con pila
    pila = [pivote]
    for p in resto:
        while len(pila) >= 2 and cruz(pila[-2], pila[-1], p) <= 0:
            pila.pop()                              # giro a la derecha o recto
        pila.append(p)

    return quitar_colineales(pila)
# --------------------------- FIN GRAHAM SCAN --------------------------


# #####################################################################
# #####################################################################
#  ALGORITMO 2: MONOTONE CHAIN (Andrew)
#  - Ordena por x (y si empata, por y). No usa ángulos.
#  - Casco inferior: de izquierda a derecha.
#  - Casco superior: de derecha a izquierda.
#  - Une las dos cadenas quitando los extremos repetidos.
#  - Complejidad: O(n log n) por el ordenamiento; las pasadas son O(n).
# #####################################################################
# #####################################################################
def monotone_chain(puntos):
    pts = sorted(set(puntos))                       # orden por (x, y), sin repetidos
    if len(pts) < 3:
        return pts

    # 1. Casco inferior (izquierda → derecha)
    inferior = []
    for p in pts:
        while len(inferior) >= 2 and cruz(inferior[-2], inferior[-1], p) <= 0:
            inferior.pop()
        inferior.append(p)

    # 2. Casco superior (derecha → izquierda)
    superior = []
    for p in reversed(pts):
        while len(superior) >= 2 and cruz(superior[-2], superior[-1], p) <= 0:
            superior.pop()
        superior.append(p)

    # 3. Unir: el último de cada cadena es el primero de la otra
    hull = inferior[:-1] + superior[:-1]
    return hull if len(hull) >= 3 else quitar_colineales(hull)
# ------------------------- FIN MONOTONE CHAIN -------------------------


# #####################################################################
# #####################################################################
#  ALGORITMO 3: DIVIDE AND CONQUER
#  - Ordena por x una sola vez.
#  - Divide los puntos en dos mitades (izquierda / derecha).
#  - Resuelve cada mitad recursivamente (caso base: 3 puntos o menos).
#  - Combina los dos hulls con la TANGENTE SUPERIOR y la INFERIOR,
#    descartando los puntos que quedan entre ellas.
#  - Complejidad: T(n) = 2T(n/2) + O(n)  →  O(n log n)
# #####################################################################
# #####################################################################
def divide_y_venceras(puntos):
    pts = sorted(set(puntos))                       # orden por (x, y), sin repetidos
    if len(pts) < 3:
        return pts
    return _dyv(pts, 0, len(pts))


def _caso_base(pts):
    """Hull de 1, 2 o 3 puntos, en sentido antihorario."""
    if len(pts) <= 2:
        return list(pts)
    a, b, c = pts
    giro = cruz(a, b, c)
    if giro > 0:
        return [a, b, c]
    if giro < 0:
        return [a, c, b]
    return [a, c]                                   # colineales: solo los extremos


def _dyv(pts, ini, fin):
    """Hull de pts[ini:fin] (ya ordenados por x)."""
    if fin - ini <= 3:
        return _caso_base(pts[ini:fin])
    medio = (ini + fin) // 2
    izq = _dyv(pts, ini, medio)                     # 1. Resolver mitad izquierda
    der = _dyv(pts, medio, fin)                     # 2. Resolver mitad derecha
    return _combinar(izq, der)                      # 3. Combinar


def _dist2(p, q):
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


def _avanzar(fijo, actual, siguiente, lado):
    """
    ¿Conviene mover la tangente de 'actual' a 'siguiente'?
    Sí, si 'siguiente' queda por fuera de la recta fijo→actual (lado),
    o si queda sobre la misma recta pero más lejos (caso colineal).
    """
    c = cruz(fijo, actual, siguiente) * lado
    return c > 0 or (c == 0 and _dist2(fijo, siguiente) > _dist2(fijo, actual))


def _combinar(A, B):
    """
    Une dos hulls (antihorarios) donde todo A está a la izquierda de B.
    Busca las dos tangentes "caminando" por cada hull.
    """
    na, nb = len(A), len(B)
    i_der = max(range(na), key=lambda k: A[k])      # punto más a la derecha de A
    j_izq = min(range(nb), key=lambda k: B[k])      # punto más a la izquierda de B

    # --- Tangente SUPERIOR ---
    # En A se avanza en sentido antihorario (subiendo hacia la izquierda);
    # en B, en sentido horario (subiendo hacia la derecha).
    i, j = i_der, j_izq
    cambio = True
    while cambio:
        cambio = False
        while _avanzar(B[j], A[i], A[(i + 1) % na], -1):    # A[i+1] está por encima
            i = (i + 1) % na
            cambio = True
        while _avanzar(A[i], B[j], B[(j - 1) % nb], +1):    # B[j-1] está por encima
            j = (j - 1) % nb
            cambio = True
    sup_a, sup_b = i, j

    # --- Tangente INFERIOR ---
    # En A se avanza en sentido horario (bajando); en B, antihorario (bajando).
    i, j = i_der, j_izq
    cambio = True
    while cambio:
        cambio = False
        while _avanzar(B[j], A[i], A[(i - 1) % na], +1):    # A[i-1] está por debajo
            i = (i - 1) % na
            cambio = True
        while _avanzar(A[i], B[j], B[(j + 1) % nb], -1):    # B[j+1] está por debajo
            j = (j + 1) % nb
            cambio = True
    inf_a, inf_b = i, j

    # --- Unir: A desde la tangente superior hasta la inferior (antihorario),
    #     luego B desde la tangente inferior hasta la superior (antihorario).
    hull = []
    k = sup_a
    hull.append(A[k])
    while k != inf_a:
        k = (k + 1) % na
        hull.append(A[k])
    k = inf_b
    hull.append(B[k])
    while k != sup_b:
        k = (k + 1) % nb
        hull.append(B[k])

    return quitar_colineales(hull)
# ----------------------- FIN DIVIDE AND CONQUER -----------------------


# =====================================================================
#  SIMULACIÓN
# =====================================================================
ALGORITMOS = {
    "Graham Scan": graham_scan,
    "Monotone Chain": monotone_chain,
    "Divide and Conquer": divide_y_venceras,
}


def generar_puntos(n, semilla=None):
    """
    Genera n puntos con distribución gaussiana (normal) alrededor de (500, 500):
    la mayoría queda cerca del centro y muy pocos se alejan.
    """
    rnd = random.Random(semilla)
    return [(rnd.gauss(500, 120), rnd.gauss(500, 120)) for _ in range(n)]


def normalizar(hull):
    """Rota el hull para que empiece en su menor punto (para poder comparar)."""
    if not hull:
        return []
    k = hull.index(min(hull))
    return hull[k:] + hull[:k]


def es_convexo_y_encierra(hull, puntos):
    """Comprueba que el hull sea convexo y que ningún punto quede por fuera."""
    h = len(hull)
    if h < 3:
        return True
    for k in range(h):
        if cruz(hull[k], hull[(k + 1) % h], hull[(k + 2) % h]) <= 0:
            return False
    for p in puntos:
        for k in range(h):
            if cruz(hull[k], hull[(k + 1) % h], p) < 0:
                return False
    return True


def ejecutar(n, semilla, graficar, archivo):
    print(f"Generando {n:,} puntos (distribución gaussiana)...".replace(",", "."))
    t0 = time.perf_counter()
    puntos = generar_puntos(n, semilla)
    print(f"  listo en {time.perf_counter() - t0:.2f} s\n")

    resultados = {}
    print(f"  {'Algoritmo':<22}{'Tiempo (s)':>12}{'Vértices del hull':>20}")
    print("  " + "-" * 54)
    for nombre, algoritmo in ALGORITMOS.items():
        t0 = time.perf_counter()
        hull = algoritmo(puntos)
        tiempo = time.perf_counter() - t0
        resultados[nombre] = (hull, tiempo)
        print(f"  {nombre:<22}{tiempo:>12.3f}{len(hull):>20}")

    # Verificación: los tres deben dar exactamente el mismo polígono
    hulls = [normalizar(h) for h, _ in resultados.values()]
    iguales = all(h == hulls[0] for h in hulls)
    print("\n  ✔ Los tres algoritmos obtienen el mismo hull" if iguales
          else "\n  ✘ Los algoritmos NO coinciden")

    if graficar:
        dibujar(puntos, resultados, archivo)
    return resultados


def dibujar(puntos, resultados, archivo):
    try:
        import matplotlib
        if not hasattr(sys, "ps1") and not _hay_pantalla():
            matplotlib.use("Agg")                   # sin pantalla: solo guardar
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n  (Instala matplotlib para ver la gráfica: pip install matplotlib)")
        return

    print("\nDibujando...")
    xs = [p[0] for p in puntos]
    ys = [p[1] for p in puntos]
    fig, ejes = plt.subplots(1, 3, figsize=(18, 6.5))
    fig.suptitle(f"Convex Hull de {len(puntos):,} puntos (gaussiana)".replace(",", "."),
                 fontsize=15)

    for ax, (nombre, (hull, tiempo)) in zip(ejes, resultados.items()):
        ax.plot(xs, ys, ",", color="#9aa5b1", alpha=0.6)        # nube (1 píxel/punto)
        cerrado = hull + hull[:1]
        ax.plot([p[0] for p in cerrado], [p[1] for p in cerrado],
                "-", color="#d1495b", linewidth=2)
        ax.plot([p[0] for p in hull], [p[1] for p in hull],
                "o", color="#d1495b", markersize=4)
        ax.set_title(f"{nombre}\n{tiempo:.3f} s · {len(hull)} vértices")
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])

    plt.tight_layout(rect=(0, 0, 1, 0.92))          # deja espacio para el título
    plt.savefig(archivo, dpi=110)
    print(f"  Gráfica guardada en: {archivo}")
    if matplotlib.get_backend().lower() != "agg":
        plt.show()


def _hay_pantalla():
    import os
    return sys.platform.startswith(("win", "darwin")) or bool(os.environ.get("DISPLAY"))

# =====================================================================
#  PRUEBA DE CORRECCIÓN (casos pequeños, con repetidos y colineales)
# =====================================================================
def prueba_correccion(casos=500):
    rnd = random.Random(1)
    for _ in range(casos):
        n = rnd.randint(1, 60)
        lim = rnd.choice([3, 5, 10, 100])           # rangos chicos → muchos colineales
        pts = [(rnd.randint(0, lim), rnd.randint(0, lim)) for _ in range(n)]
        ref = normalizar(monotone_chain(pts))
        for nombre, alg in ALGORITMOS.items():
            h = normalizar(alg(pts))
            if h != ref or not es_convexo_y_encierra(h, pts):
                print(f"✘ {nombre} falla con {pts}")
                return False
    print(f"✔ Prueba de corrección superada ({casos} casos aleatorios)")
    return True


# =====================================================================
#  PROGRAMA PRINCIPAL
# =====================================================================
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Simulación de Convex Hull")
    ap.add_argument("-n", type=int, default=1_000_000, help="cantidad de puntos")
    ap.add_argument("-s", "--semilla", type=int, default=42,
                    help="semilla aleatoria (misma semilla = mismos puntos)")
    ap.add_argument("--sin-grafica", action="store_true", help="no dibujar")
    ap.add_argument("--archivo", default="convex_hull.png", help="imagen de salida")
    ap.add_argument("--prueba", action="store_true",
                    help="solo ejecutar la prueba de corrección")
    args = ap.parse_args()

    if args.prueba:
        prueba_correccion()
    else:
        ejecutar(args.n, args.semilla,
                 not args.sin_grafica, args.archivo)
