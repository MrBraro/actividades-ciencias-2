"""
Representación computacional de grafos (TAD Grafo)
==================================================
Cuatro representaciones:
  1. Lista de adyacencias
  2. Lista de incidencias
  3. Matriz de adyacencias
  4. Matriz de incidencias

Todas comparten la misma interfaz y permiten AGREGAR, ELIMINAR y MODIFICAR
vértices y aristas. Los grafos son NO dirigidos y ponderados
(peso por defecto = 1). El peso 0 no se permite porque en las matrices
el 0 significa "no hay arista".
"""
from abc import ABC, abstractmethod


# =====================================================================
#  CLASE BASE (la abstracción / TAD)
# =====================================================================
class Grafo(ABC):
    nombre = "Grafo"

    # ---------------- operaciones que cada representación implementa
    @abstractmethod
    def vertices(self): ...

    @abstractmethod
    def aristas(self): ...                      # lista de tuplas (u, v, peso)

    @abstractmethod
    def agregar_vertice(self, v): ...

    @abstractmethod
    def eliminar_vertice(self, v): ...

    @abstractmethod
    def renombrar_vertice(self, viejo, nuevo): ...

    @abstractmethod
    def agregar_arista(self, u, v, peso=1): ...

    @abstractmethod
    def eliminar_arista(self, u, v): ...

    @abstractmethod
    def modificar_peso(self, u, v, peso): ...

    @abstractmethod
    def mostrar(self): ...

    # ---------------- operaciones comunes
    def existe_vertice(self, v):
        return v in self.vertices()

    def existe_arista(self, u, v):
        return any(self._misma(a, b, u, v) for a, b, _ in self.aristas())

    def peso(self, u, v):
        for a, b, p in self.aristas():
            if self._misma(a, b, u, v):
                return p
        raise ValueError(f"No existe la arista {self._txt(u, v)}")

    def modificar_arista(self, u, v, nuevo_u, nuevo_v):
        """Cambia los extremos de una arista conservando su peso."""
        p = self.peso(u, v)
        if self._misma(u, v, nuevo_u, nuevo_v):
            return
        self._validar_nueva_arista(nuevo_u, nuevo_v, p)
        self.eliminar_arista(u, v)
        self.agregar_arista(nuevo_u, nuevo_v, p)

    # ---------------- utilidades internas
    def _misma(self, a, b, u, v):
        """¿La arista (a,b) es la misma que (u,v)? El orden no importa."""
        return (a, b) == (u, v) or (a, b) == (v, u)

    def _txt(self, u, v):
        return f"{u}--{v}"

    def _validar_vertice(self, v):
        if not self.existe_vertice(v):
            raise ValueError(f"El vértice '{v}' no existe")

    def _validar_nuevo_vertice(self, v):
        if self.existe_vertice(v):
            raise ValueError(f"El vértice '{v}' ya existe")

    @staticmethod
    def _validar_peso(peso):
        if peso == 0:
            raise ValueError("El peso no puede ser 0 (en las matrices 0 = sin arista)")

    def _validar_nueva_arista(self, u, v, peso):
        self._validar_vertice(u)
        self._validar_vertice(v)
        self._validar_peso(peso)
        if self.existe_arista(u, v):
            raise ValueError(f"La arista {self._txt(u, v)} ya existe")

    def _encabezado(self):
        print(f"\n=== {self.nombre} ===")


def imprimir_tabla(filas, columnas, M):
    """Imprime una matriz con encabezados de filas y columnas alineados."""
    if not filas:
        print("  (grafo vacío)")
        return
    celdas = [str(x) for x in filas + columnas] + [str(c) for f in M for c in f]
    w = max(len(c) for c in celdas) + 2
    print(" " * w + "".join(str(c).rjust(w) for c in columnas))
    for nombre, fila in zip(filas, M):
        print(str(nombre).rjust(w) + "".join(str(c).rjust(w) for c in fila))


