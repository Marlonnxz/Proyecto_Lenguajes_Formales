import json
from Token import Token
from AnalisisLexico import tokenizar
from reglas_acciones import MAPA_ASOCIACION

class SintacticoDinamico:
    def __init__(self, path_reglas):
        with open(path_reglas, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.reglas = self.data['reglas']

    def procesar_consulta(self, tokens):
        # Filtramos el token EOF para el proceso del autómata
        tokens_reales = [t for t in tokens if t.tipo != "EOF"]
        
        for regla in self.reglas:
            if self._ejecutar_automata(regla['automata'], tokens_reales):
                # Si valida, usamos el apuntador para ejecutar la acción
                nombre_accion = regla.get('apuntador')
                if nombre_accion in MAPA_ASOCIACION:
                    sql = MAPA_ASOCIACION[nombre_accion](tokens_reales)
                    return regla, sql
        return None, None

    def _ejecutar_automata(self, automata, tokens):
        estado_actual = automata['inicio']
        transiciones = automata['transiciones']
        
        for token in tokens:
            if estado_actual not in transiciones:
                return False
            
            proximo_estado = transiciones[estado_actual].get(token.tipo)
            if proximo_estado:
                estado_actual = proximo_estado
            else:
                return False
        
        return estado_actual in automata['finales']

if __name__ == "__main__":
    parser = SintacticoDinamico("reglas.json")
    
    print("\n" + "="*60)
    print("Sintáctico Dinámico: Motor con Acciones Asociadas")
    print("="*60)
    
    while True:
        entrada = input("\n> ").strip()
        if entrada.lower() == "salir": break
        if not entrada: continue
        
        try:
            tokens = tokenizar(entrada)
            regla, sql = parser.procesar_consulta(tokens)
            
            if regla:
                print(f"\n  [OK] Regla aplicada: {regla['nombre']}")
                print(f"  SQL Generado: {sql}")
            else:
                print(f"\n  [Error] La consulta no coincide con ninguna regla.")
                
        except Exception as e:
            print(f"\n  [Error]: {e}")
