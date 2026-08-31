# Analizador léxico: lenguaje natural → SQL

Manual de usuario de [AnalisisLexico.py](AnalisisLexico.py).

## ¿Qué hace?

Un analizador léxico (`tokenizar`) que recorre el texto **carácter por
carácter** y reconoce consultas en español que se traducen a SQL, por
ejemplo:

```
consulta los campos id, nombre y fecha de la tabla estudiantes
```
se convierte en:
```sql
SELECT id, nombre, fecha FROM estudiantes
```

## Cómo funciona el léxico

El bucle principal (`while i < n` en `tokenizar`) clasifica cada carácter y,
según el caso, arma tokens:

| Se encuentra... | Token generado | Ejemplo |
|---|---|---|
| `,` | `SEPARATOR` | separador de campos |
| letra que arma una palabra en `SELECT_PALABRAS` | `SELECT` | `consulta`, `muestra`, `lista`, `dame`, `selecciona`, `obten`, ... |
| letra que arma la palabra `y` | `SEPARATOR` | separador de campos (alternativa a la coma) |
| letra que arma una frase de `FROM_FRASES` (mira varias palabras hacia adelante) | `FROM` | `de la tabla`, `desde la tabla`, `en la tabla`, `de tabla` |
| letra que arma una palabra en `IGNORAR` | *(no genera token)* | `el`, `los`, `las`, `un`, `una`, `campo`, `campos` |
| cualquier otra palabra | `ID` | nombre de campo o de tabla |
| cualquier otro carácter | `SyntaxError` | símbolo no reconocido |

Después de tokenizar una consulta en español, `generar_sql(tokens)` recorre
los tokens: todo lo que aparece como `ID` después de `SELECT` se guarda como
campo, y todo lo que aparece como `ID` después de `FROM` se guarda como
tabla; al final arma el `SELECT ... FROM ...`.

## Cómo probarlo

### 1. Ejecutar el script

```
python AnalisisLexico.py
```

Esto corre automáticamente:
- unos ejemplos de demostración (consultas en español con sus tokens y su SQL),
- un **self-check** con `assert` (si algo falla, se ve el error en consola),
- y al final abre un **modo interactivo**.

### 2. Modo interactivo

Al final de la ejecución el programa pregunta:

```
--- Modo interactivo ---
Escribe una consulta en lenguaje natural (ej: 'consulta id de la tabla x').
Escribe 'salir' para terminar.

>
```

Ahí puedes escribir cualquier consulta y ver:
- los tokens reconocidos, uno por línea,
- el SQL generado,
- o un `Error léxico` si falta algo (campos, tabla) o hay un carácter no reconocido.

Escribe `salir` para terminar.

### 3. Desde código (Python / notebook)

```python
from AnalisisLexico import tokenizar, texto_a_sql

texto_a_sql("consulta los campos id, nombre y fecha de la tabla estudiantes")
# 'SELECT id, nombre, fecha FROM estudiantes'

tokenizar("muestra el campo nombre de la tabla profesores")  # ver tokens crudos
```

## Ejemplos de prueba

Cópialos y pégalos en el modo interactivo (o úsalos como `texto_a_sql(...)`):

| Entrada | Resultado esperado |
|---|---|
| `consulta los campos id, nombre y fecha de la tabla estudiantes` | `SELECT id, nombre, fecha FROM estudiantes` |
| `muestra el campo nombre de la tabla profesores` | `SELECT nombre FROM profesores` |
| `lista id, nombre, correo desde la tabla usuarios` | `SELECT id, nombre, correo FROM usuarios` |
| `dame los campos codigo y precio en la tabla productos` | `SELECT codigo, precio FROM productos` |
| `selecciona id de tabla ventas` | `SELECT id FROM ventas` |
| `consulta los campos id` (sin tabla) | `Error léxico` — falta el `FROM` |
| `consulta id # de la tabla x` | `Error léxico: Carácter inesperado '#'...` |

## Limitaciones actuales

- No soporta `WHERE`, `JOIN`, ni condiciones.
- Los verbos y frases reconocidos son fijos (ver `SELECT_PALABRAS` y
  `FROM_FRASES` en el código); una palabra fuera de esas listas se toma como
  nombre de campo/tabla (`ID`), no como error.
- Nombres de tabla con varias palabras se concatenan con espacio tal cual
  aparecen (no hay validación adicional).
