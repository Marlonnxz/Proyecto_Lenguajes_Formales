# Casos de Uso para el Diseño de Autómatas Finitos (Nivel Léxico)

Este documento define **exclusivamente los Casos de Uso Léxicos** para diseñar los **Autómatas Finitos Deterministas (AFD)** del analizador léxico (*scanner*).

Cada caso representa el recorrido carácter por carácter de una palabra o símbolo desde el estado inicial $q_0$ hasta un **estado de aceptación** (Token) o un **estado de error/trampa**.

---

## 1. Definición del Alfabeto Formal

$$\Sigma = \{a\text{-}z, A\text{-}Z, 0\text{-}9, \text{','}, \text{' '}, \text{'\t'}, \text{'\n'}\}$$

---

## 2. Matriz de Casos de Uso Léxicos

| ID | Categoría | Lexema de Entrada | Token Emitido | Estado de Aceptación / Comportamiento |
| :--- | :--- | :--- | :--- | :--- |
| **CU-LEX-01** | Palabra Reservada `SELECT` | `"consulta"` | `Token(SELECT, 'consulta')` | Transición letra por letra hasta estado final específico de palabra clave. |
| **CU-LEX-02** | Variantes de `SELECT` | `"selecciona"`, `"muestra"`, `"lista"`, `"dame"`, `"obten"` | `Token(SELECT, <lexema>)` | Ramas del autómata que reconocen los diferentes verbos de consulta. |
| **CU-LEX-03** | Separador Coma | `","` | `Token(SEPARATOR, ',')` | Transición directa de 1 paso: $q_0 \xrightarrow{','} ((q_{sep1}))$. |
| **CU-LEX-04** | Separador Conjunción | `"y"` | `Token(SEPARATOR, 'y')` | Transición de 1 carácter seguido de espacio/delimitador. |
| **CU-LEX-05** | Frase Compuesta `FROM` | `"de la tabla"` | `Token(FROM, 'de la tabla')` | Secuencia con estados intermedios leyendo palabras y espacios (`de` $\rightarrow$ `' '` $\rightarrow$ `la` $\rightarrow$ `' '` $\rightarrow$ `tabla`). |
| **CU-LEX-06** | Variantes de `FROM` | `"desde la tabla"`, `"en la tabla"`, `"de tabla"` | `Token(FROM, <frase>)` | Autómata con bifurcaciones para las diferentes frases de origen. |
| **CU-LEX-07** | Identificador Simple | `"id"`, `"nombre"`, `"estudiantes"`, `"fecha"` | `Token(ID, <palabra>)` | Secuencia de letras $[a-zA-Z]+$ que **no** coincide con ninguna palabra reservada. |
| **CU-LEX-08** | Palabras a Ignorar (Stop-words) | `"el"`, `"los"`, `"las"`, `"un"`, `"una"`, `"campo"`, `"campos"` | *(Sin Token / Descarte)* | Llega a un estado final que limpia el buffer sin emitir token a la salida. |
| **CU-LEX-09** | Espacios en blanco | `" "`, `"\t"`, `"\n"` | *(Sin Token / Descarte)* | Bucle en el estado inicial $q_0 \xrightarrow{\text{espacio}} q_0$. |
| **CU-LEX-10** | Error Léxico (Símbolo Inválido) | `"@"`, `"$"`, `"#"`, `"%"`, `"&"` | `Error / Rechazo` | Transición inmediata hacia el **Estado Trampa / Error** ($q_{error}$). |

---

## 3. Detalle de los Casos de Uso para Diseñar los AFDs

---

### Caso 1: Reconocimiento de Palabras Reservadas (`SELECT`)
* **Propósito:** Reconocer los verbos de inicio de consulta.
* **Entradas de prueba:**
  * `"consulta"`
  * `"selecciona"`
  * `"muestra"`
  * `"lista"`
  * `"dame"`
  * `"obten"`
* **Traza del Autómata (Ejemplo con `"dame"`):**
  $$q_0 \xrightarrow{\text{'d'}} q_1 \xrightarrow{\text{'a'}} q_2 \xrightarrow{\text{'m'}} q_3 \xrightarrow{\text{'e'}} ((q_{\text{SELECT}}))$$
* **Salida:** `Token('SELECT', 'dame')`

---

### Caso 2: Reconocimiento de Frase Compuesta (`FROM`)
* **Propósito:** Reconocer secuencias de múltiples palabras que indican la tabla de origen.
* **Entradas de prueba:**
  * `"de la tabla"`
  * `"desde la tabla"`
  * `"en la tabla"`
  * `"de tabla"`
* **Traza del Autómata (Ejemplo con `"de la tabla"`):**
  $$q_0 \xrightarrow{\text{"de"}} q_1 \xrightarrow{\text{espacio}} q_2 \xrightarrow{\text{"la"}} q_3 \xrightarrow{\text{espacio}} q_4 \xrightarrow{\text{"tabla"}} ((q_{\text{FROM}}))$$
* **Salida:** `Token('FROM', 'de la tabla')`

---

### Caso 3: Reconocimiento de Identificadores (`ID`)
* **Propósito:** Reconocer nombres de columnas y nombres de tablas.
* **Condición Léxica:** Cualquier secuencia de letras que no sea palabra reservada ni stop-word.
* **Entradas de prueba:**
  * `"estudiantes"`
  * `"nombre"`
  * `"profesores"`
  * `"correo"`
* **Traza del Autómata:**
  $$q_0 \xrightarrow{[a-zA-Z]} q_{\text{letra}} \xrightarrow{[a-zA-Z]*} ((q_{\text{ID}}))$$
* **Salida:** `Token('ID', 'estudiantes')`

---

### Caso 4: Reconocimiento de Separadores (`SEPARATOR`)
* **Propósito:** Identificar comas y conjunciones usadas para separar campos.
* **Entradas de prueba:**
  * `","`
  * `"y"`
* **Traza del Autómata:**
  * Para coma: $q_0 \xrightarrow{\text{','}} ((q_{\text{SEP\_COMA}}))$
  * Para conjunción: $q_0 \xrightarrow{\text{'y'}} ((q_{\text{SEP\_Y}}))$
* **Salida:** `Token('SEPARATOR', ',')` o `Token('SEPARATOR', 'y')`

---

### Caso 5: Manejo de Palabras a Ignorar (Stop-words)
* **Propósito:** Consumir artículos y palabras de relleno sin generar tokens que ensucien la consulta.
* **Entradas de prueba:**
  * `"el"`
  * `"los"`
  * `"las"`
  * `"campo"`
  * `"campos"`
* **Comportamiento:**
  * Al llegar al final de la palabra `"campo"`, el autómata reconoce que pertenece al conjunto `IGNORAR`, descarta el texto y regresa a $q_0$.

---

### Caso 6: Detección de Errores Léxicos (Símbolos no permitidos)
* **Propósito:** Capturar caracteres fuera del alfabeto y detener la ejecución con mensaje de error.
* **Entradas de prueba:**
  * `"@"` (arroba)
  * `"$"` (signo pesos)
  * `"#"` (numeral)
  * `"123"` (números, en esta versión que solo maneja campos alfabéticos)
* **Traza del Autómata:**
  $$q_0 \xrightarrow{\text{cualquier carácter fuera de }\Sigma} (q_{\text{ERROR\_LEXICO}})$$
* **Resultado:** Lanza excepción `SyntaxError` con la posición exacta del carácter.
