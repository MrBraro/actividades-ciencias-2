"""
SISTEMA DE CIFRADO DE UNA SOLA VÍA (HASH) - VERSIÓN DUAL
----------------------------------------------------------
Incluye dos algoritmos, ambos irreversibles (no existe función de
"descifrado"):

  1) SHA-256 MODIFICADO
     - Basado en la estructura estándar de SHA-256, pero con:
       a) Vectores de inicialización (IV) propios, distintos a los
          oficiales (se generan igual que el estándar -raíz cuadrada
          de primos- pero usando OTRO conjunto de primos).
       b) Rotaciones extra añadidas tanto en la expansión del mensaje
          como en cada ronda de compresión, para aumentar la difusión.
     - NO es compatible con SHA-256 real ni ha sido auditado
       criptográficamente. Es un ejercicio educativo.

  2) ALGORITMO PROPIO BASADO EN ASCII (no lineal)
     - Usa una S-box (caja de sustitución) generada con una fórmula
       no lineal (multiplicación modular + mezcla de bits).
     - Combina sustitución, rotación de bits y XOR encadenado sobre
       un estado interno de 8 bytes.

Ambos son de una sola vía porque pierden información deliberadamente
(operaciones módulo, desplazamientos, sustituciones no biyectivas),
por lo que no existe una forma matemática de invertir el proceso.
"""

import math


# ============================================================
# 1) SHA-256 MODIFICADO
# ============================================================

def _rotr(x, n, w=32):
    """Rotación circular de bits a la derecha (n bits, palabra de w bits)."""
    return ((x >> n) | (x << (w - n))) & 0xFFFFFFFF


def _generar_iv_personalizados():
    """
    Genera 8 palabras de 32 bits usando la parte fraccionaria de la raíz
    cuadrada de números primos (igual que el SHA-256 oficial), pero con
    un conjunto de primos DIFERENTE:

        SHA-256 oficial usa: 2, 3, 5, 7, 11, 13, 17, 19
        Aquí usamos:         23, 29, 31, 37, 41, 43, 47, 53
    """
    primos = [23, 29, 31, 37, 41, 43, 47, 53]
    iv = []
    for p in primos:
        frac = math.sqrt(p) % 1
        iv.append(int(frac * (2 ** 32)) & 0xFFFFFFFF)
    return iv


# Constantes de ronda (K): son constantes matemáticas públicas derivadas
# de la raíz cúbica de los primeros 64 números primos. Se mantienen
# iguales a las estándar; lo que cambiamos son el IV y las rotaciones.
_K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]


def _rellenar_mensaje(mensaje_bytes):
    """Aplica el relleno (padding) estándar tipo SHA-256: bit '1', ceros,
    y longitud original del mensaje en 64 bits al final."""
    longitud_bits = (len(mensaje_bytes) * 8) & 0xFFFFFFFFFFFFFFFF
    mensaje_bytes += b'\x80'
    while (len(mensaje_bytes) % 64) != 56:
        mensaje_bytes += b'\x00'
    mensaje_bytes += longitud_bits.to_bytes(8, 'big')
    return mensaje_bytes


