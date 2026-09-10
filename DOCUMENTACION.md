# DOCUMENTACIÓN TÉCNICA: Analizador de Lenguaje Natural a SQL

## 1. Introducción
Este proyecto implementa un analizador de lenguaje natural capaz de traducir consultas en español a sentencias SQL. El sistema se basa en una arquitectura de dos niveles de autómatas: una **capa léxica** para reconocimiento de tokens y una **capa sintáctica dinámica** definida mediante reglas en formato JSON.

## 2. Arquitectura del Sistema
El núcleo del proyecto es su capacidad de procesar 10 reglas sintácticas de forma desacoplada:

*   **`AnalisisLexico.py`**: Implementa los autómatas de reconocimiento de tokens (palabras clave, identificadores, separadores).
*   **`reglas.json`**: Contiene la definición formal de los 10 autómatas sintácticos y los **apuntadores** hacia la lógica semántica.
*   **`reglas_acciones.py`**: Archivo que contiene la lógica de transformación a SQL, separando la definición de la regla de la ejecución.
*   **`SintacticoDinamico.py`**: El motor sintáctico que interpreta el JSON y ejecuta la acción correspondiente.

## 3. Configuración "Assoc" (Asociación Semántica)
Atendiendo al requerimiento de "configuración assoc", el sistema implementa un mecanismo de **mapeo dinámico**:

1.  **En `reglas.json`**: Cada regla tiene un campo `"apuntador"`, que funciona como una constante que identifica qué función lógica debe ejecutar si la regla es válida.
2.  **En `reglas_acciones.py`**: Existe un diccionario llamado `MAPA_ASOCIACION` que asocia esas constantes (los apuntadores del JSON) con funciones reales de Python.

Esto permite que el analizador sintáctico no necesite conocer la lógica interna de cada regla; simplemente "asocia" el apuntador con la función correspondiente y ejecuta la transformación.

## 4. Funcionamiento de las 10 Reglas
El sistema valida la entrada recorriendo los autómatas definidos en `reglas.json` mediante `SintacticoDinamico.py`.

### Tabla de Reglas
| ID | Nombre | Apuntador Semántico |
|:---|:---|:---|
| 1 | Consulta Simple | `accion_consulta_simple` |
| 2 | Lista (Coma) | `accion_dos_campos_coma` |
| 3 | Lista ('y') | `accion_dos_campos_y` |
| 4 | Filtro WHERE | `accion_filtro_where` |
| 5 | Ordenamiento | `accion_ordenamiento` |
| 6 | Tabla Compuesta | `accion_tabla_compuesta` |
| 7 | Consulta Completa | `accion_completa` |
| 8 | Lista Tres Campos | `accion_lista_tres_campos` |
| 9 | Todos los Campos | `accion_todos_campos` |
| 10| Filtro + Tabla Comp. | `accion_filtro_tabla_compuesta` |