# =====================================================================
#  1. LISTA DE ADYACENCIAS
#     { vertice: { vecino: peso } }
# =====================================================================
class ListaAdyacencia(Grafo):
    nombre = "Lista de adyacencias"

    def __init__(self):
        self.ady = {}

    def vertices(self):
        return list(self.ady)

    def aristas(self):
        res, vistas = [], set()
        for u, vecinos in self.ady.items():
            for v, p in vecinos.items():
                clave = frozenset((u, v))
                if clave not in vistas:
                    vistas.add(clave)
                    res.append((u, v, p))
        return res

    def agregar_vertice(self, v):
        self._validar_nuevo_vertice(v)
        self.ady[v] = {}

    def eliminar_vertice(self, v):
        self._validar_vertice(v)
        del self.ady[v]
        for vecinos in self.ady.values():      # quitarlo de las listas de los demás
            vecinos.pop(v, None)

    def renombrar_vertice(self, viejo, nuevo):
        self._validar_vertice(viejo)
        self._validar_nuevo_vertice(nuevo)
        self.ady[nuevo] = self.ady.pop(viejo)
        for vecinos in self.ady.values():
            if viejo in vecinos:
                vecinos[nuevo] = vecinos.pop(viejo)

    def agregar_arista(self, u, v, peso=1):
        self._validar_nueva_arista(u, v, peso)
        self.ady[u][v] = peso
        self.ady[v][u] = peso

    def eliminar_arista(self, u, v):
        self.peso(u, v)                          # valida que exista
        del self.ady[u][v]
        if u != v:
            del self.ady[v][u]

    def modificar_peso(self, u, v, peso):
        self._validar_peso(peso)
        self.peso(u, v)
        self.ady[u][v] = peso
        self.ady[v][u] = peso

    def mostrar(self):
        self._encabezado()
        if not self.ady:
            print("  (grafo vacío)")
        for u, vecinos in self.ady.items():
            lista = ", ".join(f"{v}(p={p})" for v, p in vecinos.items()) or "∅"
            print(f"  {u} -> [{lista}]")


# =====================================================================
#  2. LISTA DE INCIDENCIAS
#     { vertice: [ids de aristas que inciden en él] }
#     { id_arista: [vertice1, vertice2, peso] }
# =====================================================================
class ListaIncidencia(Grafo):
    nombre = "Lista de incidencias"

    def __init__(self):
        self.inc = {}
        self.tabla = {}
        self._cont = 0

    def vertices(self):
        return list(self.inc)

    def aristas(self):
        return [tuple(a) for a in self.tabla.values()]

    def _id(self, u, v):
        for e, (a, b, _) in self.tabla.items():
            if self._misma(a, b, u, v):
                return e
        raise ValueError(f"No existe la arista {self._txt(u, v)}")

    def _quitar(self, e):
        u, v, _ = self.tabla.pop(e)
        self.inc[u].remove(e)
        if v != u:
            self.inc[v].remove(e)

    def agregar_vertice(self, v):
        self._validar_nuevo_vertice(v)
        self.inc[v] = []

    def eliminar_vertice(self, v):
        self._validar_vertice(v)
        for e in list(self.inc[v]):             # primero sus aristas incidentes
            self._quitar(e)
        del self.inc[v]

    def renombrar_vertice(self, viejo, nuevo):
        self._validar_vertice(viejo)
        self._validar_nuevo_vertice(nuevo)
        self.inc[nuevo] = self.inc.pop(viejo)
        for arista in self.tabla.values():
            if arista[0] == viejo:
                arista[0] = nuevo
            if arista[1] == viejo:
                arista[1] = nuevo

    def agregar_arista(self, u, v, peso=1):
        self._validar_nueva_arista(u, v, peso)
        self._cont += 1
        e = f"e{self._cont}"
        self.tabla[e] = [u, v, peso]
        self.inc[u].append(e)
        if v != u:
            self.inc[v].append(e)

    def eliminar_arista(self, u, v):
        self._quitar(self._id(u, v))

    def modificar_peso(self, u, v, peso):
        self._validar_peso(peso)
        self.tabla[self._id(u, v)][2] = peso

    def mostrar(self):
        self._encabezado()
        if not self.inc:
            print("  (grafo vacío)")
        for v, ids in self.inc.items():
            print(f"  {v} -> [{', '.join(ids) or '∅'}]")
        if self.tabla:
            print("  Aristas:")
            for e, (a, b, p) in self.tabla.items():
                print(f"    {e}: {self._txt(a, b)}  (p={p})")


