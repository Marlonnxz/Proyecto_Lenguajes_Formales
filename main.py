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

from compilador import (
    EXTENSION,
    PATRON_PETICION,
    PRUEBAS_DIR,
    compilar,
)
from compilador import obtener_parser as _crear_parser

ETIQUETA_ERROR = {
    "lexico": "Error Léxico",
    "sintactico": "Error Sintáctico",
    "semantico": "Error Semántico",
    "entrada": "Error",
}


def verificar_parser():
    """Carga las reglas al arrancar para fallar rápido si falta reglas.json."""
    try:
        _crear_parser()
    except FileNotFoundError as error:
        print(f"[Error Crítico]: {error}.")
        sys.exit(1)


def formato_token(t):
    """Reproduce el formato Token(TIPO, 'valor') a partir del token serializado."""
    return f"Token({t['tipo']}, {t['valor']!r})"


def procesar_linea(linea, num_linea, requerir_peticion=True):
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

    resultado = compilar(consulta)

    if resultado.get("tokens"):
        print(f"    Tokens: [{', '.join(formato_token(t) for t in resultado['tokens'])}]")

    if not resultado["exito"]:
        etiqueta = ETIQUETA_ERROR.get(resultado.get("fase"), "Error")
        print(f"    [{etiqueta}]: {resultado['error']}")
        return False

    if resultado.get("regla"):
        print(f"    [OK] Regla Sintáctica: {resultado['regla']} (ID: {resultado.get('regla_id', 'N/A')})")
    if resultado.get("resultado"):
        print(f"    SQL Generado: {resultado['resultado']}")
    return True


def procesar_archivo(ruta_archivo):
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
                res = procesar_linea(linea, num_linea)
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


def modo_lote():
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
        if procesar_archivo(archivo):
            archivos_ok += 1

    print("\n" + "#" * 70)
    print(f"LOTE FINALIZADO: {archivos_ok}/{len(archivos_esql)} archivos sin errores.")
    print("#" * 70 + "\n")


def modo_interactivo(es_doble_clic=False):
    """
    Modo REPL interactivo:
    Permite probar sentencias manualmente sin que la consola se cierre.
    """
    print("\n" + "=" * 70)
    print("COMPILADOR DE LENGUAJE NATURAL A SQL (ESQL) - MODO INTERACTIVO")
    print("=" * 70)
    print("Escribe tus sentencias directamente o con 'peticion = <consulta>'.")
    print("Modos de salida: prefija la sentencia con 'tokens:', 'sql:' o 'regla:'")
    print("                 para recibir unicamente esa parte del resultado.")
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
            modo_lote()
            continue

        if cmd in ("ayuda", "help", "?"):
            mostrar_ayuda()
            continue

        if cmd in ("limpiar", "cls", "clear"):
            os.system("cls" if os.name == "nt" else "clear")
            continue

        # Soporte para arrastrar un archivo .esql a la consola
        if entrada_limpia.lower().endswith(EXTENSION.lower()) and os.path.isfile(entrada_limpia):
            procesar_archivo(entrada_limpia)
            continue

        # Procesar sentencia en lenguaje natural
        procesar_linea(entrada, num_sentencia, requerir_peticion=False)
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
    verificar_parser()

    # Caso 1: Sin argumentos -> Iniciar modo interactivo persistente (no se cierra)
    if len(sys.argv) == 1:
        modo_interactivo(es_doble_clic=True)
        return

    arg = sys.argv[1].strip()

    # Caso 2: Ayuda
    if arg in ("-h", "--help"):
        mostrar_ayuda()
        return

    # Caso 3: Lote de pruebas explícito
    if arg == "--test":
        modo_lote()
        if getattr(sys, "frozen", False):
            try:
                input("\nPresione [Enter] para cerrar...")
            except Exception:
                pass
        return

    # Caso 4: Modo interactivo explícito
    if arg in ("-i", "--interactive"):
        modo_interactivo(es_doble_clic=False)
        return

    # Caso 5: Archivo individual
    exito = procesar_archivo(arg)
    if not exito:
        sys.exit(1)


if __name__ == "__main__":
    main()
