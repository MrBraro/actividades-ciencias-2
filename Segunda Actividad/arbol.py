import math
from nodo import Nodo

class ArbolB:
    def __init__(self, orden):
        self.orden = orden
        self.raiz = Nodo(orden, True)

    def insertar(self, clave):
        self._insertar_recursivo(self.raiz, clave)

        m = self.orden
        if len(self.raiz.claves) == m:
            nueva_raiz = Nodo(m, hoja=False)
            nueva_raiz.hijos.append(self.raiz)
            self.raiz = nueva_raiz
            self._dividir_hijo(nueva_raiz, 0)


    def _dividir_hijo(self, nodo_padre, i):
        m = self.orden
        hijo_lleno = nodo_padre.hijos[i]

        nuevo_nodo = Nodo(m, hoja=hijo_lleno.hoja)

        # Índice de la clave que sube al padre
        mid = (m - 1) // 2

        clave_medio = hijo_lleno.claves[mid]

        # El nuevo nodo se queda con las claves a la derecha del medio
        nuevo_nodo.claves = hijo_lleno.claves[mid + 1:]
        hijo_lleno.claves = hijo_lleno.claves[:mid]

        if not hijo_lleno.hoja:
            nuevo_nodo.hijos = hijo_lleno.hijos[mid + 1:]
            hijo_lleno.hijos = hijo_lleno.hijos[:mid + 1]

        # Insertar el nuevo nodo y la clave que sube, en el padre
        nodo_padre.hijos.insert(i + 1, nuevo_nodo)
        nodo_padre.claves.insert(i, clave_medio)


    def _insertar_recursivo(self, nodo, clave):
        if nodo.hoja:
            i = len(nodo.claves) - 1
            nodo.claves.append(None)
            while i >= 0 and nodo.claves[i] > clave:
                nodo.claves[i + 1] = nodo.claves[i]
                i -= 1
            nodo.claves[i + 1] = clave

        else:
            i = len(nodo.claves) - 1
            while i >= 0 and nodo.claves[i] > clave:
                i -= 1
            i += 1

            self._insertar_recursivo(nodo.hijos[i], clave)

            m = self.orden
            if len(nodo.hijos[i].claves) == m:
                self._dividir_hijo(nodo, i)

