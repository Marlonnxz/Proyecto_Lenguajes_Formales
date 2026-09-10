from Token import Token

# =============================================================================
# 1. LISTAS Y DICCIONARIOS DE PALABRAS CLAVE
# =============================================================================

# Palabras que indican una acción de selección (equivalente a SELECT en SQL)
SELECT_PALABRAS = {
    "consulta", "consultar", "selecciona", "seleccionar",
    "muestra", "mostrar", "lista", "listar", "dame", "obten", "obtener",
}
# Nuevas frases clave para el soporte de las reglas
WHERE_FRASES = ["donde"]
ORDER_FRASES = ["ordenar por"]

FROM_FRASES = [
    ("de", "la", "tabla"),
    ("desde", "la", "tabla"),
    ("en", "la", "tabla"),
    ("de", "tabla"),
]

IGNORAR = {"el", "los", "las", "un", "una", "campo", "campos"}

def leer_palabra(texto, i):
    """Desde i, devuelve (token_alfanumerico, índice tras el token)."""
    inicio = i
    n = len(texto)
    # Aceptamos letras y números para permitir ID como "id1" o valores como "18"
    while i < n and texto[i].isalnum():
        i += 1
    return texto[inicio:i], i

def saltar_espacios(texto, i):
    n = len(texto)
    while i < n and texto[i].isspace():
        i += 1
    return i

def _match_frase_from(texto, i, primera_palabra):
    """Si desde i sigue una frase tipo 'de la tabla', devuelve (texto_frase, nuevo_i); si no, None."""
    candidatas = [f for f in FROM_FRASES if f[0] == primera_palabra.lower()]
    
    # Prueba primero las frases más largas
    for frase in sorted(candidatas, key=len, reverse=True):
        j = i
        palabras = [primera_palabra]
        
        # Revisa si las siguientes palabras coinciden con la frase esperada
        for esperado in frase[1:]:
            j = saltar_espacios(texto, j)
            if j >= len(texto) or not texto[j].isalpha():
                break
            siguiente, j = leer_palabra(texto, j)
            palabras.append(siguiente)
            if siguiente.lower() != esperado:
                break
        else:
            # Si todas las palabras coincidieron, retorna la frase completa
            return " ".join(palabras), j
            
    return None

def tokenizar(texto):
    """Analizador léxico que utiliza lista para reconocer frases FROM."""
    tokens = []
    i = 0
    n = len(texto)

    while i < n:
        char = texto[i]

        # Caso 1: Si es un espacio en blanco, lo ignoramos y seguimos
        if char.isspace():
            i += 1
            continue

        # Caso 2: Si es una coma, es un separador de campos
        if char == ",":
            tokens.append(Token("SEPARATOR", char))
            i += 1
            continue

        # Nuevos operadores relacionales
        if char in "<>=!":
            op = char
            if char == "!" and i + 1 < n and texto[i+1] == "=":
                op = "!="
                i += 1
            tokens.append(Token("OPERADOR", op))
            i += 1
            continue

        if char.isalnum():
            # Intentar reconocer frases del FROM
            palabra, next_i = leer_palabra(texto, i)
            frase = _match_frase_from(texto, next_i, palabra)
            
            if frase:
                texto_frase, i = frase
                tokens.append(Token("FROM", texto_frase))
                continue

            # Si no es FROM, procesar palabra normal
            i = next_i
            low = palabra.lower()

            if low in SELECT_PALABRAS:
                tokens.append(Token("SELECT", palabra))
            elif low == "y":
                tokens.append(Token("SEPARATOR", palabra))
            elif low in IGNORAR:
                pass  # artículos/preposiciones sin valor semántico
            elif low in WHERE_FRASES:
                tokens.append(Token("WHERE_CLAUSE", palabra))
            elif low == "ordenar":
                # Mirar hacia adelante para capturar "ordenar por"
                j = saltar_espacios(texto, i)
                sig, next_i = leer_palabra(texto, j)
                if sig.lower() == "por":
                    tokens.append(Token("ORDER_CLAUSE", "ordenar por"))
                    i = next_i
                else:
                    tokens.append(Token("ID", palabra))
            else:
                # Todo lo demás (incluyendo números) se toma como ID
                tokens.append(Token("ID", palabra))
            continue

        # Caso 4: Si encuentra un carácter no permitido (ej: $, #, @, números), lanza error
        raise SyntaxError(f"Carácter inesperado: {char!r} en la posición {i}")

    # Agregamos el token especial que indica el fin de la entrada
    tokens.append(Token("EOF", None))
    return tokens


# =============================================================================
# 4. TRADUCCIÓN A SQL
# =============================================================================

def generar_sql(tokens):
    """
    Toma la lista de tokens generada y construye la consulta SQL:
    SELECT <campos> FROM <tabla>
    """
    campos = []
    tabla = None
    modo = None

    for t in tokens:
        if t.tipo == "SELECT":
            modo = "campos"  # Los siguientes identificadores serán nombres de columnas
        elif t.tipo == "FROM":
            modo = "tabla"   # Los siguientes identificadores serán el nombre de la tabla
        elif t.tipo == "ID":
            if modo == "campos":
                campos.append(t.valor)
            elif modo == "tabla":
                # Si el nombre de la tabla tiene más de una palabra, se van uniendo
                tabla = t.valor if tabla is None else f"{tabla} {t.valor}"
        elif t.tipo == "EOF":
            break

    # Si falta la tabla o los campos, la consulta es inválida
    if not campos or not tabla:
        raise SyntaxError("No se reconoció una consulta válida (faltan campos o tabla)")

    # Retorna la sentencia SQL final armada
    return f"SELECT {', '.join(campos)} FROM {tabla}"


def texto_a_sql(texto):
    """Función principal que recibe el texto en lenguaje natural y devuelve la consulta SQL."""
    return generar_sql(tokenizar(texto))