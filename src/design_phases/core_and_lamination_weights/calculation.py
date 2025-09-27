# src/design_phases/core_and_lamination_weights/calculation.py
# -*- coding: utf-8 -*-

import math
import os
from core import database as db
from . import lamination_plotters

def run(d, work_dir=None):
    """Calcula el peso del núcleo detallado por cada escalón y sus laminaciones."""
    d.peso_por_escalon = []
    d.Qr_por_laminaciones = 0.0

    rho_g_cm3 = 7.65
    rho_kg_cm3 = rho_g_cm3 / 1000.0
    espesor_lamina_mm = db.acero_electrico_db.get(getattr(d, 'acero', None), {}).get('espesor_mm', 0.35)
    espesor_lamina_cm = espesor_lamina_mm / 10.0

    if getattr(d, 'anchos', None) and getattr(d, 'espesores', None):

        for i, espesor_escalon in enumerate(d.espesores):
            ancho_paquete_cm = (espesor_escalon * 2.0) if espesor_escalon else espesor_lamina_cm
            num_laminas = int(math.ceil(ancho_paquete_cm / espesor_lamina_cm)) if espesor_lamina_cm > 0 else 0

            ancho_escalon_cm = d.anchos[i]

            piezas_defs = {}
            if getattr(d, 'fases', 3) == 3:
                piezas_defs = {
                    '1': {'l': d.b + ancho_escalon_cm, 'w': ancho_escalon_cm, 'n_por_capa': 3},
                    '2': {'l': d.c + ancho_escalon_cm, 'w': ancho_escalon_cm, 'n_por_capa': 2},
                    '3': {'l': d.c * 2.0 + ancho_escalon_cm, 'w': ancho_escalon_cm, 'n_por_capa': 1}
                }
            elif getattr(d, 'fases', 3) == 1:
                piezas_defs = {
                    '1': {'l': d.b, 'w': ancho_escalon_cm, 'n_por_capa': 2},
                    '2': {'l': d.c + (2 * ancho_escalon_cm), 'w': ancho_escalon_cm, 'n_por_capa': 2}
                }

            if not piezas_defs:
                continue

            peso_total_escalon = 0.0
            detalles_escalon = []

            for nombre, pieza in piezas_defs.items():
                num_piezas_total = num_laminas * pieza['n_por_capa']
                volumen_una_lamina = pieza['l'] * pieza['w'] * espesor_lamina_cm
                peso_total_tipo = volumen_una_lamina * rho_kg_cm3 * num_piezas_total

                # --- INICIO DE LA CORRECCIÓN ---
                # Se definen las fórmulas y valores por separado, usando las claves
                # que el renderer.py está esperando.
                
                # 1. Datos para el cálculo del NÚMERO DE PIEZAS
                formula_num_piezas = r"N_{piezas} = N_{laminas} \cdot n_{piezas\_por\_capa}"
                valores_num_piezas = fr"N_{{{nombre}}} = {num_laminas} \cdot {pieza['n_por_capa']}"
                resultado_num_piezas = f"N = {num_piezas_total}"

                # 2. Datos para el cálculo del PESO
                formula_peso = r"Q_{pieza} = (l \cdot w \cdot e_{lam}) \cdot N_{piezas} \cdot \rho_{acero}"
                valores_peso = (
                    fr"Q_{{{nombre}}} = ({pieza['l']:.2f} \cdot {pieza['w']:.2f} \cdot {espesor_lamina_cm:.4f}) "
                    fr"\cdot {num_piezas_total} \cdot {rho_kg_cm3:.5f}"
                )

                detalles_escalon.append({
                    'nombre': f'Figura {nombre}',
                    'num_piezas': num_piezas_total,
                    'peso_kg': peso_total_tipo,
                    # Guardar ambos conjuntos de datos en el diccionario con las claves correctas
                    'formula_num_piezas': formula_num_piezas,
                    'valores_num_piezas': valores_num_piezas,
                    'resultado_num_piezas': resultado_num_piezas,
                    'formula_peso': formula_peso,
                    'valores_peso': valores_peso,
                })
                # --- FIN DE LA CORRECCIÓN ---
                peso_total_escalon += peso_total_tipo

            plot_path = None
            try:
                if isinstance(work_dir, str) and work_dir:
                    plot_output_dir = os.path.join(work_dir, 'temp', f'step_{i + 1}')
                    os.makedirs(plot_output_dir, exist_ok=True)
                    plot_path = lamination_plotters.generate_plot(d, output_dir=plot_output_dir, step_index=i)
                else:
                    plot_path = lamination_plotters.generate_plot(d, output_dir=f'temp/step_{i + 1}', step_index=i)
            except Exception as e:
                print(f"Advertencia: No se pudo generar el gráfico para el escalón {i+1}. Error: {e}")

            d.peso_por_escalon.append({
                'escalon': i + 1,
                'detalles': detalles_escalon,
                'peso_total_escalon': peso_total_escalon,
                'plot_path': plot_path
            })
            d.Qr_por_laminaciones += peso_total_escalon

    if getattr(d, 'Qr_por_laminaciones', 0):
        d.Qr = d.Qr_por_laminaciones
    else:
        rho_hierro_kg_cm3 = 7.65 / 1000.0
        a1 = d.anchos[0] if getattr(d, 'anchos', None) else getattr(d, 'D', 0)
        if getattr(d, 'fases', 3) == 3:
            volumen_hierro = (3 * d.An * d.b) + (2 * d.An * getattr(d, 'L_trifasico', (2 * d.c + 2 * d.D + a1)))
            d.Qr = volumen_hierro * rho_hierro_kg_cm3
        else:
            volumen_hierro = (2 * d.An * d.b) + (2 * d.An * getattr(d, 'L_monofasico', (d.c + d.D + a1)))
            d.Qr = volumen_hierro * rho_hierro_kg_cm3