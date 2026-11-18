# DOCUMENTACIÓN TÉCNICA: Analizador de Lenguaje Natural a SQL

## 1. Introducción
Este proyecto implementa un analizador de lenguaje natural capaz de traducir consultas en español a sentencias SQL y ejecutarlas en un motor PostgreSQL real bajo Docker. El sistema se basa en una arquitectura de dos niveles de autómatas: una **capa léxica** para reconocimiento de tokens y una **capa sintáctica dinámica** definida mediante reglas en formato JSON.

## 2. Arquitectura del Sistema
El núcleo del proyecto procesa la gramática de forma desacoplada y modular:

*   **`AnalisisLexico.py`**: Implementa los autómatas de reconocimiento de tokens (palabras clave, identificadores, separadores, operadores relacionales, literales entre comillas, wildcard `*`, conectores lógicos `AND`/`OR`, `BETWEEN`, `GROUP BY` y dirección `ORDER_DIR`).
*   **`reglas.json`**: Contiene la definición formal de los autómatas finitos deterministas (AFD) sintácticos y los **apuntadores** hacia la lógica semántica.
*   **`reglas_acciones.py`**: Archivo que contiene la lógica de transformación a SQL (`MAPA_ASOCIACION`), separando la definición de la regla de la ejecución.
*   **`SintacticoDinamico.py`**: El motor sintáctico que interpreta el JSON y ejecuta la acción correspondiente.
*   **`db.py`**: Controlador de conexión y ejecución segura de consultas en PostgreSQL con sanitización de tipos JSON.

## 3. Configuración "Assoc" (Asociación Semántica)
Atendiendo al requerimiento de "configuración assoc", el sistema implementa un mecanismo de **mapeo dinámico**:

1.  **En `reglas.json`**: Cada regla tiene un campo `"apuntador"`, que funciona como una constante que identifica qué función lógica debe ejecutar si la regla es válida.
2.  **En `reglas_acciones.py`**: Existe un diccionario llamado `MAPA_ASOCIACION` que asocia esas constantes (los apuntadores del JSON) con funciones reales de Python.

Esto permite que el analizador sintáctico no necesite conocer la lógica interna de cada regla; simplemente "asocia" el apuntador con la función correspondiente y ejecuta la transformación.

## 4. Tabla Completa de Reglas Sintácticas

| ID | Nombre | Descripción Gramatical | Apuntador Semántico |
|:---|:---|:---|:---|
| 1 | Consulta Simple | `SELECT + ID + FROM + ID` | `accion_consulta_simple` |
| 2 | Lista (Coma) | `SELECT + ID + SEPARATOR + ID + FROM + ID` | `accion_dos_campos_coma` |
| 3 | Lista ('y') | `SELECT + ID + SEPARATOR('y') + ID + FROM + ID` | `accion_dos_campos_y` |
| 4 | Filtro WHERE | `SELECT + ID + FROM + ID + WHERE + ID + OP + VALOR` | `accion_filtro_where` |
| 5 | Ordenamiento | `SELECT + ID + FROM + ID + ORDER + ID` | `accion_ordenamiento` |
| 6 | Tabla Compuesta | `SELECT + ID + FROM + ID + ID` | `accion_tabla_compuesta` |
| 7 | Consulta Completa | `SELECT + ID + FROM + ID + WHERE + ID + OP + VALOR + ORDER + ID` | `accion_completa` |
| 8 | Lista Tres Campos | `SELECT + ID + SEP + ID + SEP + ID + FROM + ID` | `accion_lista_tres_campos` |
| 9 | Todos los Campos | `SELECT + WILDCARD + FROM + ID` (`*` o `todos los datos`) | `accion_todos_campos` |
| 10| Filtro + Tabla Comp. | `SELECT + ID + FROM + ID + ID + WHERE + ID + OP + VALOR` | `accion_filtro_tabla_compuesta` |
| 11| Consulta N Campos | `SELECT + ID + (SEPARATOR + ID)* + FROM + ID` (Ciclo en AFD) | `accion_n_campos` |
| 12| Filtro WHERE con N Campos | `SELECT + (Campos N o WILDCARD) + FROM + Tabla + WHERE + Condición` | `accion_filtro_where_n_campos` |
| 13| Ordenamiento y Dirección | `SELECT + (Campos o WILDCARD) + FROM + Tabla + ORDER + ID (+ ASC/DESC)` | `accion_ordenamiento_direccion` |
| 14| Filtro Múltiple (AND/OR) | `SELECT + Campos + FROM + Tabla + WHERE + Cond1 + (LOGICAL_OP + Cond2)+` | `accion_filtro_multiple` |
| 15| Rango BETWEEN | `SELECT + Campos + FROM + Tabla + WHERE + ID + BETWEEN + Val1 + y + Val2` | `accion_filtro_between` |
| 16| Agrupamiento GROUP BY | `SELECT + Campos + FROM + Tabla + GROUP_CLAUSE + ID` | `accion_agrupamiento` |
| 17| Consulta Maestra Avanzada | Combinación flexible de `WHERE` (simple/between/múltiple) + `GROUP BY` + `ORDER BY` | `accion_maestra_avanzada` |
