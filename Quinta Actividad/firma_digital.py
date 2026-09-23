"""
SISTEMA DE FIRMA DIGITAL
========================

Objetivo del proceso:
  1. INTEGRIDAD   -> demostrar que el documento recibido es EXACTAMENTE
                     el original (no fue modificado ni un solo bit).
  2. AUTENTICIDAD -> demostrar que quien firmó es el dueño del documento,
                     es decir, quien posee la llave privada correspondiente
                     a la llave pública usada para verificar.

Piezas que se combinan:
  - Cifrado de una vía (hash): sha256_modificado, tomado de Cifrado1via.py.
    Se usa para "resumir" el documento en una huella de 256 bits.
  - Cifrado asimétrico (llave pública / llave privada): RSA, implementado
    aquí desde cero, siguiendo la estructura clásica de una firma digital:

        firmar    -> firma = hash(documento) cifrado con la LLAVE PRIVADA
        verificar -> se descifra la firma con la LLAVE PÚBLICA y se
                     compara contra el hash recalculado del documento

  Solo quien tiene la llave privada pudo haber generado una firma que,
  al descifrarla con la llave pública correspondiente, coincida con el
  hash del documento. Y si el documento cambia aunque sea un carácter,
  su hash cambia por completo (efecto avalancha) y la verificación falla.

Nota de seguridad: esta es una implementación educativa de "RSA de libro"
(sin relleno / padding OAEP-PSS). Para un entorno productivo real se
usarían librerías como `cryptography` con padding PSS, pero para esta
actividad se construye la estructura matemática completa a mano, tal como
se hizo con el hash en Cifrado1via.py.
"""

import math
import random
from dataclasses import dataclass

from Cifrado1via import sha256_modificado


# =========================================================
# 1) PRIMALIDAD Y GENERACIÓN DE LLAVES RSA
# =========================================================

def _es_primo(n: int, rondas: int = 20) -> bool:
    """Test de primalidad de Miller-Rabin (probabilístico, muy confiable)."""
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p

    # n - 1 = 2^r * d, con d impar
    r, d = 0, n - 1
    while d % 2 == 0:
        d //= 2
        r += 1

    for _ in range(rondas):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def _generar_primo(bits: int) -> int:
    """Genera un número primo grande de 'bits' bits."""
    while True:
        candidato = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if _es_primo(candidato):
            return candidato


@dataclass
class LlavePublica:
    e: int
    n: int


@dataclass
class LlavePrivada:
    d: int
    n: int


@dataclass
class ParLlaves:
    publica: LlavePublica
    privada: LlavePrivada
    propietario: str = "desconocido"


def generar_par_llaves(propietario: str, bits: int = 1024) -> ParLlaves:
    """
    Genera un par de llaves RSA (pública, privada) para un firmante.
    'bits' es el tamaño del módulo n (1024 para la actividad; 2048+ en
    un caso real de producción).
    """
    mitad = bits // 2
    p = _generar_primo(mitad)
    q = _generar_primo(mitad)
    while p == q:
        q = _generar_primo(mitad)

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 65537  # exponente público estándar
    while math.gcd(e, phi) != 1:
        e += 2

    d = pow(e, -1, phi)  # inverso modular de e -> exponente privado

    return ParLlaves(
        publica=LlavePublica(e, n),
        privada=LlavePrivada(d, n),
        propietario=propietario,
    )


# =========================================================
# 2) FIRMA DIGITAL (hash + cifrado con llave privada)
# =========================================================

@dataclass
class DocumentoFirmado:
    documento: str
    hash_hex: str          # hash del documento en el momento de firmar
    firma: int             # hash cifrado con la llave privada del firmante
    llave_publica: LlavePublica
    firmante: str


def firmar_documento(documento: str, llaves: ParLlaves) -> DocumentoFirmado:
    """
    Proceso de firma:
      1. Se calcula el hash de una vía del documento (integridad).
      2. Ese hash se cifra con la LLAVE PRIVADA del firmante (autenticidad).
    """
    hash_hex = sha256_modificado(documento)
    hash_int = int(hash_hex, 16)

    if hash_int >= llaves.privada.n:
        raise ValueError(
            "El módulo n de la llave es muy pequeño para este hash; "
            "usa 'bits' mayor en generar_par_llaves()."
        )

    firma = pow(hash_int, llaves.privada.d, llaves.privada.n)

    return DocumentoFirmado(
        documento=documento,
        hash_hex=hash_hex,
        firma=firma,
        llave_publica=llaves.publica,
        firmante=llaves.propietario,
    )


def verificar_documento(documento_recibido: str, firmado: DocumentoFirmado):
    """
    Proceso de verificación:
      1. Se recalcula el hash del documento tal como llegó.
      2. Se descifra la firma con la LLAVE PÚBLICA del supuesto firmante.
      3. Si ambos valores coinciden:
           - el documento NO fue modificado (integridad)
           - la firma solo pudo generarla quien tiene la llave privada
             asociada a esa llave pública (autenticidad / dueño)

    Retorna (es_valida, detalle) donde detalle explica qué se comprobó.
    """
    e, n = firmado.llave_publica.e, firmado.llave_publica.n

    hash_actual_hex = sha256_modificado(documento_recibido)
    hash_actual_int = int(hash_actual_hex, 16)

    hash_descifrado_int = pow(firmado.firma, e, n)

    integridad_ok = (hash_actual_int == hash_descifrado_int)

    detalle = {
        "hash_del_documento_recibido": hash_actual_hex,
        "hash_recuperado_de_la_firma": f"{hash_descifrado_int:064x}",
        "coinciden": integridad_ok,
    }

    return integridad_ok, detalle