# =====================================================================
#  3. MATRIZ DE ADYACENCIAS   (n x n)
#     M[i][j] = M[j][i] = peso si hay arista i--j, 0 si no (simétrica)
# =====================================================================
class MatrizAdyacencia(Grafo):
    nombre = "Matriz de adyacencias"

    def __init__(self):
        self.nombres = []
        self.M = []

    def vertices(self):
        return list(self.nombres)

    def _i(self, v):
        self._validar_vertice(v)
        return self.nombres.index(v)

    def aristas(self):
        res, n = [], len(self.nombres)
        for i in range(n):
            # matriz simétrica: solo triángulo superior (incluida la diagonal)
            for j in range(i, n):
                if self.M[i][j] != 0:
                    res.append((self.nombres[i], self.nombres[j], self.M[i][j]))
        return res

    def agregar_vertice(self, v):
        self._validar_nuevo_vertice(v)
        self.nombres.append(v)
        for fila in self.M:                     # nueva columna
            fila.append(0)
        self.M.append([0] * len(self.nombres))  # nueva fila

    def eliminar_vertice(self, v):
        i = self._i(v)
        self.nombres.pop(i)
        self.M.pop(i)                           # quitar fila
        for fila in self.M:                     # quitar columna
            fila.pop(i)

    def renombrar_vertice(self, viejo, nuevo):
        i = self._i(viejo)
        self._validar_nuevo_vertice(nuevo)
        self.nombres[i] = nuevo

    def agregar_arista(self, u, v, peso=1):
        self._validar_nueva_arista(u, v, peso)
        i, j = self._i(u), self._i(v)
        self.M[i][j] = peso
        self.M[j][i] = peso

    def eliminar_arista(self, u, v):
        self.peso(u, v)
        i, j = self._i(u), self._i(v)
        self.M[i][j] = 0
        self.M[j][i] = 0

    def modificar_peso(self, u, v, peso):
        self._validar_peso(peso)
        self.peso(u, v)
        i, j = self._i(u), self._i(v)
        self.M[i][j] = peso
        self.M[j][i] = peso

    def mostrar(self):
        self._encabezado()
        imprimir_tabla(self.nombres, self.nombres, self.M)


