#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Núcleo del compilador ESQL, compartido por la API (servidor.py) y la CLI (main.py).
Centraliza: rutas de reglas, extracción de la petición, modos de salida y el pipeline
léxico -> sintáctico -> SQL.
"""

import os
import re
import sys

from AnalisisLexico import tokenizar
from SintacticoDinamico import SintacticoDinamico

EXTENSION = ".esql"

# Rutas (compatible con ejecución directa y con PyInstaller --onefile)
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    BUNDLE_DIR = sys._MEIPASS
    APP_DIR = os.path.dirname(sys.executable)
else:
    BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_DIR = BUNDLE_DIR

REGLAS_PATH = os.path.join(BUNDLE_DIR, "reglas.json")
PRUEBAS_DIR = os.path.join(APP_DIR, "pruebas")

PATRON_PETICION = re.compile(r"^peticion\s*=\s*(.*)$", re.IGNORECASE)

# Modo de salida: palabra clave opcional al inicio ("tokens: ...", "sql ...")
MODOS = {
    "todo": None,                       # None = todas las claves
    "tokens": ("tokens",),
    "sql": ("resultado",),
    "regla": ("regla", "regla_id", "descripcion"),
}
PATRON_MODO = re.compile(r"^(%s)\s*:?\s+(.+)$" % "|".join(MODOS), re.IGNORECASE)

_parser = None


def obtener_parser():
    """Devuelve la instancia única del analizador sintáctico dinámico."""
    global _parser
    if _parser is None:
        if not os.path.isfile(REGLAS_PATH):
            raise FileNotFoundError(f"No se encontró el archivo de reglas en '{REGLAS_PATH}'")
        _parser = SintacticoDinamico(REGLAS_PATH)
    return _parser


def separar_modo(codigo):
    """('tokens: consulta x', ) -> ('tokens', 'consulta x'). Sin prefijo -> ('todo', codigo)."""
    match = PATRON_MODO.match(codigo.strip())
    if not match:
        return "todo", codigo.strip()
    return match.group(1).lower(), match.group(2).strip()


def extraer_consulta(codigo):
    """Acepta 'peticion = <consulta>' o la consulta directa."""
    match = PATRON_PETICION.match(codigo.strip())
    return match.group(1).strip() if match else codigo.strip()


def compilar(codigo):
    """
    Pipeline completo sobre una sentencia ESQL.

    Retorna un dict con 'exito'. En éxito incluye solo las claves que pida el modo
    (todo | tokens | sql | regla). En error incluye 'error' y 'fase'.
    """
    modo, resto = separar_modo(codigo or "")
    if not resto:
        return {"exito": False, "modo": modo, "fase": "entrada", "error": "No se ingresó código"}

    consulta = extraer_consulta(resto)
    if modo == "todo":  # admite tanto 'tokens: peticion = x' como 'peticion = tokens: x'
        modo, consulta = separar_modo(consulta)
    if not consulta:
        return {
            "exito": False, "modo": modo, "fase": "entrada",
            "error": "Asignación 'peticion=' vacía (no se especificó consulta)",
        }

    try:
        tokens = tokenizar(consulta)
    except SyntaxError as error:
        return {"exito": False, "modo": modo, "consulta": consulta,
                "fase": "lexico", "error": str(error)}

    try:
        regla, sql = obtener_parser().procesar_consulta(tokens)
    except Exception as error:  # error en la acción semántica asociada a la regla
        return {"exito": False, "modo": modo, "consulta": consulta,
                "fase": "semantico", "error": str(error)}

    if not regla:
        return {
            "exito": False, "modo": modo, "consulta": consulta, "fase": "sintactico",
            "error": "La consulta no coincide con ninguna regla sintáctica válida",
            "tokens": [t.to_json() for t in tokens],
        }

    completo = {
        "exito": True,
        "modo": modo,
        "consulta": consulta,
        "resultado": sql,
        "regla": regla["nombre"],
        "regla_id": regla.get("id"),
        "descripcion": regla.get("descripcion"),
        "tokens": [t.to_json() for t in tokens],
    }

    claves = MODOS[modo]
    if claves is None:
        return completo
    return {"exito": True, "modo": modo, "consulta": consulta,
            **{k: completo[k] for k in claves}}


def demo():
    """Autocomprobación mínima: python compilador.py"""
    ok = compilar("peticion = selecciona nombre, edad de la tabla usuarios")
    assert ok["exito"] and ok["resultado"] == "SELECT nombre, edad FROM usuarios", ok
    assert len(ok["tokens"]) == 7, ok["tokens"]

    solo_tokens = compilar("tokens: selecciona nombre de la tabla usuarios")
    assert set(solo_tokens) == {"exito", "modo", "consulta", "tokens"}, solo_tokens

    solo_sql = compilar("sql selecciona nombre de la tabla usuarios")
    assert set(solo_sql) == {"exito", "modo", "consulta", "resultado"}, solo_sql
    assert solo_sql["resultado"] == "SELECT nombre FROM usuarios"

    solo_regla = compilar("regla: selecciona nombre de la tabla usuarios")
    assert solo_regla["regla_id"] == 1, solo_regla

    malo = compilar("selecciona de la tabla usuarios")
    assert not malo["exito"] and malo["fase"] == "sintactico", malo

    lexico = compilar("selecciona nombre$ de la tabla usuarios")
    assert not lexico["exito"] and lexico["fase"] == "lexico", lexico


    ambos = compilar("peticion = sql: selecciona nombre de la tabla usuarios")
    assert set(ambos) == {"exito", "modo", "consulta", "resultado"}, ambos

    print("compilador.py OK")


if __name__ == "__main__":
    demo()