def sha256_modificado(texto: str, rotacion_extra: int = 5) -> str:
    """
    Variante NO estándar de SHA-256 con IV propios y rotaciones extra.
    Devuelve un hash hexadecimal de 64 caracteres (256 bits).
    """
    H = _generar_iv_personalizados()
    mensaje = _rellenar_mensaje(texto.encode('utf-8'))

    for inicio in range(0, len(mensaje), 64):
        bloque = mensaje[inicio:inicio + 64]
        w = [int.from_bytes(bloque[i:i + 4], 'big') for i in range(0, 64, 4)]

        # --- Expansión del mensaje, con rotación extra añadida ---
        for i in range(16, 64):
            s0 = _rotr(w[i - 15], 7) ^ _rotr(w[i - 15], 18) ^ (w[i - 15] >> 3)
            s0 ^= _rotr(w[i - 15], rotacion_extra)              # rotación extra
            s1 = _rotr(w[i - 2], 17) ^ _rotr(w[i - 2], 19) ^ (w[i - 2] >> 10)
            s1 ^= _rotr(w[i - 2], rotacion_extra + 4)           # rotación extra
            w.append((w[i - 16] + s0 + w[i - 7] + s1) & 0xFFFFFFFF)

        a, b, c, d, e, f, g, h = H

        # --- Ronda de compresión, con rotación extra añadida ---
        for i in range(64):
            S1 = _rotr(e, 6) ^ _rotr(e, 11) ^ _rotr(e, 25)
            ch = (e & f) ^ ((~e & 0xFFFFFFFF) & g)
            temp1 = (h + S1 + ch + _K[i] + w[i]) & 0xFFFFFFFF
            S0 = _rotr(a, 2) ^ _rotr(a, 13) ^ _rotr(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (S0 + maj) & 0xFFFFFFFF

            h = g
            g = f
            f = e
            e = (d + temp1) & 0xFFFFFFFF
            e = _rotr(e, (rotacion_extra % 31) + 1)             # rotación extra
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xFFFFFFFF
            a = _rotr(a, ((rotacion_extra + 3) % 31) + 1)       # rotación extra

        H = [(H[j] + v) & 0xFFFFFFFF for j, v in enumerate([a, b, c, d, e, f, g, h])]

    return ''.join(f'{x:08x}' for x in H)


# ============================================================
# 2) ALGORITMO PROPIO BASADO EN ASCII (no lineal)
# ============================================================

def _generar_sbox():
    """
    Genera una caja de sustitución (S-box) de 256 valores usando una
    combinación no lineal: multiplicación modular por un primo +
    mezcla de bits con rotación. Introduce no linealidad (la salida
    no varía de forma proporcional a la entrada).
    """
    sbox = []
    for i in range(256):
        val = (i * 167 + 173) % 256                     # multiplicación no lineal
        val ^= ((i << 3) | (i >> 5)) & 0xFF              # mezcla con rotación de 8 bits
        val = (val * val + 41) % 256                     # término cuadrático (no lineal)
        sbox.append(val)
    return sbox


_SBOX = _generar_sbox()


def cifrado_ascii_no_lineal(texto: str, clave: int = 42) -> str:
    """
    Algoritmo propio de una sola vía: recorre cada carácter, obtiene su
    código ASCII/UTF-8, lo pasa por la S-box (sustitución no lineal),
    y lo combina con un estado interno de 8 bytes mediante suma modular,
    sustitución y rotación de bits, encadenando todo con XOR.
    """
    estado = [0x6a, 0x09, 0xe6, 0x67, 0xbb, 0x67, 0xae, 0x85]  # estado inicial (8 bytes)

    for i, caracter in enumerate(texto):
        b = ord(caracter) & 0xFF
        b_sustituido = _SBOX[b]

        for j in range(len(estado)):
            mezcla = (estado[j] + b_sustituido + i * clave + j) % 256
            mezcla = _SBOX[mezcla]                        # segunda pasada no lineal
            rot = ((mezcla << (j % 7 + 1)) | (mezcla >> (8 - (j % 7 + 1)))) & 0xFF
            estado[j] = rot ^ estado[(j + 1) % len(estado)]

    return ''.join(f'{byte:02x}' for byte in estado)


# ============================================================
# 3) MENÚ INTERACTIVO
# ============================================================

def _mostrar_resultado(nombre, texto, hash_resultado):
    print(f"\nTexto original : {texto}")
    print(f"Algoritmo      : {nombre}")
    print(f"Hash resultante: {hash_resultado}")
    print(f"Longitud       : {len(hash_resultado)} caracteres hexadecimales "
          f"({len(hash_resultado) * 4} bits)")


def menu():
    while True:
        print("\n" + "=" * 50)
        print(" SISTEMA DE CIFRADO DE UNA SOLA VÍA (HASH)")
        print("=" * 50)
        print("1. SHA-256 modificado (IV propios + rotaciones extra)")
        print("2. Algoritmo propio ASCII (operaciones no lineales)")
        print("3. Comparar ambos algoritmos")
        print("4. Salir")

        opcion = input("\nSelecciona una opción (1-4): ").strip()

        if opcion == "1":
            texto = input("Escribe el texto a cifrar: ")
            _mostrar_resultado("SHA-256 modificado", texto, sha256_modificado(texto))

        elif opcion == "2":
            texto = input("Escribe el texto a cifrar: ")
            _mostrar_resultado("ASCII no lineal", texto, cifrado_ascii_no_lineal(texto))

        elif opcion == "3":
            texto = input("Escribe el texto a cifrar: ")
            print(f"\nTexto original: {texto}")
            print(f"SHA-256 modificado : {sha256_modificado(texto)}")
            print(f"ASCII no lineal     : {cifrado_ascii_no_lineal(texto)}")

        elif opcion == "4":
            print("¡Hasta luego!")
            break

        else:
            print("Opción no válida, intenta de nuevo.")


if __name__ == "__main__":
    menu()