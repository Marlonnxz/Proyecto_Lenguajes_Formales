from Token import Token

SELECT_PALABRAS = {
    "consulta", "consultar", "selecciona", "seleccionar",
    "muestra", "mostrar", "lista", "listar", "dame", "obten", "obtener",
}
FROM_FRASES = [
    ("de", "la", "tabla"),
    ("desde", "la", "tabla"),
    ("en", "la", "tabla"),
    ("de", "tabla"),
]
IGNORAR = {"el", "los", "las", "un", "una", "campo", "campos"}


def _leer_palabra(texto, i):
    """Desde i (posición alfabética), devuelve (palabra, índice tras la palabra)."""
    inicio = i
    n = len(texto)
    while i < n and texto[i].isalpha():
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
    """Analizador léxico: reconoce palabras clave en español (SELECT/FROM/ID/SEPARATOR)
    para generar SQL, todo en el mismo recorrido carácter por carácter."""
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

        if char.isalpha():
            palabra, i = _leer_palabra(texto, i)
            low = palabra.lower()

            frase = _match_frase_from(texto, i, palabra)
            if frase:
                texto_frase, i = frase
                tokens.append(Token("FROM", texto_frase))
                continue

            if low in SELECT_PALABRAS:
                tokens.append(Token("SELECT", palabra))
            elif low == "y":
                tokens.append(Token("SEPARATOR", palabra))
            elif low in IGNORAR:
                pass  # artículos/preposiciones sin valor semántico
            else:
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


if __name__ == "__main__":
    frases = [
        "consulta los campos id, nombre y fecha de la tabla estudiantes",
        "muestra el campo nombre de la tabla profesores",
        "lista id, nombre, correo desde la tabla usuarios",
        "consulta los campos id, nombre y fecha de la tabla estudiantes"
    ]

    for frase in frases:
        print(f"\nFrase: {frase}")
        for t in tokenizar(frase):
            print(f"  {t}")
        print(f"  SQL -> {texto_a_sql(frase)}")

    # self-check
    assert texto_a_sql("consulta los campos id, nombre y fecha de la tabla estudiantes") == \
        "SELECT id, nombre, fecha FROM estudiantes"
    assert texto_a_sql("muestra el campo nombre de la tabla profesores") == \
        "SELECT nombre FROM profesores"
    assert texto_a_sql("lista id, nombre, correo desde la tabla usuarios") == \
        "SELECT id, nombre, correo FROM usuarios"
    assert texto_a_sql("dame los campos codigo y precio en la tabla productos") == \
        "SELECT codigo, precio FROM productos"
    try:
        texto_a_sql("consulta los campos id")  # sin FROM -> debe fallar
        assert False, "se esperaba SyntaxError por falta de tabla"
    except SyntaxError:
        pass
    print("\nSelf-check OK")

    print("\n--- Modo interactivo ---")
    print("Escribe una consulta en lenguaje natural (ej: 'consulta id de la tabla x').")
    print("Escribe 'salir' para terminar.")
    while True:
        entrada = input("\n> ").strip()
        if entrada.lower() == "salir":
            break
        if not entrada:
            continue
        try:
            tokens = tokenizar(entrada)
            for t in tokens:
                print(f"  {t}")
            print(f"  SQL -> {texto_a_sql(entrada)}")
        except SyntaxError as e:
            print(f"  Error léxico: {e}")
