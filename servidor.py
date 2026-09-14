#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor API REST con FastAPI para el compilador del lenguaje ESQL
Proyecto: Lenguajes Formales y Teoría de la Computación
"""

import os
import re
from fastapi import FastAPI
from pydantic import BaseModel
from AnalisisLexico import tokenizar
from SintacticoDinamico import SintacticoDinamico

app = FastAPI(
    title="ESQL Language",
    description="API para ejecutar programas del lenguaje ESQL",
    version="1"
)

# Inicializar parser con reglas del lenguaje
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REGLAS_PATH = os.path.join(BASE_DIR, "reglas.json")
parser = SintacticoDinamico(REGLAS_PATH)

PATRON_PETICION = re.compile(r"^peticion\s*=\s*(.*)$", re.IGNORECASE)


class CodigoRequest(BaseModel):
    codigo: str


@app.get("/")
def inicio():
    """Endpoint inicial con información del lenguaje y versión."""
    return {
        "lenguaje": "ESQL",
        "version": "v1.0",
        "estado": "En desarrollo"
    }


@app.post("/iniciar")
def ejecutar_codigo(request: CodigoRequest):
    """
    Endpoint para procesar y ejecutar una sentencia en lenguaje natural ESQL:
    1. Extrae la consulta (soporta 'peticion = ...' o consulta directa).
    2. Realiza el análisis léxico obteniendo los tokens.
    3. Ejecuta el análisis sintáctico dinámico contra reglas.json.
    4. Retorna resultado traducido a SQL, regla aplicada y lista de tokens.
    """
    try:
        codigo = request.codigo.strip()
        if not codigo:
            return {"error": "No se ingreso codigo"}

        # Soporte para formato 'peticion = consulta' o consulta directa
        match = PATRON_PETICION.match(codigo)
        consulta = match.group(1).strip() if match else codigo

        if not consulta:
            return {"error": "Asignación 'peticion=' vacía (no se especificó consulta)"}

        # Análisis Léxico
        tokens = tokenizar(consulta)

        # Análisis Sintáctico Dinámico
        regla, sql = parser.procesar_consulta(tokens)

        if not regla:
            raise SyntaxError("La consulta no coincide con ninguna regla sintáctica válida")

        return {
            "exito": True,
            "resultado": sql,
            "regla": regla["nombre"],
            "tokens": [
                token.to_json()
                for token in tokens
            ]
        }
    except SyntaxError as error:
        return {"error": str(error)}
    except Exception as error:
        return {"error": f"Error interno: {str(error)}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("servidor:app", host="0.0.0.0", port=8000, reload=True)
