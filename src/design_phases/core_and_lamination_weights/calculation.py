# src/design_phases/core_and_lamination_weights/calculation.py
# -*- coding: utf-8 -*-

import math
from core import database as db
from . import lamination_plotters

def run(d):
    """Calcula el peso del núcleo detallado por cada escalón y sus laminaciones."""
    d.peso_por_escalon = []
    d.Qr_por_laminaciones = 0.0

    rho_g_cm3 = 7.65
    rho_kg_cm3 = rho_g_cm3 / 1000.0  # Densidad en kg/cm^3 para los cálculos
    espesor_lamina_mm = db.acero_electrico_db.get(d.acero, {}).get('espesor_mm', 0.35)
    espesor_lamina_cm = espesor_lamina_mm / 10.0

    if d.fases == 3 and getattr(d, 'anchos', None) and getattr(d, 'espesores', None):
 
        for i, espesor_escalon in enumerate(d.espesores):
            ancho_paquete_cm = (espesor_escalon * 2.0) if espesor_escalon else espesor_lamina_cm
            num_laminas = int(math.ceil(ancho_paquete_cm / espesor_lamina_cm)) if espesor_lamina_cm > 0 else 0
 
            # Obtener el ancho de la laminación para el escalón actual (en cm)
            ancho_escalon_cm = d.anchos[i]
 
            # Definir piezas usando el ancho del escalón actual
            piezas_defs = {
                '1': {'l': d.b + ancho_escalon_cm, 'w': ancho_escalon_cm, 'n_por_capa': 3},
                '2': {'l': d.c + ancho_escalon_cm, 'w': ancho_escalon_cm, 'n_por_capa': 2},
                '3': {'l': d.c * 2.0 + ancho_escalon_cm, 'w': ancho_escalon_cm, 'n_por_capa': 1}
            }

            peso_total_escalon = 0.0
            detalles_escalon = []

            for nombre, pieza in piezas_defs.items():
                # --- LÓGICA DE CÁLCULO (sin cambios) ---
                volumen_una_lamina = pieza['l'] * pieza['w'] * espesor_lamina_cm
                peso_una_lamina_kg = volumen_una_lamina * rho_kg_cm3
                peso_total_tipo = peso_una_lamina_kg * num_laminas * pieza['n_por_capa']
                
                # --- NUEVO: Guardar fórmulas y valores para el reporte ---
                formula_latex = r"Q_{pieza} = (l \cdot w \cdot e_{lam}) \cdot N_{lam} \cdot n_{piezas} \cdot \rho_{acero}"
                valores_latex = (
                    fr"Q_{{{nombre}}} = ({pieza['l']:.2f} \cdot {pieza['w']:.2f} \cdot {espesor_lamina_cm:.4f}) "
                    fr"\cdot {num_laminas} \cdot {pieza['n_por_capa']} \cdot {rho_kg_cm3:.5f}"
                )
    
                detalles_escalon.append({
                    'nombre': f'Figura {nombre}',
                    'num_piezas': num_laminas * pieza['n_por_capa'],
                    'peso_kg': peso_total_tipo,
                    'formula': formula_latex,
                    'valores': valores_latex
                })
                peso_total_escalon += peso_total_tipo

            # --- NUEVO: Generar y guardar la ruta del gráfico para este escalón ---
            plot_path = None
            try:
                plot_path = lamination_plotters.generate_plot(d, output_dir=f'temp/step_{i + 1}', step_index=i)
            except Exception as e:
                # No interrumpir el cálculo si falla el dibujo; registrar advertencia en consola
                print(f"Advertencia: No se pudo generar el gráfico para el escalón {i+1}. Error: {e}")

            d.peso_por_escalon.append({
                'escalon': i + 1,
                'detalles': detalles_escalon,
                'peso_total_escalon': peso_total_escalon,
                'plot_path': plot_path
            })
            d.Qr_por_laminaciones += peso_total_escalon

    # Establecer d.Qr usando laminaciones si se calculó
    if getattr(d, 'Qr_por_laminaciones', 0):
        d.Qr = d.Qr_por_laminaciones
    else:
        # fallback volumétrico
        rho_hierro_kg_cm3 = 7.65 / 1000.0
        a1 = d.anchos[0] if getattr(d, 'anchos', None) else getattr(d, 'D', 0)
        if d.fases == 3:
            volumen_hierro = (3 * d.An * d.b) + (2 * d.An * getattr(d, 'L_trifasico', (2 * d.c + 2 * d.D + a1)))
            d.Qr = volumen_hierro * rho_hierro_kg_cm3
        else:
            volumen_hierro = (2 * d.An * d.b) + (2 * d.An * getattr(d, 'L_monofasico', (d.c + d.D + a1)))
            d.Qr = volumen_hierro * rho_hierro_kg_cm3