# =========================================================
# 3) DEMOSTRACIÓN
# =========================================================

def _linea():
    print("-" * 60)


def demo():
    print("=" * 60)
    print(" DEMOSTRACIÓN: FIRMA DIGITAL (hash propio + RSA propio)")
    print("=" * 60)

    # --- Alicia genera su par de llaves ---
    print("\n[1] Alicia genera su par de llaves RSA...")
    llaves_alicia = generar_par_llaves("Alicia", bits=1024)
    print(f"    Llave pública  (e, n) -> e={llaves_alicia.publica.e}")
    print(f"    n tiene {llaves_alicia.publica.n.bit_length()} bits")

    documento_original = "Contrato de compraventa - Monto: $10.000.000 COP - Fecha: 2026-09-23"

    # --- Alicia firma el documento ---
    print("\n[2] Alicia firma el documento con su llave PRIVADA...")
    firmado = firmar_documento(documento_original, llaves_alicia)
    print(f"    Hash del documento: {firmado.hash_hex}")
    print(f"    Firma (entero RSA): {firmado.firma}")

    # --- Caso A: verificación normal (documento intacto) ---
    _linea()
    print("[3] Caso A: Bob verifica el documento SIN modificar")
    valida, detalle = verificar_documento(documento_original, firmado)
    print(f"    ¿Firma válida? -> {valida}")
    if valida:
        print("    ✅ Documento íntegro y firmado por el dueño de la llave privada.")

    # --- Caso B: alguien modifica el documento después de firmado ---
    _linea()
    print("[4] Caso B: alguien modifica el documento (cambia el monto)")
    documento_alterado = documento_original.replace("10.000.000", "90.000.000")
    valida, detalle = verificar_documento(documento_alterado, firmado)
    print(f"    Hash original firmado : {firmado.hash_hex}")
    print(f"    Hash del doc. alterado: {detalle['hash_del_documento_recibido']}")
    print(f"    ¿Firma válida? -> {valida}")
    if not valida:
        print("    ❌ Se detecta que el documento NO es el original (integridad violada).")

    # --- Caso C: un impostor intenta firmar como si fuera Alicia ---
    _linea()
    print("[5] Caso C: Mallory (impostora) firma un documento con SU PROPIA llave")
    llaves_mallory = generar_par_llaves("Mallory", bits=1024)
    firmado_falso = firmar_documento(documento_original, llaves_mallory)

    # Bob cree que está verificando con la llave pública de Alicia,
    # pero la firma fue generada con la llave privada de Mallory.
    firmado_falso.llave_publica = llaves_alicia.publica
    firmado_falso.firmante = "Alicia (suplantada)"

    valida, detalle = verificar_documento(documento_original, firmado_falso)
    print(f"    ¿Firma válida contra la llave pública de Alicia? -> {valida}")
    if not valida:
        print("    ❌ Se detecta que el firmante NO es el dueño real (autenticidad violada).")


def menu():
    llaves_registradas = {}
    firmados_registrados = {}

    while True:
        print("\n" + "=" * 60)
        print(" SISTEMA DE FIRMA DIGITAL")
        print("=" * 60)
        print("1. Generar par de llaves para un firmante")
        print("2. Firmar un documento")
        print("3. Verificar un documento firmado")
        print("4. Ejecutar demostración completa (casos válido / alterado / suplantado)")
        print("5. Salir")

        opcion = input("\nSelecciona una opción (1-5): ").strip()

        if opcion == "1":
            nombre = input("Nombre del propietario de las llaves: ").strip()
            print("Generando llaves (puede tardar unos segundos)...")
            llaves_registradas[nombre] = generar_par_llaves(nombre, bits=1024)
            print(f"Llaves generadas para '{nombre}'.")

        elif opcion == "2":
            nombre = input("¿Quién firma? (debe tener llaves generadas): ").strip()
            if nombre not in llaves_registradas:
                print("Ese firmante no tiene llaves generadas todavía.")
                continue
            texto = input("Escribe el documento a firmar: ")
            firmado = firmar_documento(texto, llaves_registradas[nombre])
            clave_doc = f"{nombre}-{len(firmados_registrados) + 1}"
            firmados_registrados[clave_doc] = firmado
            print(f"Documento firmado y guardado como '{clave_doc}'.")
            print(f"Hash: {firmado.hash_hex}")
            print(f"Firma: {firmado.firma}")

        elif opcion == "3":
            if not firmados_registrados:
                print("No hay documentos firmados todavía.")
                continue
            print("Documentos firmados disponibles:", ", ".join(firmados_registrados))
            clave_doc = input("¿Cuál documento firmado quieres verificar? ").strip()
            if clave_doc not in firmados_registrados:
                print("No existe ese identificador.")
                continue
            texto_a_verificar = input(
                "Pega el documento tal como fue recibido (puede estar igual o alterado): "
            )
            firmado = firmados_registrados[clave_doc]
            valida, detalle = verificar_documento(texto_a_verificar, firmado)
            print(f"\n¿Firma válida? -> {valida}")
            print(f"Hash recibido   : {detalle['hash_del_documento_recibido']}")
            print(f"Hash de la firma: {detalle['hash_recuperado_de_la_firma']}")
            if valida:
                print("✅ Documento íntegro y firmado por su dueño.")
            else:
                print("❌ El documento fue modificado o la firma no corresponde al firmante.")

        elif opcion == "4":
            demo()

        elif opcion == "5":
            print("¡Hasta luego!")
            break

        else:
            print("Opción no válida, intenta de nuevo.")


if __name__ == "__main__":
    menu()
