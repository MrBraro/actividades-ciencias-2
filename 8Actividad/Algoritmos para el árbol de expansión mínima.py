import time
import random

class Grafo:
    """Grafo no dirigido ponderado mediante lista de adyacencia."""

    def __init__(self):
        self.ady = {}

    def agregar_vertice(self, v):
        if not v:
            raise ValueError("El nombre del vértice no puede estar vacío.")
        if v in self.ady:
            raise ValueError(f"El vértice '{v}' ya existe.")
        self.ady[v] = {}

    def eliminar_vertice(self, v):
        if v not in self.ady:
            raise ValueError(f"El vértice '{v}' no existe.")
        del self.ady[v]
        for vecinos in self.ady.values():
            vecinos.pop(v, None)

    def agregar_arista(self, u, v, peso):
        if u not in self.ady or v not in self.ady:
            raise ValueError("Ambos vértices deben existir.")
        if u == v:
            raise ValueError("No se permiten aristas de un vértice a sí mismo.")
        if v in self.ady[u]:
            raise ValueError(f"La arista {u}--{v} ya existe.")
        self.ady[u][v] = peso
        self.ady[v][u] = peso

    def aristas(self):
        resultado = []
        for u, vecinos in self.ady.items():
            for v, peso in vecinos.items():
                if u < v:
                    resultado.append((u, v, peso))
        return resultado

    def mostrar(self):
        if not self.ady:
            print("  (grafo vacío)")
        for u, vecinos in self.ady.items():
            lista = ", ".join(f"{v}(peso={p:g})" for v, p in vecinos.items()) or "∅"
            print(f"  {u} -> [{lista}]")


def validar_conexo(grafo):
    if not grafo.ady:
        raise ValueError("El grafo no tiene vértices.")
    inicio = next(iter(grafo.ady))
    visitados = {inicio}
    pendientes = [inicio]
    while pendientes:
        u = pendientes.pop()
        for v in grafo.ady[u]:
            if v not in visitados:
                visitados.add(v)
                pendientes.append(v)
    if len(visitados) != len(grafo.ady):
        raise ValueError("El grafo no está conectado; no tiene árbol de expansión.")


def prim(grafo):
    validar_conexo(grafo)
    inicio = next(iter(grafo.ady))
    visitados = {inicio}
    arbol = []
    pasos = [f"Comenzar en el vértice {inicio}."]
    while len(visitados) < len(grafo.ady):
        candidatas = [
            (peso, u, v) for u in visitados
            for v, peso in grafo.ady[u].items() if v not in visitados
        ]
        peso, u, v = min(candidatas)
        arbol.append((u, v, peso))
        visitados.add(v)
        pasos.append(f"Elegir {u}--{v}, peso {peso:g}; añadir {v} al árbol.")
    return arbol, pasos


def kruskal(grafo):
    validar_conexo(grafo)
    padre = {v: v for v in grafo.ady}
    rango = {v: 0 for v in grafo.ady}

    def buscar(v):
        if padre[v] != v:
            padre[v] = buscar(padre[v])
        return padre[v]

    def unir(a, b):
        ra, rb = buscar(a), buscar(b)
        if ra == rb:
            return False
        if rango[ra] < rango[rb]:
            ra, rb = rb, ra
        padre[rb] = ra
        if rango[ra] == rango[rb]:
            rango[ra] += 1
        return True

    arbol, pasos = [], []
    for u, v, peso in sorted(grafo.aristas(), key=lambda e: (e[2], e[0], e[1])):
        if unir(u, v):
            arbol.append((u, v, peso))
            pasos.append(f"Aceptar {u}--{v}, peso {peso:g}; no forma un ciclo.")
        else:
            pasos.append(f"Descartar {u}--{v}, peso {peso:g}; formaría un ciclo.")
        if len(arbol) == len(grafo.ady) - 1:
            break
    return arbol, pasos


def mostrar_resultado(nombre, resultado):
    arbol, pasos = resultado
    print(f"\nPrimeros {min(6, len(pasos))} pasos de {nombre}:")
    for i, paso in enumerate(pasos[:6], 1):
        print(f"  {i}. {paso}")
    print("Árbol de expansión mínima:")
    for u, v, peso in arbol:
        print(f"  {u} -- {v} (peso {peso:g})")
    print(f"Peso total: {sum(p for _, _, p in arbol):g}")


def cargar_ejemplo():
    g = Grafo()
    for v in "ABCDEF":
        g.agregar_vertice(v)
    for u, v, peso in (
        ("A", "B", 4), ("A", "C", 2), ("B", "C", 1),
        ("B", "D", 5), ("C", "D", 8), ("C", "E", 10),
        ("D", "E", 2), ("D", "F", 6), ("E", "F", 3),
    ):
        g.agregar_arista(u, v, peso)
    return g

def cargar_grafo_esparcido():
    g = Grafo()
    # Grafo tipo línea (N nodos, N-1 aristas)
    nodos = "ABCDEFGH"
    for v in nodos:
        g.agregar_vertice(v)
    for i in range(len(nodos) - 1):
        peso = random.randint(1, 15)
        g.agregar_arista(nodos[i], nodos[i+1], peso)
    return g