# =====================================================================
#  4. MATRIZ DE INCIDENCIAS   (n vértices x m aristas)
#     1 en ambos extremos de la arista.
#     Lazo: 2.
#     Los pesos se guardan aparte (un peso por columna).
# =====================================================================
class MatrizIncidencia(Grafo):
    nombre = "Matriz de incidencias"

    def __init__(self):
        self.nombres = []       # filas
        self.ids = []           # columnas
        self.pesos = []
        self.M = []
        self._cont = 0

    def vertices(self):
        return list(self.nombres)

    def _i(self, v):
        self._validar_vertice(v)
        return self.nombres.index(v)

    def _extremos(self, j):
        """Reconstruye los extremos de la arista leyendo la columna j."""
        filas = [(i, self.M[i][j]) for i in range(len(self.nombres)) if self.M[i][j] != 0]
        if len(filas) == 1:                     # lazo
            v = self.nombres[filas[0][0]]
            return v, v
        (i1, _), (i2, _) = filas
        return self.nombres[i1], self.nombres[i2]

    def aristas(self):
        return [(*self._extremos(j), self.pesos[j]) for j in range(len(self.ids))]

    def _col(self, u, v):
        for j in range(len(self.ids)):
            if self._misma(*self._extremos(j), u, v):
                return j
        raise ValueError(f"No existe la arista {self._txt(u, v)}")

    def _quitar_col(self, j):
        self.ids.pop(j)
        self.pesos.pop(j)
        for fila in self.M:
            fila.pop(j)

    def agregar_vertice(self, v):
        self._validar_nuevo_vertice(v)
        self.nombres.append(v)
        self.M.append([0] * len(self.ids))

    def eliminar_vertice(self, v):
        i = self._i(v)
        cols = [j for j, x in enumerate(self.M[i]) if x != 0]
        for j in reversed(cols):                # quitar sus aristas (columnas)
            self._quitar_col(j)
        self.nombres.pop(i)
        self.M.pop(i)

    def renombrar_vertice(self, viejo, nuevo):
        i = self._i(viejo)
        self._validar_nuevo_vertice(nuevo)
        self.nombres[i] = nuevo

    def agregar_arista(self, u, v, peso=1):
        self._validar_nueva_arista(u, v, peso)
        self._cont += 1
        self.ids.append(f"e{self._cont}")
        self.pesos.append(peso)
        for fila in self.M:                     # nueva columna
            fila.append(0)
        i, k = self._i(u), self._i(v)
        if i == k:
            self.M[i][-1] = 2
        else:
            self.M[i][-1] = 1
            self.M[k][-1] = 1

    def eliminar_arista(self, u, v):
        self._quitar_col(self._col(u, v))

    def modificar_peso(self, u, v, peso):
        self._validar_peso(peso)
        self.pesos[self._col(u, v)] = peso

    def mostrar(self):
        self._encabezado()
        imprimir_tabla(self.nombres, self.ids, self.M)
        if self.ids:
            print("  Pesos: " + ", ".join(f"{e}={p}" for e, p in zip(self.ids, self.pesos)))


# =====================================================================
#  UTILIDADES
# =====================================================================
REPRESENTACIONES = {
    "1": ListaAdyacencia,
    "2": ListaIncidencia,
    "3": MatrizAdyacencia,
    "4": MatrizIncidencia,
}


def convertir(grafo, Clase):
    """Pasa un grafo de una representación a otra usando solo la interfaz común."""
    nuevo = Clase()
    for v in grafo.vertices():
        nuevo.agregar_vertice(v)
    for u, v, p in grafo.aristas():
        nuevo.agregar_arista(u, v, p)
    return nuevo


def cargar_ejemplo(Clase):
    g = Clase()
    for v in "ABCD":
        g.agregar_vertice(v)
    for u, v, p in [("A", "B", 4), ("A", "C", 2), ("B", "C", 5), ("C", "D", 1), ("D", "D", 3)]:
        g.agregar_arista(u, v, p)
    return g


# =====================================================================
#  ALGORITMOS DE CAMINOS MÁS CORTOS — FUNCIONES COMPARTIDAS
#  Los algoritmos usan solo vertices() y aristas(), así que funcionan
#  con las 4 representaciones sin cambiar nada.
# =====================================================================
INF = float("inf")


def vecinos_de(grafo):
    """Arma {vértice: [(vecino, peso), ...]} a partir de las aristas (no dirigido)."""
    vec = {v: [] for v in grafo.vertices()}
    for u, v, p in grafo.aristas():
        vec[u].append((v, p))
        if u != v:
            vec[v].append((u, p))
    return vec


def reconstruir_camino(previo, origen, destino):
    """Recorre 'previo' desde el destino hacia atrás hasta llegar al origen."""
    if destino != origen and previo[destino] is None:
        return []                                   # no hay camino
    camino, actual = [], destino
    while actual is not None:
        camino.append(actual)
        actual = previo[actual]
    return camino[::-1]


def formato(x):
    return "∞" if x == INF else str(x)


def mostrar_resultado(nombre, origen, dist, previo):
    print(f"\n=== {nombre} desde {origen} ===")
    print(f"  {'Destino':<10}{'Distancia':<12}Camino")
    for v in dist:
        camino = reconstruir_camino(previo, origen, v)
        txt = " -> ".join(camino) if camino else "sin camino"
        print(f"  {v:<10}{formato(dist[v]):<12}{txt}")


