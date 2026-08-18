# main.py
from arbol import ArbolB
from arbol import ArbolBMas


def mostrar_arbol(arbol):
    if arbol.raiz is None or len(arbol.raiz.claves) == 0:
        print("(árbol vacío)")
        return

    nivel_actual = [arbol.raiz]
    nivel = 0

    while nivel_actual:
        print(f"Nivel {nivel}: ", end="")
        siguiente_nivel = []

        for nodo in nivel_actual:
            print(nodo.claves, end="  ")
            if not nodo.hoja:
                siguiente_nivel.extend(nodo.hijos)

        print()
        nivel_actual = siguiente_nivel
        nivel += 1


def mostrar_hojas_enlazadas(arbol):
    nodo = arbol.raiz
    while not nodo.hoja:
        nodo = nodo.hijos[0]

    print("Hojas enlazadas: ", end="")
    while nodo is not None:
        print(nodo.claves, end=" -> ")
        nodo = nodo.siguiente
    print("None")


def pedir_entero(mensaje):
    while True:
        entrada = input(mensaje)
        try:
            return int(entrada)
        except ValueError:
            print("Por favor ingresa un número entero válido.")


def menu_arbol_b():
    orden = pedir_entero("Ingresa el orden (m) del árbol: ")
    arbol = ArbolB(orden)

    while True:
        print("\n--- Menú Árbol B ---")
        print("1. Insertar clave")
        print("2. Eliminar clave")
        print("3. Mostrar árbol")
        print("4. Volver")
        opcion = input("Elige una opción: ")

        if opcion == "1":
            clave = pedir_entero("Ingresa la clave a insertar: ")
            arbol.insertar(clave)
            print(f"Clave {clave} insertada.")

        elif opcion == "2":
            clave = pedir_entero("Ingresa la clave a eliminar: ")
            arbol.eliminar(clave)
            print(f"Clave {clave} eliminada (si existía).")

        elif opcion == "3":
            mostrar_arbol(arbol)

        elif opcion == "4":
            break

        else:
            print("Opción inválida, intenta de nuevo.")


def menu_arbol_bmas():
    orden = pedir_entero("Ingresa el orden (m) del árbol: ")
    arbol = ArbolBMas(orden)

    while True:
        print("\n--- Menú Árbol B+ ---")
        print("1. Insertar clave")
        print("2. Eliminar clave")
        print("3. Mostrar árbol")
        print("4. Mostrar hojas enlazadas")
        print("5. Volver")
        opcion = input("Elige una opción: ")

        if opcion == "1":
            clave = pedir_entero("Ingresa la clave a insertar: ")
            arbol.insertar(clave)
            print(f"Clave {clave} insertada.")

        elif opcion == "2":
            clave = pedir_entero("Ingresa la clave a eliminar: ")
            arbol.eliminar(clave)
            print(f"Clave {clave} eliminada (si existía).")

        elif opcion == "3":
            mostrar_arbol(arbol)

        elif opcion == "4":
            mostrar_hojas_enlazadas(arbol)

        elif opcion == "5":
            break

        else:
            print("Opción inválida, intenta de nuevo.")


def menu():
    while True:
        print("\n=== Prueba de Árboles ===")
        print("1. Árbol B")
        print("2. Árbol B+")
        print("3. Salir")
        opcion = input("Elige una opción: ")

        if opcion == "1":
            menu_arbol_b()

        elif opcion == "2":
            menu_arbol_bmas()

        elif opcion == "3":
            print("Saliendo...")
            break

        else:
            print("Opción inválida, intenta de nuevo.")


if __name__ == "__main__":
    menu()