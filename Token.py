# Clase que representa un Token (unidad básica del analizador léxico)
class Token:
    def __init__(self, tipo, valor):
        # tipo: Categoría del token (ej: 'SELECT', 'FROM', 'ID', 'SEPARATOR', 'EOF')
        # valor: Texto exacto que se leyó en la entrada (lexema)
        self.tipo = tipo
        self.valor = valor

    def __repr__(self):
        # Permite imprimir el token de forma clara en consola: Token(TIPO, 'valor')
        return f"Token({self.tipo}, {self.valor!r})"