# #####################################################################
# #####################################################################
#  ALGORITMO 1: DIJKSTRA
#  - Desde UN origen hacia todos los vértices.
#  - Voraz: en cada paso fija el vértice no visitado más cercano.
#  - NO admite pesos negativos.
# #####################################################################
# #####################################################################
def dijkstra(grafo, origen, mostrar_pasos=False):
    """
    Distancias más cortas desde 'origen' a todos los vértices.
    Devuelve (dist, previo):
      dist[v]   = distancia mínima de origen a v (INF si es inalcanzable)
      previo[v] = vértice anterior a v en el camino más corto
    """
    grafo._validar_vertice(origen)
    if any(p < 0 for _, _, p in grafo.aristas()):
        raise ValueError("Dijkstra no admite pesos negativos")

    vec = vecinos_de(grafo)
    dist = {v: INF for v in vec}
    previo = {v: None for v in vec}
    visitado = set()
    dist[origen] = 0
    paso = 0

    while len(visitado) < len(vec):
        # 1. Elegir el vértice NO visitado con menor distancia (paso voraz)
        u = min((v for v in vec if v not in visitado), key=lambda v: dist[v])
        if dist[u] == INF:                          # los que quedan son inalcanzables
            break
        visitado.add(u)                             # su distancia queda definitiva
        paso += 1
        cambios = []

        # 2. Relajar las aristas de u: ¿llegar al vecino pasando por u es más corto?
        for v, p in vec[u]:
            if v not in visitado and dist[u] + p < dist[v]:
                dist[v] = dist[u] + p
                previo[v] = u
                cambios.append(f"{v}={formato(dist[v])}")

        if mostrar_pasos:
            print(f"  Paso {paso}: se fija {u} (dist={formato(dist[u])})"
                  f"  → actualiza: {', '.join(cambios) or 'nada'}")
    return dist, previo
# ---------------------------- FIN DIJKSTRA ----------------------------


# #####################################################################
# #####################################################################
#  ALGORITMO 2: BELLMAN-FORD
#  - Desde UN origen hacia todos los vértices.
#  - Relaja TODAS las aristas, V-1 veces (V = número de vértices).
#  - Admite pesos negativos y DETECTA ciclos negativos.
#  - Ojo: en un grafo no dirigido, cualquier arista negativa alcanzable
#    ya es un ciclo negativo (se puede ir y volver por ella: A-B-A...).
# #####################################################################
# #####################################################################
def bellman_ford(grafo, origen, mostrar_pasos=False):
    """
    Distancias más cortas desde 'origen' a todos los vértices.
    Devuelve (dist, previo), igual que Dijkstra.
    Lanza ValueError si encuentra un ciclo negativo alcanzable.
    """
    grafo._validar_vertice(origen)

    vertices = grafo.vertices()
    # Como el grafo es no dirigido, cada arista u--v se revisa en los dos sentidos
    aristas = []
    for u, v, p in grafo.aristas():
        aristas.append((u, v, p))
        if u != v:
            aristas.append((v, u, p))

    dist = {v: INF for v in vertices}
    previo = {v: None for v in vertices}
    dist[origen] = 0

    # 1. Repetir V-1 veces: relajar todas las aristas
    for ronda in range(1, len(vertices)):
        cambios = []
        for u, v, p in aristas:
            if dist[u] != INF and dist[u] + p < dist[v]:
                dist[v] = dist[u] + p
                previo[v] = u
                cambios.append(f"{v}={formato(dist[v])} (vía {u})")

        if mostrar_pasos:
            print(f"  Ronda {ronda}: actualiza: {', '.join(cambios) or 'nada'}")
        if not cambios:                             # nada cambió: ya terminó
            if mostrar_pasos:
                print("  Sin cambios en esta ronda → se detiene antes")
            break

    # 2. Una ronda más: si algo aún mejora, hay un ciclo negativo
    for u, v, p in aristas:
        if dist[u] != INF and dist[u] + p < dist[v]:
            raise ValueError(
                f"Se detectó un ciclo negativo alcanzable desde {origen}: las "
                "distancias pueden bajar indefinidamente, así que no existe "
                "camino más corto.")
    return dist, previo
