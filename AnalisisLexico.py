from Token import Token

# =============================================================================
# 1. LISTAS Y DICCIONARIOS DE PALABRAS CLAVE
# =============================================================================

# Palabras que indican una acción de selección (equivalente a SELECT en SQL)
SELECT_PALABRAS = {
    "consulta", "consultar", "selecciona", "seleccionar",
    "muestra", "mostrar", "lista", "listar", "dame", "obten", "obtener",
}

# Frases compuestas que indican de qué tabla se obtienen los datos (equivalente a FROM en SQL)
FROM_FRASES = [
    ("de", "la", "tabla"),
    ("desde", "la", "tabla"),
    ("en", "la", "tabla"),
    ("de", "tabla"),
]

# Palabras de relleno o artículos que no aportan significado a la consulta y se ignoran
IGNORAR = {"el", "los", "las", "un", "una", "campo", "campos"}


# =============================================================================
# 2. FUNCIONES AUXILIARES PARA LEER EL TEXTO
# =============================================================================

def _leer_palabra(texto, i):
    """Lee letras consecutivas desde la posición i hasta encontrar un espacio o símbolo."""
    inicio = i
    n = len(texto)
    while i < n and texto[i].isalpha():
        i += 1
    return texto[inicio:i], i


def _saltar_espacios(texto, i):
    """Avanza el índice i mientras encuentre espacios en blanco."""
    n = len(texto)
    while i < n and texto[i].isspace():
        i += 1
    return i


def _match_frase_from(texto, i, primera_palabra):
    """
    Verifica si las siguientes palabras forman una frase tipo 'de la tabla'.
    Si coincide, devuelve el texto de la frase unida y la nueva posición en el texto.
    Si no coincide, devuelve None.
    """
    # Filtra solo las frases que empiezan con la misma palabra actual
    candidatas = [f for f in FROM_FRASES if f[0] == primera_palabra.lower()]
    
    # Prueba primero las frases más largas
    for frase in sorted(candidatas, key=len, reverse=True):
        j = i
        palabras = [primera_palabra]
        
        # Revisa si las siguientes palabras coinciden con la frase esperada
        for esperado in frase[1:]:
            j = _saltar_espacios(texto, j)
            if j >= len(texto) or not texto[j].isalpha():
                break
            siguiente, j = _leer_palabra(texto, j)
            palabras.append(siguiente)
            if siguiente.lower() != esperado:
                break
        else:
            # Si todas las palabras coincidieron, retorna la frase completa
            return " ".join(palabras), j
            
    return None


# =============================================================================
# 3. ANALIZADOR LÉXICO (TOKENIZADOR)
# =============================================================================

def tokenizar(texto):
    """
    Recorre el texto carácter por carácter y lo divide en tokens:
    - SELECT: Palabras como 'consulta', 'muestra', 'selecciona'.
    - FROM: Frases como 'de la tabla', 'desde la tabla'.
    - SEPARATOR: Comas (,) o la letra 'y' para separar campos.
    - ID: Nombres de campos o nombres de tablas.
    - EOF: Marca el final del texto.
    """
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

        # Caso 3: Si es una letra, leemos la palabra completa
        if char.isalpha():
            palabra, i = _leer_palabra(texto, i)
            low = palabra.lower()

            # Verificamos si es el inicio de una frase FROM (ej: 'de la tabla')
            frase = _match_frase_from(texto, i, palabra)
            if frase:
                texto_frase, i = frase
                tokens.append(Token("FROM", texto_frase))
                continue

            # Clasificamos la palabra según corresponda
            if low in SELECT_PALABRAS:
                tokens.append(Token("SELECT", palabra))
            elif low == "y":
                tokens.append(Token("SEPARATOR", palabra))
            elif low in IGNORAR:
                # Palabras como 'el', 'los', 'campo' se omiten
                pass
            else:
                # Si no es palabra reservada, se asume que es un identificador (columna o tabla)
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


# =============================================================================
# 5. DEMOSTRACIÓN Y MODO INTERACTIVO
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ANALIZADOR LÉXICO Y TRADUCTOR A SQL")
    print("=" * 60)

    # Lista de frases de prueba
    frases = [
        "consulta los campos id, nombre y fecha de la tabla estudiantes",
        "muestra el campo nombre de la tabla profesores",
        "lista id, nombre, correo desde la tabla usuarios",
        "dame los campos codigo y precio en la tabla productos"
    ]

    print("\n--- CASOS DE PRUEBA ---")
    for frase in frases:
        print(f"\nFrase: \"{frase}\"")
        for t in tokenizar(frase):
            print(f"  {t}")
        print(f"  SQL -> {texto_a_sql(frase)}")

    # Comprobaciones automáticas para verificar que todo funcione bien
    assert texto_a_sql("consulta los campos id, nombre y fecha de la tabla estudiantes") == \
        "SELECT id, nombre, fecha FROM estudiantes"
    assert texto_a_sql("muestra el campo nombre de la tabla profesores") == \
        "SELECT nombre FROM profesores"
    assert texto_a_sql("lista id, nombre, correo desde la tabla usuarios") == \
        "SELECT id, nombre, correo FROM usuarios"
    assert texto_a_sql("dame los campos codigo y precio en la tabla productos") == \
        "SELECT codigo, precio FROM productos"
    
    # Comprobar que detecte error cuando no hay tabla
    try:
        texto_a_sql("consulta los campos id")
        assert False, "Se esperaba un error por falta de tabla"
    except SyntaxError:
        pass

    print("\n[OK] Pruebas automáticas superadas con éxito.")

    # Modo interactivo para probar frases escritas por el usuario en tiempo real
    print("\n" + "=" * 60)
    print("MODO INTERACTIVO")
    print("Escribe una consulta en lenguaje natural (ej: 'consulta id de la tabla estudiantes')")
    print("Escribe 'salir' para terminar.")
    print("=" * 60)

    while True:
        entrada = input("\n> ").strip()
        if entrada.lower() == "salir":
            print("Fin del programa.")
            break
        if not entrada:
            continue
        try:
            tokens = tokenizar(entrada)
            for t in tokens:
                print(f"  {t}")
            print(f"  SQL -> {texto_a_sql(entrada)}")
        except SyntaxError as e:
            print(f"  Error: {e}")