# Aqui abajo va toda la logica para eliminar

    def _minimo_claves(self):
        m = self.orden
        return math.ceil(m / 2) - 1


    def eliminar(self, clave):
        self._eliminar_recursivo(self.raiz, clave)

        # Si la raíz quedó vacía y tiene hijos, el primer hijo pasa a ser la raíz
        if len(self.raiz.claves) == 0 and not self.raiz.hoja:
            self.raiz = self.raiz.hijos[0]


    def _eliminar_recursivo(self, nodo, clave):
        i = 0
        while i < len(nodo.claves) and clave > nodo.claves[i]:
            i += 1

        # ¿La clave está en este nodo?
        if i < len(nodo.claves) and nodo.claves[i] == clave:
            if nodo.hoja:
                nodo.claves.pop(i)
            else:
                self._eliminar_de_interno(nodo, i)
        else:
            if nodo.hoja:
                # La clave no existe en el árbol
                return

            self._garantizar_minimo(nodo, i)

            # Tras el rebalanceo, el índice del hijo correcto puede haber cambiado
            # (si hubo fusión con el hermano izquierdo, la clave "bajó" un índice)
            if i > len(nodo.claves):
                i = len(nodo.claves)

            self._eliminar_recursivo(nodo.hijos[i], clave)


    def _eliminar_de_interno(self, nodo, i):
        minimo = self._minimo_claves()
        clave = nodo.claves[i]

        if len(nodo.hijos[i].claves) > minimo:
            predecesor = self._obtener_predecesor(nodo.hijos[i])
            nodo.claves[i] = predecesor
            self._eliminar_recursivo(nodo.hijos[i], predecesor)

        elif len(nodo.hijos[i + 1].claves) > minimo:
            sucesor = self._obtener_sucesor(nodo.hijos[i + 1])
            nodo.claves[i] = sucesor
            self._eliminar_recursivo(nodo.hijos[i + 1], sucesor)

        else:
            self._fusionar(nodo, i)
            self._eliminar_recursivo(nodo.hijos[i], clave)


    def _obtener_predecesor(self, nodo):
        while not nodo.hoja:
            nodo = nodo.hijos[-1]
        return nodo.claves[-1]


    def _obtener_sucesor(self, nodo):
        while not nodo.hoja:
            nodo = nodo.hijos[0]
        return nodo.claves[0]


    def _garantizar_minimo(self, nodo, i):
        minimo = self._minimo_claves()

        if len(nodo.hijos[i].claves) > minimo:
            return  # ya cumple, no hace falta nada

        # Intentar pedir prestado al hermano izquierdo
        if i > 0 and len(nodo.hijos[i - 1].claves) > minimo:
            self._pedir_prestado_izquierda(nodo, i)

        # Intentar pedir prestado al hermano derecho
        elif i < len(nodo.claves) and len(nodo.hijos[i + 1].claves) > minimo:
            self._pedir_prestado_derecha(nodo, i)

        else:
            # Preferir fusionar con el hermano izquierdo si existe
            if i > 0:
                self._fusionar(nodo, i - 1)
            else:
                self._fusionar(nodo, i)


    def _pedir_prestado_izquierda(self, nodo, i):
        hijo = nodo.hijos[i]
        hermano_izq = nodo.hijos[i - 1]

        # La clave del padre baja al inicio del hijo
        hijo.claves.insert(0, nodo.claves[i - 1])

        # La última clave del hermano sube al padre
        nodo.claves[i - 1] = hermano_izq.claves.pop()

        # Si no son hojas, también se mueve el último hijo del hermano
        if not hijo.hoja:
            hijo.hijos.insert(0, hermano_izq.hijos.pop())


    def _pedir_prestado_derecha(self, nodo, i):
        hijo = nodo.hijos[i]
        hermano_der = nodo.hijos[i + 1]

        # La clave del padre baja al final del hijo
        hijo.claves.append(nodo.claves[i])

        # La primera clave del hermano sube al padre
        nodo.claves[i] = hermano_der.claves.pop(0)

        # Si no son hojas, también se mueve el primer hijo del hermano
        if not hijo.hoja:
            hijo.hijos.append(hermano_der.hijos.pop(0))


    def _fusionar(self, nodo, i):
        hijo_izq = nodo.hijos[i]
        hijo_der = nodo.hijos[i + 1]

        # La clave del padre baja al medio, uniendo ambos hijos
        hijo_izq.claves.append(nodo.claves[i])
        hijo_izq.claves.extend(hijo_der.claves)

        if not hijo_izq.hoja:
            hijo_izq.hijos.extend(hijo_der.hijos)

        # Quitar la clave del padre y la referencia al hijo derecho (ya fusionado)
        nodo.claves.pop(i)
        nodo.hijos.pop(i + 1)


# =================== Separacion entre Arbol B y Arbol B+ ===================

# arbol_bmas.py
from nodo import NodoBMas


