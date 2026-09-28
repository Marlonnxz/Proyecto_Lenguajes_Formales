# Acciones Semánticas Asociadas a las Reglas Sintácticas
# Aquí se define el funcionamiento lógico de cada regla mediante la Configuración Assoc.

def formatear_literal(token):
    """Formatea valores literales para SQL (agrega comillas a strings y preserva números)."""
    val = token.valor
    if token.tipo == "STRING":
        return f"'{val}'"
    # Si es numérico (entero o decimal)
    if val.replace(".", "", 1).isdigit():
        return val
    # Si es texto sin comillas en el lenguaje natural (ej. Bogota -> 'Bogota')
    return f"'{val}'"


def construir_consulta_sql(tokens):
    """
    Construye de forma dinámica la consulta SQL a partir de la secuencia de tokens.
    Soporta:
      - N campos o WILDCARD (*)
      - Tablas simples o compuestas (separadas por guión bajo)
      - WHERE simple, con BETWEEN o múltiple (AND / OR)
      - GROUP BY
      - ORDER BY con o sin ASC / DESC
    """
    idx_from = -1
    idx_where = -1
    idx_group = -1
    idx_order = -1

    for i, t in enumerate(tokens):
        if t.tipo == "FROM" and idx_from == -1:
            idx_from = i
        elif t.tipo == "WHERE_CLAUSE" and idx_where == -1:
            idx_where = i
        elif t.tipo == "GROUP_CLAUSE" and idx_group == -1:
            idx_group = i
        elif t.tipo == "ORDER_CLAUSE" and idx_order == -1:
            idx_order = i

    # 1. Campos a seleccionar
    tokens_campos = tokens[1:idx_from] if idx_from != -1 else tokens[1:]
    if any(t.tipo == "WILDCARD" for t in tokens_campos):
        campos_str = "*"
    else:
        campos = [t.valor for t in tokens_campos if t.tipo == "ID"]
        campos_str = ", ".join(campos) if campos else "*"

    # 2. Nombre de la tabla
    indices_posteriores = [idx for idx in [idx_where, idx_group, idx_order, len(tokens)] if idx > idx_from]
    limite_tabla = min(indices_posteriores)
    tokens_tabla = tokens[idx_from + 1:limite_tabla]
    partes_tabla = [t.valor for t in tokens_tabla if t.tipo == "ID"]
    tabla_str = "_".join(partes_tabla)

    sql = f"SELECT {campos_str} FROM {tabla_str}"

    # 3. Cláusula WHERE
    if idx_where != -1:
        limites_where = [idx for idx in [idx_group, idx_order, len(tokens)] if idx > idx_where]
        limite_where = min(limites_where)
        tokens_where = tokens[idx_where + 1:limite_where]
        condiciones = []
        k = 0
        while k < len(tokens_where):
            t = tokens_where[k]
            if t.tipo == "ID":
                campo = t.valor
                k += 1
                if k < len(tokens_where):
                    sig = tokens_where[k]
                    if sig.tipo == "BETWEEN_CLAUSE":
                        # campo BETWEEN val1 AND val2
                        val1 = formatear_literal(tokens_where[k + 1])
                        # tokens_where[k + 2] es SEPARATOR ('y')
                        val2 = formatear_literal(tokens_where[k + 3])
                        condiciones.append(f"{campo} BETWEEN {val1} AND {val2}")
                        k += 4
                    elif sig.tipo == "OPERADOR":
                        operador = sig.valor
                        val = formatear_literal(tokens_where[k + 1])
                        condiciones.append(f"{campo} {operador} {val}")
                        k += 2
                    else:
                        k += 1
                else:
                    k += 1
            elif t.tipo in ("LOGICAL_OP", "SEPARATOR"):
                op_logico = "AND" if (t.tipo == "SEPARATOR" or t.valor.lower() in ("y", "and")) else "OR"
                condiciones.append(op_logico)
                k += 1
            else:
                k += 1

        if condiciones:
            sql += f" WHERE {' '.join(condiciones)}"

    # 4. Cláusula GROUP BY
    if idx_group != -1:
        limites_group = [idx for idx in [idx_order, len(tokens)] if idx > idx_group]
        limite_group = min(limites_group)
        tokens_group = tokens[idx_group + 1:limite_group]
        campos_group = [t.valor for t in tokens_group if t.tipo == "ID"]
        if campos_group:
            sql += f" GROUP BY {', '.join(campos_group)}"

    # 5. Cláusula ORDER BY
    if idx_order != -1:
        tokens_order = tokens[idx_order + 1:]
        campo_order = None
        dir_order = None
        for t in tokens_order:
            if t.tipo == "ID" and campo_order is None:
                campo_order = t.valor
            elif t.tipo == "ORDER_DIR":
                dir_order = t.valor

        if campo_order:
            sql += f" ORDER BY {campo_order}"
            if dir_order:
                sql += f" {dir_order}"

    return sql


