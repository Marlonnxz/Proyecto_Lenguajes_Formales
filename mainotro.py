import sys
import os

from ImplementacionAnalisisLexico import tokenizar
from AnalisisSintactico import AnalizadorSintactico


EXTENSION = ".upytc"


def ejecutar_linea(texto):

    texto = texto.strip()

    if not texto:
        return True

    try:
        tokens = tokenizar(texto)
        print("Tokens:", tokens)
        analizador = AnalizadorSintactico(tokens)
        resultado = analizador.revisarSintaxis()
        print("Resultado:", resultado)
        return resultado
    except SyntaxError as error:
        print(f"Error de sintaxis: {error}")
        return True


def ejecutar_archivo(ruta):

    if not os.path.exists(ruta):
        print(f"Error: el archivo '{ruta}'")
        return False
    if not ruta.lower().endswith(EXTENSION):
        print(f"Error: el archivo debe tener " f"la extension {EXTENSION}")
        return False
    try:
        with open(ruta,"r",encoding="utf-8") as archivo:
            contenido = archivo.read()

    except Exception as error:

        print(f"Error leyendo el archivo: {error}")
        return False

    if not contenido.strip():
        print("No hay nada")
        return False

    print(f"{ruta}")
    resultado = ejecutar_linea(contenido)
    return resultado


def modo_interactivo():

    print("BIENVENIDO A UPYTC")
    print("Escribe una operación básica de momento")
    print("Escribe CERRAR para salir")

    while True:

        try:
            texto = input("UPYTC> ")
        except KeyboardInterrupt:
            print("Programa terminado")
            break
        except EOFError:
            print("Programa terminado.")

            break

        resultado = ejecutar_linea(texto)

        if resultado is False:
            break


def mostrar_ayuda():

    print("UPYTC Language FACULTAD SECCIONAL SOGAMOSO")
    print("Uso:")
    print("  upytc")
    print("  upytc archivo.upytc")
    print(f"Extension soportada: {EXTENSION}")


def main():

    if len(sys.argv) == 1:
        modo_interactivo()
        return

    if (sys.argv[1] == "--help" or sys.argv[1] == "-h"):
        mostrar_ayuda()
        return

    if len(sys.argv) == 2:
        ruta = sys.argv[1]
        ejecutar_archivo(ruta)
        return

    print("Error: cantidad de argumentos ")

    mostrar_ayuda()


if __name__ == "__main__":
    main()