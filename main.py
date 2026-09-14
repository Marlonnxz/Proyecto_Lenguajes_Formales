import sys
import os

from AnalisisLexico import tokenizar
from SintacticoDinamico import SintacticoDinamico

# Extensión de archivo soportada para el lenguaje
EXTENSION = ".nsql"

# Ruta absoluta al archivo de reglas para garantizar su carga sin importar el directorio de ejecución
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REGLAS_PATH = os.path.join(BASE_DIR, "reglas.json")

# Inicialización del analizador sintáctico dinámico
parser = SintacticoDinamico(REGLAS_PATH)


def ejecutar_linea(texto, mostrar_tokens=True):
    """
    Analiza y ejecuta una línea de texto en lenguaje natural.
    Tokeniza la entrada y valida la sintaxis con el autómata correspondiente.
    """
    texto = texto.strip()

    if not texto or texto.startswith("#"):
        return True

    try:
        tokens = tokenizar(texto)
        if mostrar_tokens:
            print(f"  Tokens: {tokens}")

        regla, sql = parser.procesar_consulta(tokens)

        if regla:
            print(f"  [OK] Regla aplicada: {regla['nombre']} (ID: {regla['id']})")
            print(f"  [SQL Generado]: {sql}")
            return True
        else:
            print("  [Error Sintáctico]: La consulta no coincide con ninguna regla gramatical definida.")
            return False

    except SyntaxError as error:
        print(f"  [Error Léxico/Sintáctico]: {error}")
        return False
    except Exception as error:
        print(f"  [Error inesperado]: {error}")
        return False


def ejecutar_archivo(ruta):
    """
    Lee y procesa un archivo con la extensión permitida (.nsql).
    Soporta archivos con una o múltiples consultas (una por línea).
    """
    if not os.path.exists(ruta):
        print(f"Error: El archivo '{ruta}' no existe.")
        return False

    if not ruta.lower().endswith(EXTENSION):
        print(f"Error: El archivo debe tener la extensión '{EXTENSION}'.")
        return False

    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            lineas = archivo.readlines()
    except Exception as error:
        print(f"Error leyendo el archivo '{ruta}': {error}")
        return False

    lineas_procesar = [l.strip() for l in lineas if l.strip() and not l.strip().startswith("#")]

    if not lineas_procesar:
        print(f"El archivo '{ruta}' está vacío o solo contiene comentarios.")
        return False

    print("=" * 65)
    print(f"Ejecutando archivo: {ruta}")
    print(f"Total de consultas a procesar: {len(lineas_procesar)}")
    print("=" * 65)

    # Caso especial: si el archivo contiene varias líneas que juntas forman una única consulta válida
    if len(lineas_procesar) > 1:
        texto_unificado = " ".join(lineas_procesar)
        try:
            tokens_uni = tokenizar(texto_unificado)
            regla_uni, sql_uni = parser.procesar_consulta(tokens_uni)
            if regla_uni:
                print(f"\n[Consulta Unificada]: {texto_unificado}")
                print(f"  Tokens: {tokens_uni}")
                print(f"  [OK] Regla aplicada: {regla_uni['nombre']} (ID: {regla_uni['id']})")
                print(f"  [SQL Generado]: {sql_uni}")
                print("=" * 65)
                print("Resumen: 1/1 consulta ejecutada con éxito.")
                return True
        except Exception:
            pass

    # Procesar línea por línea
    total = len(lineas_procesar)
    exitos = 0

    for i, linea in enumerate(lineas_procesar, 1):
        print(f"\n[{i}/{total}] Entrada: {linea}")
        if ejecutar_linea(linea):
            exitos += 1

    print("\n" + "=" * 65)
    print(f"Resumen de ejecución: {exitos}/{total} consulta(s) procesada(s) con éxito.")
    print("=" * 65)

    return exitos == total


def modo_interactivo():
    """
    Inicia una sesión interactiva (REPL) en consola.
    """
    print("=" * 65)
    print("  BIENVENIDO AL ANALIZADOR DE LENGUAJE NATURAL A SQL")
    print("  UPTC - FACULTAD SECCIONAL SOGAMOSO")
    print("=" * 65)
    print("Escribe una consulta (ej: 'consulta id de la tabla usuarios')")
    print("Escribe 'SALIR' o 'CERRAR' para salir del programa.\n")

    while True:
        try:
            texto = input("NSQL> ").strip()
        except KeyboardInterrupt:
            print("\nPrograma interrumpido por el usuario.")
            break
        except EOFError:
            print("\nPrograma terminado.")
            break

        if not texto:
            continue

        if texto.lower() in ("salir", "cerrar", "exit", "quit"):
            print("Programa finalizado. ¡Hasta luego!")
            break

        ejecutar_linea(texto)


def mostrar_ayuda():
    """
    Muestra información de ayuda y sintaxis de uso por línea de comandos.
    """
    print("=" * 65)
    print("NSQL Language - Analizador de Lenguaje Natural a SQL")
    print("UPTC - FACULTAD SECCIONAL SOGAMOSO")
    print("=" * 65)
    print("Uso:")
    print("  py main.py                      Inicia el modo interactivo (consola)")
    print("  py main.py <archivo>            Ejecuta un archivo de consultas")
    print("  py main.py -h / --help          Muestra este mensaje de ayuda")
    print()
    print(f"Extensión soportada: {EXTENSION}")
    print("=" * 65)


def main():
    if len(sys.argv) == 1:
        modo_interactivo()
        return

    if sys.argv[1] in ("--help", "-h"):
        mostrar_ayuda()
        return

    if len(sys.argv) == 2:
        ruta = sys.argv[1]
        ejecutar_archivo(ruta)
        return

    print("Error: Cantidad de argumentos inválida.\n")
    mostrar_ayuda()


if __name__ == "__main__":
    main()
