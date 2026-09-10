# Acciones Semánticas Asociadas a las Reglas Sintácticas
# Aquí se define el funcionamiento lógico de cada una de las 10 reglas por separado

def accion_consulta_simple(tokens):
    # SELECT + ID + FROM + ID
    # Ejemplo: [Token(SELECT, 'consulta'), Token(ID, 'id'), Token(FROM, 'de la tabla'), Token(ID, 'usuarios')]
    campo = tokens[1].valor
    tabla = tokens[3].valor
    return f"SELECT {campo} FROM {tabla}"

def accion_dos_campos_coma(tokens):
    # SELECT + ID + SEPARATOR + ID + FROM + ID
    campo1 = tokens[1].valor
    campo2 = tokens[3].valor
    tabla = tokens[5].valor
    return f"SELECT {campo1}, {campo2} FROM {tabla}"

def accion_dos_campos_y(tokens):
    # SELECT + ID + SEPARATOR + ID + FROM + ID
    campo1 = tokens[1].valor
    campo2 = tokens[3].valor
    tabla = tokens[5].valor
    return f"SELECT {campo1}, {campo2} FROM {tabla}"

def accion_filtro_where(tokens):
    # SELECT + ID + FROM + ID + WHERE + ID + OPERADOR + ID
    campo = tokens[1].valor
    tabla = tokens[3].valor
    condicion_campo = tokens[5].valor
    operador = tokens[6].valor
    valor = tokens[7].valor
    return f"SELECT {campo} FROM {tabla} WHERE {condicion_campo} {operador} {valor}"

def accion_ordenamiento(tokens):
    # SELECT + ID + FROM + ID + ORDER + ID
    campo = tokens[1].valor
    tabla = tokens[3].valor
    orden_campo = tokens[5].valor
    return f"SELECT {campo} FROM {tabla} ORDER BY {orden_campo}"

def accion_tabla_compuesta(tokens):
    # SELECT + ID + FROM + ID + ID
    campo = tokens[1].valor
    tabla_parte1 = tokens[3].valor
    tabla_parte2 = tokens[4].valor
    return f"SELECT {campo} FROM {tabla_parte1}_{tabla_parte2}"

def accion_completa(tokens):
    # SELECT + ID + FROM + ID + WHERE + ID + OP + ID + ORDER + ID
    campo = tokens[1].valor
    tabla = tokens[3].valor
    condicion_campo = tokens[5].valor
    operador = tokens[6].valor
    valor = tokens[7].valor
    orden_campo = tokens[9].valor
    return f"SELECT {campo} FROM {tabla} WHERE {condicion_campo} {operador} {valor} ORDER BY {orden_campo}"

def accion_lista_tres_campos(tokens):
    # SELECT + ID + SEP + ID + SEP + ID + FROM + ID
    campo1 = tokens[1].valor
    campo2 = tokens[3].valor
    campo3 = tokens[5].valor
    tabla = tokens[7].valor
    return f"SELECT {campo1}, {campo2}, {campo3} FROM {tabla}"

def accion_todos_campos(tokens):
    # SELECT + '*' + FROM + ID
    tabla = tokens[3].valor
    return f"SELECT * FROM {tabla}"

def accion_filtro_tabla_compuesta(tokens):
    # SELECT + ID + FROM + ID + ID + WHERE + ID + OP + ID
    campo = tokens[1].valor
    tabla_parte1 = tokens[3].valor
    tabla_parte2 = tokens[4].valor
    condicion_campo = tokens[6].valor
    operador = tokens[7].valor
    valor = tokens[8].valor
    return f"SELECT {campo} FROM {tabla_parte1}_{tabla_parte2} WHERE {condicion_campo} {operador} {valor}"


# Mapa de Asociación ("Configuración Assoc")
# Asocia los apuntadores definidos en el JSON con las funciones de Python de este archivo
MAPA_ASOCIACION = {
    "accion_consulta_simple": accion_consulta_simple,
    "accion_dos_campos_coma": accion_dos_campos_coma,
    "accion_dos_campos_y": accion_dos_campos_y,
    "accion_filtro_where": accion_filtro_where,
    "accion_ordenamiento": accion_ordenamiento,
    "accion_tabla_compuesta": accion_tabla_compuesta,
    "accion_completa": accion_completa,
    "accion_lista_tres_campos": accion_lista_tres_campos,
    "accion_todos_campos": accion_todos_campos,
    "accion_filtro_tabla_compuesta": accion_filtro_tabla_compuesta
}