# =============================================================================
# ACCIONES BASE (REGLAS 1 A 10)
# =============================================================================

def accion_consulta_simple(tokens):
    campo = tokens[1].valor
    tabla = tokens[3].valor
    return f"SELECT {campo} FROM {tabla}"

def accion_dos_campos_coma(tokens):
    campo1 = tokens[1].valor
    campo2 = tokens[3].valor
    tabla = tokens[5].valor
    return f"SELECT {campo1}, {campo2} FROM {tabla}"

def accion_dos_campos_y(tokens):
    campo1 = tokens[1].valor
    campo2 = tokens[3].valor
    tabla = tokens[5].valor
    return f"SELECT {campo1}, {campo2} FROM {tabla}"

def accion_filtro_where(tokens):
    campo = tokens[1].valor
    tabla = tokens[3].valor
    condicion_campo = tokens[5].valor
    operador = tokens[6].valor
    valor = formatear_literal(tokens[7])
    return f"SELECT {campo} FROM {tabla} WHERE {condicion_campo} {operador} {valor}"

def accion_ordenamiento(tokens):
    campo = tokens[1].valor
    tabla = tokens[3].valor
    orden_campo = tokens[5].valor
    return f"SELECT {campo} FROM {tabla} ORDER BY {orden_campo}"

def accion_tabla_compuesta(tokens):
    campo = tokens[1].valor
    tabla_parte1 = tokens[3].valor
    tabla_parte2 = tokens[4].valor
    return f"SELECT {campo} FROM {tabla_parte1}_{tabla_parte2}"

def accion_completa(tokens):
    campo = tokens[1].valor
    tabla = tokens[3].valor
    condicion_campo = tokens[5].valor
    operador = tokens[6].valor
    valor = formatear_literal(tokens[7])
    orden_campo = tokens[9].valor
    return f"SELECT {campo} FROM {tabla} WHERE {condicion_campo} {operador} {valor} ORDER BY {orden_campo}"

def accion_lista_tres_campos(tokens):
    campo1 = tokens[1].valor
    campo2 = tokens[3].valor
    campo3 = tokens[5].valor
    tabla = tokens[7].valor
    return f"SELECT {campo1}, {campo2}, {campo3} FROM {tabla}"

def accion_todos_campos(tokens):
    # Soporta tanto SELECT * directo como tokens dinámicos
    return construir_consulta_sql(tokens)

def accion_filtro_tabla_compuesta(tokens):
    campo = tokens[1].valor
    tabla_parte1 = tokens[3].valor
    tabla_parte2 = tokens[4].valor
    condicion_campo = tokens[6].valor
    operador = tokens[7].valor
    valor = formatear_literal(tokens[8])
    return f"SELECT {campo} FROM {tabla_parte1}_{tabla_parte2} WHERE {condicion_campo} {operador} {valor}"


# =============================================================================
# NUEVAS ACCIONES DINÁMICAS (REGLAS 11 A 17)
# =============================================================================

def accion_n_campos(tokens):
    return construir_consulta_sql(tokens)

def accion_filtro_where_n_campos(tokens):
    return construir_consulta_sql(tokens)

def accion_ordenamiento_direccion(tokens):
    return construir_consulta_sql(tokens)

def accion_filtro_multiple(tokens):
    return construir_consulta_sql(tokens)

def accion_filtro_between(tokens):
    return construir_consulta_sql(tokens)

def accion_agrupamiento(tokens):
    return construir_consulta_sql(tokens)

def accion_maestra_avanzada(tokens):
    return construir_consulta_sql(tokens)


# Mapa de Asociación ("Configuración Assoc")
MAPA_ASOCIACION = {
    # Reglas base 1-10
    "accion_consulta_simple": accion_consulta_simple,
    "accion_dos_campos_coma": accion_dos_campos_coma,
    "accion_dos_campos_y": accion_dos_campos_y,
    "accion_filtro_where": accion_filtro_where,
    "accion_ordenamiento": accion_ordenamiento,
    "accion_tabla_compuesta": accion_tabla_compuesta,
    "accion_completa": accion_completa,
    "accion_lista_tres_campos": accion_lista_tres_campos,
    "accion_todos_campos": accion_todos_campos,
    "accion_filtro_tabla_compuesta": accion_filtro_tabla_compuesta,
    # Reglas ampliadas 11-17
    "accion_n_campos": accion_n_campos,
    "accion_filtro_where_n_campos": accion_filtro_where_n_campos,
    "accion_ordenamiento_direccion": accion_ordenamiento_direccion,
    "accion_filtro_multiple": accion_filtro_multiple,
    "accion_filtro_between": accion_filtro_between,
    "accion_agrupamiento": accion_agrupamiento,
    "accion_maestra_avanzada": accion_maestra_avanzada,
}