def cargar_grafo_denso():
    g = Grafo()
    # Grafo completo (Todos conectados con todos)
    nodos = "ABCDEF"
    for v in nodos:
        g.agregar_vertice(v)
    
    for i in range(len(nodos)):
        for j in range(i + 1, len(nodos)):
            peso = random.randint(1, 20)
            g.agregar_arista(nodos[i], nodos[j], peso)
    return g

def comparar_resultados(grafo):
    try:
        validar_conexo(grafo)
    except ValueError as error:
        print(f"Error: {error}")
        return

    # Medición de Prim
    t_inicio = time.perf_counter()
    r_prim, _ = prim(grafo)
    t_fin = time.perf_counter()
    t_prim = (t_fin - t_inicio) * 1000

    # Medición de Kruskal
    t_inicio = time.perf_counter()
    r_kruskal, _ = kruskal(grafo)
    t_fin = time.perf_counter()
    t_kruskal = (t_fin - t_inicio) * 1000

    # Costos
    peso_prim = sum(p for _, _, p in r_prim)
    peso_kruskal = sum(p for _, _, p in r_kruskal)
    coincide_costo = "Sí (Correcto)" if peso_prim == peso_kruskal else "No (Diferente)"

    # Formateo de aristas
    str_aristas_prim = ", ".join(f"{u}-{v}" for u, v, _ in r_prim)
    str_aristas_kruskal = ", ".join(f"{u}-{v}" for u, v, _ in r_kruskal)
    
    # Truncar las aristas si la cadena es muy larga para mantener el formato de tabla
    if len(str_aristas_prim) > 27: str_aristas_prim = str_aristas_prim[:24] + "..."
    if len(str_aristas_kruskal) > 27: str_aristas_kruskal = str_aristas_kruskal[:24] + "..."

    # Comparación estructural de subgrafos (sin importar el orden o dirección de u, v)
    set_prim = {frozenset([u, v]) for u, v, _ in r_prim}
    set_kruskal = {frozenset([u, v]) for u, v, _ in r_kruskal}
    coincide_aristas = "Sí (Mismo subgrafo)" if set_prim == set_kruskal else "No (Diferente)"

    # Impresión de Tabla
    print(f"\n{'-'*95}")
    print(f"{'Métrica':<25} | {'Algoritmo de Prim':<25} | {'Algoritmo de Kruskal':<22} | {'¿Coinciden?':<15}")
    print(f"{'-'*95}")
    print(f"{'Costo Total del MST':<25} | {peso_prim:<25} | {peso_kruskal:<22} | {coincide_costo:<15}")
    print(f"{'Tiempo de Ejecución':<25} | {t_prim:.4f} ms{'':<17} | {t_kruskal:.4f} ms{'':<14} | N/A")
    print(f"{'Aristas elegidas':<25} | {str_aristas_prim:<25} | {str_aristas_kruskal:<22} | {coincide_aristas:<15}")
    print(f"{'-'*95}\n")


def menu():
    grafo = Grafo()
    while True:
        print("\n=== ÁRBOL DE EXPANSIÓN MÍNIMA ===")
        print("1. Cargar grafo ejemplo (General)")
        print("2. Cargar grafo 'Línea' o 'Esparcido'")
        print("3. Cargar grafo 'Completo' o 'Denso'")
        print("4. Crear vértice")
        print("5. Eliminar vértice")
        print("6. Crear arista")
        print("7. Hallar árbol mínimo por Prim")
        print("8. Hallar árbol mínimo por Kruskal")
        print("9. Comparar resultados en Tabla")
        print("10. Mostrar grafo")
        print("0. Salir")
        opcion = input("Opción: ").strip()
        
        try:
            if opcion == "1":
                grafo = cargar_ejemplo()
                print("Grafo de ejemplo cargado:")
                grafo.mostrar()
            elif opcion == "2":
                grafo = cargar_grafo_esparcido()
                print("Grafo esparcido (Línea) cargado:")
                grafo.mostrar()
            elif opcion == "3":
                grafo = cargar_grafo_denso()
                print("Grafo denso (Completo) cargado:")
                grafo.mostrar()
            elif opcion == "4":
                v = input("Nombre del vértice: ").strip()
                grafo.agregar_vertice(v)
                print("Vértice creado.")
            elif opcion == "5":
                grafo.eliminar_vertice(input("Vértice a eliminar: ").strip())
                print("Vértice eliminado junto con sus aristas.")
            elif opcion == "6":
                u = input("Primer vértice: ").strip()
                v = input("Segundo vértice: ").strip()
                peso = float(input("Peso: "))
                grafo.agregar_arista(u, v, peso)
                print("Arista creada.")
            elif opcion == "7":
                mostrar_resultado("Prim", prim(grafo))
            elif opcion == "8":
                mostrar_resultado("Kruskal", kruskal(grafo))
            elif opcion == "9":
                comparar_resultados(grafo)
            elif opcion == "10":
                grafo.mostrar()
            elif opcion == "0":
                break
            else:
                print("Opción no válida.")
        except (ValueError, OverflowError) as error:
            print(f"Error: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\nHasta luego.")
            break

if __name__ == "__main__":
    menu()