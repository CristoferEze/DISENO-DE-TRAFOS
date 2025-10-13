# Modulo: calc_core_weights (Reescrito)
# Calcula el peso del nucleo basado en el tipo de corte y las fases.

import math
import database as db

def run(d):
    """Calcula el peso detallado del nucleo, considerando la geometria del corte."""
    d.peso_por_escalon = []
    d.Qr_por_laminaciones = 0.0

    rho_kg_cm3 = 7.65 / 1000.0
    steel_data = db.acero_electrico_db.get(getattr(d, 'acero', 'M-6'), {})
    espesor_lamina_cm = steel_data.get('espesor_mm', 0.35) / 10.0
    factor_apilamiento = float(getattr(d, 'fa_original', 0.975))

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