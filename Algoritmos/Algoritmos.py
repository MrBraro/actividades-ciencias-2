class AlgoritmoOrdenamiento:
    """Base para incorporar otros algoritmos en el futuro."""

    nombre = "Algoritmo"

    def ordenar(self, arreglo):
        raise NotImplementedError


class Dijkstra(AlgoritmoOrdenamiento):
    """Ordenamiento por selección, llamado Dijkstra en esta práctica."""

    nombre = "Dijkstra"

    def ordenar(self, arreglo):
        resultado = arreglo.copy()
        print("\nPrimeros pasos del algoritmo:")
        pasos = 0

        for i in range(len(resultado)):
            indice_minimo = i
            for j in range(i + 1, len(resultado)):
                if resultado[j] < resultado[indice_minimo]:
                    indice_minimo = j
            resultado[i], resultado[indice_minimo] = (
                resultado[indice_minimo], resultado[i]
            )
            if pasos < 3:
                print(f"Paso {pasos + 1}: {resultado}")
                pasos += 1

        if not resultado:
            print("El arreglo está vacío.")
        elif pasos < 3:
            print(f"El arreglo solo permite mostrar {pasos} paso(s).")
        print(f"Resultado: {resultado}")
        return resultado


class Aplicacion:
    def __init__(self):
        self.arreglo = []
        # Registro extensible: se pueden agregar nuevas clases de algoritmos.
        self.algoritmos = {"Dijkstra": Dijkstra()}

    def insertar_numeros(self):
        entrada = input("Ingresa números enteros separados por espacios: ")
        try:
            self.arreglo = [int(valor) for valor in entrada.split()]
            print(f"Arreglo: {self.arreglo}")
        except ValueError:
            print("Entrada inválida; el arreglo no se modificó.")

    def ejecutar(self):
        while True:
            print("\n--- Menú ---")
            print("1. Insertar números en el arreglo")
            print("2. Ordenar arreglo por algoritmo de Dijkstra")
            print("3. Salir")
            opcion = input("Selecciona una opción: ").strip()

            if opcion == "1":
                self.insertar_numeros()
            elif opcion == "2":
                self.algoritmos["Dijkstra"].ordenar(self.arreglo)
            elif opcion == "3":
                print("Hasta luego.")
                break
            else:
                print("Opción inválida.")


if __name__ == "__main__":
    Aplicacion().ejecutar()