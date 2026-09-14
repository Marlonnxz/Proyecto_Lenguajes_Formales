#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Punto de Entrada Principal - Compilador de Lenguaje Natural a SQL (.esql)
Proyecto: Lenguajes Formales y Teoría de la Computación
"""

import os
import sys

# Asegurar codificación UTF-8 en terminales Windows
if sys.version_info >= (3, 7):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import re
from AnalisisLexico import tokenizar
from SintacticoDinamico import SintacticoDinamico

# =============================================================================
# CONSTANTES Y CONFIGURACIÓN
# =============================================================================
EXTENSION = ".esql"
PATRON_PETICION = re.compile(r"^peticion\s*=\s*(.*)$", re.IGNORECASE)
# Configuración de rutas (compatible con ejecución directa y PyInstaller --onefile)
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    BUNDLE_DIR = sys._MEIPASS
    APP_DIR = os.path.dirname(sys.executable)
else:
    BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_DIR = BUNDLE_DIR

REGLAS_PATH = os.path.join(BUNDLE_DIR, "reglas.json")
PRUEBAS_DIR = os.path.join(APP_DIR, "pruebas")


def obtener_parser():
    """Inicializa y retorna la instancia del analizador sintáctico dinámico."""
    if not os.path.isfile(REGLAS_PATH):
        print(f"[Error Crítico]: No se encontró el archivo de reglas en '{REGLAS_PATH}'.")
        sys.exit(1)
    return SintacticoDinamico(REGLAS_PATH)


def procesar_linea(linea, num_linea, parser, requerir_peticion=True):
    """
    Procesa una única línea de código:
    1. Limpieza de espacios y comprobación de comentarios.
    2. Validación de la palabra reservada 'peticion' y operador '='.
    3. Análisis léxico (tokenizar) sobre la consulta asignada.
    4. Análisis sintáctico dinámico (procesar_consulta).
    5. Control de excepciones controlado.

    Retorna:
        True si la sentencia fue procesada con éxito, False si hubo error, None si fue ignorada.
    """
    contenido = linea.strip()

    # Ignorar líneas vacías y comentarios (# o --)
    if not contenido or contenido.startswith("#") or contenido.startswith("--"):
        return None

    # Filtrar por la asignación 'peticion='
    match = PATRON_PETICION.match(contenido)
    if requerir_peticion:
        if not match:
            # Línea sin 'peticion=', se ignora
            return None
        consulta = match.group(1).strip()
        if not consulta:
            print(f"\n  [Línea {num_linea}]: \"{contenido}\"")
            print("    [Error]: Asignación 'peticion=' vacía (no se especificó consulta).")
            return False
    else:
        # En modo interactivo, aceptar con o sin 'peticion='
        consulta = match.group(1).strip() if match else contenido

    print(f"\n  [Línea {num_linea}]: \"{contenido}\"")
    if match:
        print(f"    Petición Asignada: \"{consulta}\"")

    # 1. Fase de Análisis Léxico
    try:
        tokens = tokenizar(consulta)
    except SyntaxError as e_lex:
        print(f"    [Error Léxico]: {e_lex}")
        return False
    except Exception as e_gen:
        print(f"    [Error Inesperado en Léxico]: {e_gen}")
        return False

    # Imprimir tokens generados de forma legible
    tokens_str = ", ".join(repr(t) for t in tokens)
    print(f"    Tokens: [{tokens_str}]")

    # 2. Fase de Análisis Sintáctico Dinámico
    try:
        regla, sql = parser.procesar_consulta(tokens)
        if regla is not None:
            print(f"    [OK] Regla Sintáctica: {regla['nombre']} (ID: {regla.get('id', 'N/A')})")
            print(f"    SQL Generado: {sql}")
            return True
        else:
            print(f"    [Error Sintáctico]: La sentencia no coincide con ninguna estructura gramatical válida.")
            return False
    except Exception as e_sint:
        print(f"    [Error Inesperado en Sintáctico]: {e_sint}")
        return False


def procesar_archivo(ruta_archivo, parser):
    """
    Valida y procesa un archivo con extensión .esql línea por línea.
    """
    # Validación 1: Existencia en disco
    if not os.path.isfile(ruta_archivo):
        print(f"\n[Error]: El archivo '{ruta_archivo}' no existe en el disco.")
        return False

    # Validación 2: Extensión estricta .esql (case-insensitive)
    _, ext = os.path.splitext(ruta_archivo)
    if ext.lower() != EXTENSION.lower():
        print(f"\n[Error de Extensión]: El archivo '{ruta_archivo}' fue rechazado.")
        print(f"                      Extensión recibida: '{ext}'. Se requiere estrictamente '{EXTENSION}'.")
        return False

    print("\n" + "=" * 70)
    print(f"PROCESANDO ARCHIVO: {ruta_archivo}")
    print("=" * 70)

    total_lineas = 0
    correctas = 0
    errores = 0

    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            for num_linea, linea in enumerate(f, start=1):
                res = procesar_linea(linea, num_linea, parser)
                if res is True:
                    total_lineas += 1
                    correctas += 1
                elif res is False:
                    total_lineas += 1
                    errores += 1
    except Exception as e:
        print(f"\n[Error de Lectura]: No se pudo leer el archivo '{ruta_archivo}': {e}")
        return False

    print("\n" + "-" * 70)
    print(f"Resumen de {os.path.basename(ruta_archivo)}: {correctas} correctas, {errores} con error (Total procesadas: {total_lineas})")
    print("-" * 70)
    return errores == 0


def modo_lote(parser):
    """
    Busca y ejecuta secuencialmente todos los archivos .esql en la carpeta 'pruebas/'.
    """
    if not os.path.isdir(PRUEBAS_DIR):
        print(f"\n[Error]: El directorio de pruebas '{PRUEBAS_DIR}' no existe.")
        return

    archivos_esql = [
        os.path.join(PRUEBAS_DIR, f)
        for f in sorted(os.listdir(PRUEBAS_DIR))
        if f.lower().endswith(EXTENSION.lower())
    ]

    if not archivos_esql:
        print(f"\n[Aviso]: No se encontraron archivos con extensión '{EXTENSION}' en '{PRUEBAS_DIR}'.")
        return

    print("\n" + "#" * 70)
    print(f"EJECUCIÓN EN LOTE: {len(archivos_esql)} archivos encontrados en pruebas/")
    print("#" * 70)

    archivos_ok = 0
    for archivo in archivos_esql:
        if procesar_archivo(archivo, parser):
            archivos_ok += 1

    print("\n" + "#" * 70)
    print(f"LOTE FINALIZADO: {archivos_ok}/{len(archivos_esql)} archivos sin errores.")
    print("#" * 70 + "\n")


def modo_interactivo(parser, es_doble_clic=False):
    """
    Modo REPL interactivo:
    Permite probar sentencias manualmente sin que la consola se cierre.
    """
    print("\n" + "=" * 70)
    print("COMPILADOR DE LENGUAJE NATURAL A SQL (ESQL) - MODO INTERACTIVO")
    print("=" * 70)
    print("Escribe tus sentencias directamente o con 'peticion = <consulta>'.")
    print("Comandos disponibles:")
    print("  - 'test' o 'lote' : Ejecutar todos los archivos en la carpeta 'pruebas/'")
    print("  - 'ayuda'         : Mostrar la guía de opciones")
    print("  - 'limpiar'       : Limpiar pantalla")
    print("  - 'salir'         : Cerrar la aplicación")
    print("=" * 70)

    num_sentencia = 1
    while True:
        try:
            entrada = input("\nESQL> ")
        except (KeyboardInterrupt, EOFError):
            print("\n\nSaliendo del modo interactivo...")
            break

        entrada_limpia = entrada.strip()
        if not entrada_limpia:
            continue

        cmd = entrada_limpia.lower()
        if cmd in ("salir", "exit", "quit"):
            print("Finalizando sesión de ESQL.")
            break

        if cmd in ("test", "lote"):
            modo_lote(parser)
            continue

        if cmd in ("ayuda", "help", "?"):
            mostrar_ayuda()
            continue

        if cmd in ("limpiar", "cls", "clear"):
            os.system("cls" if os.name == "nt" else "clear")
            continue

        # Soporte para arrastrar un archivo .esql a la consola
        if entrada_limpia.lower().endswith(EXTENSION.lower()) and os.path.isfile(entrada_limpia):
            procesar_archivo(entrada_limpia, parser)
            continue

        # Procesar sentencia en lenguaje natural
        procesar_linea(entrada, num_sentencia, parser, requerir_peticion=False)
        num_sentencia += 1

    if es_doble_clic or getattr(sys, "frozen", False):
        try:
            input("\nPresione [Enter] para cerrar la ventana...")
        except Exception:
            pass


def mostrar_ayuda():
    """Muestra la sintaxis de uso y opciones de main.py."""
    ayuda = f"""
