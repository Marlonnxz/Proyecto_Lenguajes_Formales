#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor API REST con FastAPI para el compilador del lenguaje ESQL
Proyecto: Lenguajes Formales y Teoría de la Computación
"""

import json
import os

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from compilador import BUNDLE_DIR, MODOS, REGLAS_PATH, compilar

app = FastAPI(
    title="ESQL Language",
    description="API y consola web para ejecutar programas del lenguaje ESQL",
    version="1"
)

CONSOLA_PATH = os.path.join(BUNDLE_DIR, "consola.html")


class CodigoRequest(BaseModel):
    codigo: str


@app.get("/")
def consola():
    """Consola web interactiva del lenguaje ESQL."""
    return FileResponse(CONSOLA_PATH, media_type="text/html")


@app.get("/info")
def info():
    """Información del lenguaje, versión y modos de salida disponibles."""
    return {
        "lenguaje": "ESQL",
        "version": "v1.0",
        "estado": "En desarrollo",
        "modos": list(MODOS),
    }


@app.get("/reglas")
def listar_reglas():
    """Gramática soportada: reglas sintácticas cargadas desde reglas.json."""
    with open(REGLAS_PATH, "r", encoding="utf-8") as archivo:
        reglas = json.load(archivo)["reglas"]
    return {
        "total": len(reglas),
        "reglas": [
            {"id": r["id"], "nombre": r["nombre"], "descripcion": r["descripcion"]}
            for r in reglas
        ],
    }


@app.post("/iniciar")
def ejecutar_codigo(request: CodigoRequest):
    """
    Procesa y ejecuta una sentencia ESQL.

    Acepta un modo de salida opcional como palabra clave inicial:
      - "tokens: <consulta>"  -> solo la lista de tokens
      - "sql: <consulta>"     -> solo el SQL generado
      - "regla: <consulta>"   -> solo la regla sintáctica aplicada
      - sin prefijo           -> respuesta completa
    La consulta admite el formato 'peticion = <consulta>' o directa.
    """
    return compilar(request.codigo)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("servidor:app", host="0.0.0.0", port=8000, reload=True)