# -------------------------- FIN BELLMAN-FORD --------------------------


# #####################################################################
# #####################################################################
#  ALGORITMO 3: FLOYD-WARSHALL
#  - Entre TODOS los pares de vértices (no necesita origen).
#  - Programación dinámica sobre una matriz de distancias:
#      para cada vértice intermedio k, para cada par (i, j):
#      dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
#  - Admite pesos negativos y DETECTA ciclos negativos
#    (si al final algún dist[i][i] < 0).
# #####################################################################
# #####################################################################
def floyd_warshall(grafo, mostrar_pasos=False):
    """
    Distancias más cortas entre todos los pares de vértices.
    Devuelve (nombres, dist, sig):
      nombres    = lista de vértices (orden de filas y columnas)
      dist[i][j] = distancia mínima de nombres[i] a nombres[j]
      sig[i][j]  = índice del siguiente vértice en el camino de i a j
    Lanza ValueError si hay un ciclo negativo.
    """
    nombres = grafo.vertices()
    n = len(nombres)
    pos = {v: i for i, v in enumerate(nombres)}

    # 1. Matriz inicial: 0 en la diagonal, peso si hay arista, ∞ si no
    dist = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    sig = [[j if i == j else None for j in range(n)] for i in range(n)]
    for u, v, p in grafo.aristas():
        i, j = pos[u], pos[v]
        if i == j:                                  # lazo: solo importa si es negativo
            dist[i][i] = min(dist[i][i], p)
        else:                                       # no dirigido: simétrica
            dist[i][j] = dist[j][i] = p
            sig[i][j], sig[j][i] = j, i

    if mostrar_pasos:
        print("\n  Matriz inicial (D0):")
        imprimir_tabla(nombres, nombres, [[formato(x) for x in f] for f in dist])

    # 2. Probar cada vértice k como intermedio
    for k in range(n):
        cambios = []
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    sig[i][j] = sig[i][k]
                    cambios.append(f"{nombres[i]}-{nombres[j]}={formato(dist[i][j])}")

        if mostrar_pasos:
            print(f"\n  k = {nombres[k]} (D{k + 1}): "
                  f"actualiza: {', '.join(cambios) or 'nada'}")
            imprimir_tabla(nombres, nombres, [[formato(x) for x in f] for f in dist])

    # 3. Un valor negativo en la diagonal indica un ciclo negativo
    for i in range(n):
        if dist[i][i] < 0:
            raise ValueError(
                f"Se detectó un ciclo negativo (pasa por {nombres[i]}): las "
                "distancias pueden bajar indefinidamente, así que no existe "
                "camino más corto.")
    return nombres, dist, sig


def camino_floyd(nombres, sig, i, j):
    """Sigue la matriz 'sig' desde i hasta j para armar el camino."""
    if sig[i][j] is None:
        return []                                   # no hay camino
    camino = [nombres[i]]
    while i != j:
        i = sig[i][j]
        camino.append(nombres[i])
    return camino


def mostrar_floyd(nombres, dist, sig):
    print("\n=== Floyd-Warshall: matriz de distancias ===")
    imprimir_tabla(nombres, nombres, [[formato(x) for x in f] for f in dist])
    print("\n  Caminos más cortos:")
    n = len(nombres)
    for i in range(n):
        for j in range(i + 1, n):                   # no dirigido: basta con i < j
            camino = camino_floyd(nombres, sig, i, j)
            txt = " -> ".join(camino) if camino else "sin camino"
            print(f"    {nombres[i]}--{nombres[j]}: {formato(dist[i][j]):<5} {txt}")
# ------------------------- FIN FLOYD-WARSHALL -------------------------


def leer(msg):
    txt = input(msg).strip()
    if not txt:
        raise ValueError("El valor no puede estar vacío")
    return txt


def leer_peso(msg="Peso (Enter = 1): "):
    txt = input(msg).strip()
    if not txt:
        return 1
    try:
        n = float(txt)
    except ValueError:
        raise ValueError("El peso debe ser numérico")
    return int(n) if n.is_integer() else n


