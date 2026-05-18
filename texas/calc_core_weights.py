# Modulo: calc_core_weights (Reescrito)
# Calcula el peso del nucleo basado en el tipo de corte y las fases.

import math
import database as db

def _find_steel_data(steel_key):
    # Buscar por clave directa o por designacion_antigua (compatibilidad)
    if steel_key in db.acero_electrico_db:
        return db.acero_electrico_db[steel_key]
    for data in db.acero_electrico_db.values():
        if data.get('designacion_antigua') == steel_key:
            return data
    return {}


def run(d):
    """Calcula el peso detallado del nucleo, considerando la geometria del corte.

    Añade soporte para valores opcionales definidos en `main.py`:
    - d.usar_valores_opcionales: flag general
    - d.acero_opcional: clave alternativa para seleccionar el acero
    - d.fa_opcional: factor de apilamiento (fa)
    - d.espesor_lamina_mm_opcional: espesor de lamina en mm
    """
    d.peso_por_escalon = []
    d.Qr_por_laminaciones = 0.0

    rho_kg_cm3 = 7.65 / 1000.0
    # Determinar el tipo de acero a usar (permite override opcional)
    acero_key = getattr(d, 'acero_opcional', None) or getattr(d, 'acero', 'M-6')
    steel_data = _find_steel_data(acero_key)

    # Espesor de lamina: preferir valor opcional si está activado
    if getattr(d, 'usar_valores_opcionales', False) and getattr(d, 'espesor_lamina_mm_opcional', None) is not None:
        espesor_lamina_cm = float(d.espesor_lamina_mm_opcional) / 10.0
    else:
        espesor_lamina_cm = steel_data.get('espesor_mm', 0.35) / 10.0

    # Factor de apilamiento (fa): preferir valor opcional si está activado
    if getattr(d, 'usar_valores_opcionales', False) and getattr(d, 'fa_opcional', None) is not None:
        factor_apilamiento = float(d.fa_opcional)
        d.fa_original = factor_apilamiento
    else:
        factor_apilamiento = float(getattr(d, 'fa_original', steel_data.get('fa', 0.975)))

    if not (getattr(d, 'anchos', None) and getattr(d, 'espesores', None)):
        return # No se puede calcular sin estas dimensiones

    for i, espesor_escalon in enumerate(getattr(d, 'espesores')):
        # Dimensiones base para el escalon actual
        b_cm = getattr(d, 'b', 0)
        c_prima_cm = getattr(d, 'c_prima', 0)
        ancho_escalon_cm = getattr(d, 'anchos')[i]
        
        # Ajustar b y c' para escalones > 1 (regla acumulativa)
        if i > 0:
            cumulative_e_cm = sum(getattr(d, 'espesores')[1:i + 1]) * 2.0
            b_cm += cumulative_e_cm
            c_prima_cm += cumulative_e_cm

        ancho_paquete_cm = espesor_escalon * 2.0
        num_laminas = int(math.ceil(ancho_paquete_cm / espesor_lamina_cm)) if espesor_lamina_cm > 0 else 0

        piezas_defs = {}
        cut_type = getattr(d, 'cut_type', 'Recto')
        fases = getattr(d, 'fases', 3)

        # --- APLICAR LOGICA SEGUN TIPO DE CORTE Y FASES ---
        if fases == 3:
            if cut_type == 'Recto':
                piezas_defs = {
                    'Pieza 1 (Columna)': {'l': b_cm + ancho_escalon_cm, 'w': ancho_escalon_cm, 'n': 3},
                    'Pieza 2 (Yugo Corto)': {'l': c_prima_cm + ancho_escalon_cm, 'w': ancho_escalon_cm, 'n': 2},
                    'Pieza 3 (Yugo Largo)': {'l': 2*c_prima_cm + ancho_escalon_cm, 'w': ancho_escalon_cm, 'n': 1}
                }
            else: # Diagonal
                a = ancho_escalon_cm
                area1 = (b_cm + (2*a + b_cm)) * a / 2.0 # Trapecio
                area_t2 = (2*c_prima_cm + a + 2*c_prima_cm + 3*a) * a / 2.0
                area_tc = a * (a/2.0) / 2.0
                area2 = area_t2 - area_tc # Trapecio con corte
                area3 = a * b_cm + (a**2) / 2.0 # Rectangulo + triangulos
                piezas_defs = {
                    'Pieza 1 (Trapecio)': {'area_cm2': area1, 'n': 3},
                    'Pieza 2 (Yugo c/corte)': {'area_cm2': area2, 'n': 2},
                    'Pieza 3 (Col. Central)': {'area_cm2': area3, 'n': 1}
                }
        elif fases == 1:
            if cut_type == 'Recto':
                piezas_defs = {
                    'Pieza 1 (Columna)': {'l': b_cm + ancho_escalon_cm, 'w': ancho_escalon_cm, 'n': 2},
                    'Pieza 2 (Yugo)': {'l': c_prima_cm + ancho_escalon_cm, 'w': ancho_escalon_cm, 'n': 2}
                }
            else: # Diagonal
                a = ancho_escalon_cm
                area1 = (b_cm + (2*a + b_cm)) * a / 2.0
                area2 = (c_prima_cm + (2*a + c_prima_cm)) * a / 2.0
                piezas_defs = {
                    'Pieza 1 (Columna)': {'area_cm2': area1, 'n': 2},
                    'Pieza 2 (Yugo)': {'area_cm2': area2, 'n': 2}
                }

        peso_total_escalon, detalles_escalon = 0.0, []
        for nombre, pieza in piezas_defs.items():
            num_piezas_total = num_laminas * pieza['n']
            volumen_cm3 = 0
            if 'area_cm2' in pieza:
                volumen_cm3 = pieza['area_cm2'] * espesor_lamina_cm
            else:
                volumen_cm3 = pieza['l'] * pieza['w'] * espesor_lamina_cm
            
            peso_total_tipo = volumen_cm3 * rho_kg_cm3 * num_piezas_total * factor_apilamiento
            
            detalle = {'nombre': nombre, 'num_piezas': num_piezas_total, 'peso_kg': peso_total_tipo}
            if 'area_cm2' in pieza:
                detalle['area_cm2'] = pieza['area_cm2']
            detalles_escalon.append(detalle)
            peso_total_escalon += peso_total_tipo

        d.peso_por_escalon.append({
            'escalon': i + 1,
            'detalles': detalles_escalon,
            'peso_total_escalon': peso_total_escalon
        })
        d.Qr_por_laminaciones += peso_total_escalon

    d.Qr = d.Qr_por_laminaciones