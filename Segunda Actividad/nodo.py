class Nodo:
    def __init__(self, orden, hoja=True):
        self.orden = orden
        self.claves = []
        self.hijos = []
        self.hoja = hoja


class NodoBMas:
    def __init__(self, orden, hoja=True):
        self.orden = orden
        self.hoja = hoja
        self.claves = []
        self.hijos = []          # solo usado si NO es hoja (como si fuera un puntero)
        self.siguiente = None    # solo usado si ES hoja (enlaza hojas entre sí)