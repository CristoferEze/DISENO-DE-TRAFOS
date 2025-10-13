# Modulo: utils
# Funciones de ayuda para los calculos de diseno.

import database as db

def get_promedio(tupla):
    """Calcula el promedio de una tupla de dos numeros."""
    try:
        return (tupla[0] + tupla[1]) / 2.0
    except:
        return 0.0

def sel_clave(diccionario, valor_buscado):
    """Selecciona la clave correcta en un diccionario basado en rangos."""
    clave_seleccionada = None
    for clave in sorted(diccionario.keys()):
        if valor_buscado <= clave:
            clave_seleccionada = clave
            break
    if clave_seleccionada is None:
        clave_seleccionada = max(diccionario.keys()) if diccionario else None
    return clave_seleccionada

def get_specific_iron_loss(acero_id, b_kgauss):
    """Obtiene las perdidas especificas del hierro interpolando si es necesario."""
    if not acero_id or acero_id not in db.acero_electrico_db:
        return 0.0
    
    datos_acero = db.acero_electrico_db[acero_id]
    p15 = datos_acero.get('perdidas_w_kg_15k', 0)
    p16 = datos_acero.get('perdidas_w_kg_16k', 0)
    p17 = datos_acero.get('perdidas_w_kg_17k', 0)

    if b_kgauss <= 15: return p15
    if b_kgauss >= 17: return p17
    
    if 15 < b_kgauss <= 16:
        return p15 + (p16 - p15) * (b_kgauss - 15)
    elif 16 < b_kgauss < 17:
        return p16 + (p17 - p16) * (b_kgauss - 16)
    return 0.0

def find_awg_conductor_for_section(seccion_requerida_mm2):
    """Encuentra el conductor AWG mas cercano para una seccion dada."""
    if seccion_requerida_mm2 is None or seccion_requerida_mm2 <= 0:
        return None, None
    
    mejor_coincidencia = None
    menor_diferencia = float('inf')

    for calibre, props in db.awg_conductors_db.items():
        seccion_actual = props['seccion_mm2']
        if seccion_actual >= seccion_requerida_mm2:
            diferencia = seccion_actual - seccion_requerida_mm2
            if diferencia < menor_diferencia:
                menor_diferencia = diferencia
                mejor_coincidencia = (calibre, props)

    return mejor_coincidencia if mejor_coincidencia else (None, None)