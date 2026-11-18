#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de conexión y ejecución de consultas en PostgreSQL.
Proyecto: Compilador de Lenguaje Natural a SQL (ESQL)
"""

import os
import decimal
import datetime

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_DISPONIBLE = True
except ImportError:
    PSYCOPG2_DISPONIBLE = False

# Variables de conexión (con valores por defecto compatibles con docker-compose)
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "esql_db")
DB_USER = os.getenv("DB_USER", "esql_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "esql_pass")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


def sanitizar_valor(valor):
    """Convierte tipos no serializables en JSON (Decimal, Date) a tipos estándar."""
    if isinstance(valor, decimal.Decimal):
        return float(valor) if (valor % 1) else int(valor)
    if isinstance(valor, (datetime.date, datetime.datetime)):
        return valor.isoformat()
    return valor


def obtener_conexion():
    """Crea y retorna una conexión a PostgreSQL."""
    if not PSYCOPG2_DISPONIBLE:
        raise RuntimeError("El controlador 'psycopg2' no está instalado en este entorno.")
    return psycopg2.connect(
        dsn=DATABASE_URL,
        connect_timeout=3
    )


def verificar_estado():
    """Comprueba si el servidor PostgreSQL está accesible."""
    if not PSYCOPG2_DISPONIBLE:
        return {"conectado": False, "error": "Librería psycopg2 no disponible"}
    try:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                return {"conectado": True, "servidor": f"{DB_HOST}:{DB_PORT}/{DB_NAME}"}
    except Exception as e:
        return {"conectado": False, "error": str(e)}


def ejecutar_consulta(sql: str):
    """
    Ejecuta una sentencia SQL en PostgreSQL y retorna las filas y columnas.

    Retorna:
        dict con:
            - 'exito': bool
            - 'columnas': lista de nombres de columnas
            - 'filas': lista de diccionarios {columna: valor}
            - 'total': cantidad de registros devueltos
            - 'error': mensaje en caso de fallo (o None)
    """
    if not PSYCOPG2_DISPONIBLE:
        return {
            "exito": False,
            "error": "El controlador 'psycopg2' no está instalado. No se puede conectar a PostgreSQL.",
            "columnas": [],
            "filas": [],
            "total": 0,
        }

    try:
        with obtener_conexion() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)

                if cur.description is None:
                    # Sentencia que no retorna filas (ej. DDL o INSERT sin RETURNING)
                    return {
                        "exito": True,
                        "columnas": [],
                        "filas": [],
                        "total": 0,
                    }

                columnas = [desc[0] for desc in cur.description]
                filas_crudas = cur.fetchall()

                # Limpiar datos para serialización JSON segura
                filas = [
                    {k: sanitizar_valor(v) for k, v in fila.items()}
                    for fila in filas_crudas
                ]

                return {
                    "exito": True,
                    "columnas": columnas,
                    "filas": filas,
                    "total": len(filas),
                    "error": None,
                }
    except Exception as err:
        return {
            "exito": False,
            "error": str(err).strip(),
            "columnas": [],
            "filas": [],
            "total": 0,
        }