Compilador de Lenguaje Natural a SQL (ESQL)
Uso: esql [OPCIÓN | RUTA_ARCHIVO]

Opciones y Modos:
  esql <archivo{EXTENSION}>
      Procesa un archivo individual especificado. Valida estrictamente la extensión {EXTENSION}.

  esql --test
      Modo Lote: Ejecuta secuencialmente todos los archivos '{EXTENSION}' en la carpeta 'pruebas/'.

  esql -i, --interactive
  esql (sin argumentos)
      Modo Interactivo (REPL): Mantiene la consola abierta con el prompt 'ESQL> '
      para ingresar sentencias interactivamente sin que se cierre.

  esql -h, --help
      Muestra este mensaje de ayuda.

Ejemplos:
  esql pruebas/consulta_basica.esql
  esql --test
  esql
"""
    print(ayuda)


def main():
    parser = obtener_parser()

    # Caso 1: Sin argumentos -> Iniciar modo interactivo persistente (no se cierra)
    if len(sys.argv) == 1:
        modo_interactivo(parser, es_doble_clic=True)
        return

    arg = sys.argv[1].strip()

    # Caso 2: Ayuda
    if arg in ("-h", "--help"):
        mostrar_ayuda()
        return

    # Caso 3: Lote de pruebas explícito
    if arg == "--test":
        modo_lote(parser)
        if getattr(sys, "frozen", False):
            try:
                input("\nPresione [Enter] para cerrar...")
            except Exception:
                pass
        return

    # Caso 4: Modo interactivo explícito
    if arg in ("-i", "--interactive"):
        modo_interactivo(parser, es_doble_clic=False)
        return

    # Caso 5: Archivo individual
    exito = procesar_archivo(arg, parser)
    if not exito:
        sys.exit(1)


if __name__ == "__main__":
    main()
