# Proyecto: Analizador de Lenguaje Natural a SQL con Doble Capa de Autómatas

Este proyecto implementa un sistema de traducción de lenguaje natural a SQL utilizando una arquitectura de dos niveles de **Autómatas Finitos Deterministas (DFA)**.

---

## 1. Capa de Análisis Léxico (Nivel Micro)
Basado en los **10 Casos de Uso** definidos en la matriz de diseño. Esta capa convierte caracteres en tokens.

### AFD por Caracteres:

#### Casos 1 y 3
*   **Caso 1 (Palabras Reservadas SELECT)**: Autómata que reconoce "consulta", "selecciona", "muestra", "lista", "dame", "obten". Finaliza en el estado de aceptación `qSELECT`.
*   **Caso 3 (Identificadores ID)**: Reconocimiento de nombres de campos y tablas mediante la regla `[a-zA-Z]+` que no sean palabras reservadas ni stop-words.

#### Casos 2 y 5
*   **Caso 2 (Frases FROM)**: Autómata con bifurcaciones para reconocer frases compuestas como "de la tabla", "desde la tabla", "en la tabla" o "de tabla". Finaliza en `qFROM`.
*   **Caso 5 (Stop-words)**: Reconocimiento de palabras a ignorar ("el", "los", "las", "un", "una", "campo", "campos"). Estas regresan al estado inicial `q0` sin generar token.

#### Casos 4 y 6
*   **Caso 4 (Separadores)**: Reconoce la coma `,` y la conjunción `y`. Ambos generan un `Token(SEPARATOR)`.
*   **Caso 6 (Errores Léxicos)**: Estado de error `qERROR_LEXICO` para caracteres no permitidos como `@`, `$`, `#`, `&` o números fuera de contexto.

---

## 2. Capa de Análisis Sintáctico (Nivel Macro)
Ubicada en `reglas.json` y procesada por `SintacticoDinamico.py`. Esta capa valida la **secuencia de tokens**.

### Funcionamiento Dinámico
El sistema carga 10 reglas sintácticas enunciadas en un archivo JSON. Cada regla representa un autómata donde las transiciones no son caracteres, sino los **Tokens** generados en la fase anterior.

### Las 10 Reglas Sintácticas en `reglas.json`:

| ID | Nombre de la Regla | Estructura de Transiciones (Tokens) |
|:---|:---|:---|
| 1 | Consulta Simple | SELECT → ID → FROM → ID |
| 2 | Lista (Coma) | SELECT → ID → SEPARATOR → ID → FROM → ID |
| 3 | Lista (Conector 'y') | SELECT → ID → SEPARATOR → ID → FROM → ID |
| 4 | Filtro WHERE | ... → FROM → ID → WHERE_CLAUSE → ID → OPERADOR → ID |
| 5 | Ordenamiento | ... → FROM → ID → ORDER_CLAUSE → ID |
| 6 | Tabla Compuesta | ... → FROM → ID → ID |
| 7 | Consulta Maestra | SELECT + Campos + FROM + Tabla + WHERE + ORDER |
| 8 | Lista Triple | SELECT → ID → SEP → ID → SEP → ID → FROM → ID |
| 9 | Todos los Campos | SELECT → '*' (ID) → FROM → ID |
| 10| Filtro + Tabla Comp. | SELECT → ID → FROM → ID → ID → WHERE + ... |

---

## 3. Cómo funciona el código completo

1.  **Entrada**: El usuario escribe: `"consulta id y nombre de la tabla usuarios"`.
2.  **Lexer (`AnalisisLexico.py`)**: 
    *   Aplica los autómatas de **Julian, Harold y Marlon**.
    *   Genera la lista: `[Token(SELECT, "consulta"), Token(ID, "id"), Token(SEPARATOR, "y"), Token(ID, "nombre"), Token(FROM, "de la tabla"), Token(ID, "usuarios")]`.
3.  **Parser (`SintacticoDinamico.py`)**:
    *   Carga los autómatas de `reglas.json`.
    *   Evalúa la lista de tokens contra cada regla. En este caso, el autómata de la **Regla 3** llega a un estado final de aceptación.
4.  **Resultado**: Se confirma que la sintaxis es válida según la Regla 3.

## Ejecución
Para ejecutar el sistema completo con validación dinámica:
```bash
python SintacticoDinamico.py
```