class ArbolBMas:
    def __init__(self, orden):
        self.orden = orden
        self.raiz = NodoBMas(orden, hoja=True)

    def insertar(self, clave):
        self._insertar_recursivo(self.raiz, clave)

        m = self.orden
        if len(self.raiz.claves) == m:
            nueva_raiz = NodoBMas(m, hoja=False)
            nueva_raiz.hijos.append(self.raiz)
            self.raiz = nueva_raiz
            self._dividir_hijo(nueva_raiz, 0)

    def _insertar_recursivo(self, nodo, clave):
        if nodo.hoja:
            i = len(nodo.claves) - 1
            nodo.claves.append(None)
            while i >= 0 and nodo.claves[i] > clave:
                nodo.claves[i + 1] = nodo.claves[i]
                i -= 1
            nodo.claves[i + 1] = clave
        else:
            i = len(nodo.claves) - 1
            while i >= 0 and nodo.claves[i] > clave:
                i -= 1
            i += 1

            self._insertar_recursivo(nodo.hijos[i], clave)

            m = self.orden
            if len(nodo.hijos[i].claves) == m:
                self._dividir_hijo(nodo, i)

    def _dividir_hijo(self, nodo_padre, i):
        m = self.orden
        hijo_lleno = nodo_padre.hijos[i]
        nuevo_nodo = NodoBMas(m, hoja=hijo_lleno.hoja)
        mid = (m - 1) // 2

        if hijo_lleno.hoja:
            nuevo_nodo.claves = hijo_lleno.claves[mid:]
            hijo_lleno.claves = hijo_lleno.claves[:mid]

            clave_que_sube = nuevo_nodo.claves[0]

            nuevo_nodo.siguiente = hijo_lleno.siguiente
            hijo_lleno.siguiente = nuevo_nodo
        else:
            clave_que_sube = hijo_lleno.claves[mid]

            nuevo_nodo.claves = hijo_lleno.claves[mid + 1:]
            hijo_lleno.claves = hijo_lleno.claves[:mid]

            nuevo_nodo.hijos = hijo_lleno.hijos[mid + 1:]
            hijo_lleno.hijos = hijo_lleno.hijos[:mid + 1]

        nodo_padre.hijos.insert(i + 1, nuevo_nodo)
        nodo_padre.claves.insert(i, clave_que_sube)


    def _minimo_claves(self):
        m = self.orden
        return math.ceil(m / 2) - 1


    def eliminar(self, clave):
        self._eliminar_recursivo(self.raiz, clave)

        if len(self.raiz.claves) == 0 and not self.raiz.hoja:
            self.raiz = self.raiz.hijos[0]


    def _eliminar_recursivo(self, nodo, clave):
        if nodo.hoja:
            if clave in nodo.claves:
                nodo.claves.remove(clave)
            return

        i = 0
        while i < len(nodo.claves) and clave >= nodo.claves[i]:
            i += 1

        self._eliminar_recursivo(nodo.hijos[i], clave)

        # Si el hijo es hoja, el separador correspondiente debe reflejar
        # la primera clave real de esa hoja (pudo cambiar tras el borrado)
        if i > 0 and nodo.hijos[i].hoja and len(nodo.hijos[i].claves) > 0:
            nodo.claves[i - 1] = nodo.hijos[i].claves[0]

        minimo = self._minimo_claves()
        if len(nodo.hijos[i].claves) < minimo:
            self._garantizar_minimo(nodo, i)


    def _garantizar_minimo(self, nodo, i):
        minimo = self._minimo_claves()

        if i > 0 and len(nodo.hijos[i - 1].claves) > minimo:
            self._pedir_prestado_izquierda(nodo, i)

        elif i < len(nodo.claves) and len(nodo.hijos[i + 1].claves) > minimo:
            self._pedir_prestado_derecha(nodo, i)

        else:
            if i > 0:
                self._fusionar(nodo, i - 1)
            else:
                self._fusionar(nodo, i)


    def _pedir_prestado_izquierda(self, nodo, i):
        hijo = nodo.hijos[i]
        hermano_izq = nodo.hijos[i - 1]

        if hijo.hoja:
            clave_prestada = hermano_izq.claves.pop()
            hijo.claves.insert(0, clave_prestada)
            nodo.claves[i - 1] = hijo.claves[0]
        else:
            hijo.claves.insert(0, nodo.claves[i - 1])
            nodo.claves[i - 1] = hermano_izq.claves.pop()
            hijo.hijos.insert(0, hermano_izq.hijos.pop())


    def _pedir_prestado_derecha(self, nodo, i):
        hijo = nodo.hijos[i]
        hermano_der = nodo.hijos[i + 1]

        if hijo.hoja:
            clave_prestada = hermano_der.claves.pop(0)
            hijo.claves.append(clave_prestada)
            nodo.claves[i] = hermano_der.claves[0]
        else:
            hijo.claves.append(nodo.claves[i])
            nodo.claves[i] = hermano_der.claves.pop(0)
            hijo.hijos.append(hermano_der.hijos.pop(0))


    def _fusionar(self, nodo, i):
        hijo_izq = nodo.hijos[i]
        hijo_der = nodo.hijos[i + 1]

        if hijo_izq.hoja:
            # En hojas NO se baja la clave del padre, solo se unen las claves reales
            hijo_izq.claves.extend(hijo_der.claves)
            hijo_izq.siguiente = hijo_der.siguiente
        else:
            hijo_izq.claves.append(nodo.claves[i])
            hijo_izq.claves.extend(hijo_der.claves)
            hijo_izq.hijos.extend(hijo_der.hijos)

        nodo.claves.pop(i)
        nodo.hijos.pop(i + 1)