# =====================================================================
#  MENÚ INTERACTIVO
# =====================================================================
MENU = """
------- MENÚ: {nombre} -------
  1. Agregar vértice
  2. Eliminar vértice
  3. Modificar (renombrar) vértice
  4. Agregar arista
  5. Eliminar arista
  6. Modificar peso de una arista
  7. Modificar extremos de una arista
  8. Mostrar grafo
  9. Mostrar en las 4 representaciones
 10. Cambiar de representación (conserva los datos)
 11. Cargar grafo de ejemplo
 12. Dijkstra (camino más corto desde un vértice)
 13. Bellman-Ford (camino más corto, admite pesos negativos)
 14. Floyd-Warshall (caminos más cortos entre todos los pares)
  0. Salir"""


def elegir_representacion():
    print("\nRepresentaciones disponibles:")
    for k, C in REPRESENTACIONES.items():
        print(f"  {k}. {C.nombre}")
    op = input("Elija una (1-4): ").strip()
    while op not in REPRESENTACIONES:
        op = input("Opción inválida, elija 1-4: ").strip()
    return REPRESENTACIONES[op]


def menu():
    print("=== REPRESENTACIÓN COMPUTACIONAL DE GRAFOS ===")
    g = elegir_representacion()()

    while True:
        print(MENU.format(nombre=g.nombre))
        op = input("Opción: ").strip()
        try:
            if op == "1":
                g.agregar_vertice(leer("Nombre del vértice: "))
                print("✔ Vértice agregado")
            elif op == "2":
                g.eliminar_vertice(leer("Vértice a eliminar: "))
                print("✔ Vértice y sus aristas eliminados")
            elif op == "3":
                g.renombrar_vertice(leer("Nombre actual: "), leer("Nuevo nombre: "))
                print("✔ Vértice modificado")
            elif op == "4":
                u, v = leer("Vértice 1: "), leer("Vértice 2: ")
                g.agregar_arista(u, v, leer_peso())
                print("✔ Arista agregada")
            elif op == "5":
                g.eliminar_arista(leer("Vértice 1: "), leer("Vértice 2: "))
                print("✔ Arista eliminada")
            elif op == "6":
                u, v = leer("Vértice 1: "), leer("Vértice 2: ")
                g.modificar_peso(u, v, leer_peso("Nuevo peso: "))
                print("✔ Peso modificado")
            elif op == "7":
                u, v = leer("Vértice 1 actual: "), leer("Vértice 2 actual: ")
                g.modificar_arista(u, v, leer("Nuevo vértice 1: "), leer("Nuevo vértice 2: "))
                print("✔ Arista modificada")
            elif op == "8":
                g.mostrar()
            elif op == "9":
                for C in REPRESENTACIONES.values():
                    convertir(g, C).mostrar()
            elif op == "10":
                g = convertir(g, elegir_representacion())
                print(f"✔ Ahora se usa: {g.nombre}")
            elif op == "11":
                g = cargar_ejemplo(type(g))
                print("✔ Ejemplo cargado (A, B, C, D)")
                g.mostrar()
            elif op == "12":
                origen = leer("Vértice origen: ")
                pasos = input("¿Mostrar paso a paso? (s/n): ").strip().lower() == "s"
                dist, previo = dijkstra(g, origen, pasos)
                mostrar_resultado("Dijkstra", origen, dist, previo)
            elif op == "13":
                origen = leer("Vértice origen: ")
                pasos = input("¿Mostrar paso a paso? (s/n): ").strip().lower() == "s"
                dist, previo = bellman_ford(g, origen, pasos)
                mostrar_resultado("Bellman-Ford", origen, dist, previo)
            elif op == "14":
                pasos = input("¿Mostrar paso a paso? (s/n): ").strip().lower() == "s"
                mostrar_floyd(*floyd_warshall(g, pasos))
            elif op == "0":
                print("¡Hasta luego!")
                break
            else:
                print("Opción no válida")
        except ValueError as e:
            print(f"✘ Error: {e}")


if __name__ == "__main__":
    menu()