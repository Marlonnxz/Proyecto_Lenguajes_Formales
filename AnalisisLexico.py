from Token import Token

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

def _leer_palabra(texto, i):
    """Desde i, devuelve (token_alfanumerico, índice tras el token)."""
    inicio = i
    n = len(texto)
    # Aceptamos letras y números para permitir ID como "id1" o valores como "18"
    while i < n and texto[i].isalnum():
        i += 1
    return texto[inicio:i], i

def _saltar_espacios(texto, i):
    n = len(texto)
    while i < n and texto[i].isspace():
        i += 1
    return i

def _match_frase_from(texto, i, primera_palabra):
    """Si desde i sigue una frase tipo 'de la tabla', devuelve (texto_frase, nuevo_i); si no, None."""
    candidatas = [f for f in FROM_FRASES if f[0] == primera_palabra.lower()]
    for frase in sorted(candidatas, key=len, reverse=True):
        j = i
        palabras = [primera_palabra]
        for esperado in frase[1:]:
            j = _saltar_espacios(texto, j)
            if j >= len(texto) or not texto[j].isalpha():
                break
            siguiente, j = _leer_palabra(texto, j)
            palabras.append(siguiente)
            if siguiente.lower() != esperado:
                break
        else:
            return " ".join(palabras), j
    return None

def tokenizar(texto):
    """Analizador léxico que utiliza lista para reconocer frases FROM."""
    tokens = []
    i = 0
    n = len(texto)

    while i < n:
        char = texto[i]

        if char.isspace():
            i += 1
            continue

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
            palabra, next_i = _leer_palabra(texto, i)
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
                j = _saltar_espacios(texto, i)
                sig, next_i = _leer_palabra(texto, j)
                if sig.lower() == "por":
                    tokens.append(Token("ORDER_CLAUSE", "ordenar por"))
                    i = next_i
                else:
                    tokens.append(Token("ID", palabra))
            else:
                # Todo lo demás (incluyendo números) se toma como ID
                tokens.append(Token("ID", palabra))
            continue

        raise SyntaxError(f"Carácter inesperado: {char!r} en la posición {i}")

    tokens.append(Token("EOF", None))  # marca de fin de entrada
    return tokens


def generar_sql(tokens):
    """Recorre los tokens (SELECT campos... FROM tabla) y arma el SQL."""
    campos, tabla, modo = [], None, None

    for t in tokens:
        if t.tipo == "SELECT":
            modo = "campos"
        elif t.tipo == "FROM":
            modo = "tabla"
        elif t.tipo == "ID":
            if modo == "campos":
                campos.append(t.valor)
            elif modo == "tabla":
                tabla = t.valor if tabla is None else f"{tabla} {t.valor}"
        elif t.tipo == "EOF":
            break

    if not campos or not tabla:
        raise SyntaxError("No se reconoció una consulta válida (faltan campos o tabla)")

    return f"SELECT {', '.join(campos)} FROM {tabla}"


def texto_a_sql(texto):
    return generar_sql(tokenizar(texto))
