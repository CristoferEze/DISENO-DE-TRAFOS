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

    # Usar densidad opcional del acero si está disponible
    if d.usar_valores_opcionales and d.rho_acero_opcional:
        rho_kg_cm3 = d.rho_acero_opcional
    else:
        rho_g_cm3 = 7.65
        rho_kg_cm3 = rho_g_cm3 / 1000.0
    
    # Obtener datos del acero incluyendo el factor de apilamiento
    steel_data = db.acero_electrico_db.get(getattr(d, 'acero', None), {})
    espesor_lamina_mm = steel_data.get('espesor_mm', 0.35)
    espesor_lamina_cm = espesor_lamina_mm / 10.0
    
    # Usar factor de apilamiento sin redondear:
    # Priorizar valor opcional si se proporcionó, luego usar d.fa_original si existe (no redondeado),
    # y finalmente el valor de la base de datos. Convertir a float para asegurar tipo numérico.
    if getattr(d, 'usar_valores_opcionales', False) and getattr(d, 'fa_opcional', None) is not None:
        factor_apilamiento = float(d.fa_opcional)
    elif hasattr(d, 'fa_original'):
        factor_apilamiento = float(d.fa_original)
    else:
        factor_apilamiento = steel_data.get('fa', 0.975)

    if getattr(d, 'anchos', None) and getattr(d, 'espesores', None):

        for i, espesor_escalon in enumerate(d.espesores):
            # --- INICIO DE LA MODIFICACIÓN: USAR DIMENSIONES PRE-CALCULADAS POR ESCALÓN ---
            # Usar las dimensiones actualizadas ya calculadas en nucleus_and_window/calculation.py
            if hasattr(d, 'b_por_escalon') and hasattr(d, 'c_prima_por_escalon'):
                b_actual_cm = d.b_por_escalon[i] if i < len(d.b_por_escalon) else d.b
                c_prima_actual_cm = d.c_prima_por_escalon[i] if i < len(d.c_prima_por_escalon) else getattr(d, 'c_prima', d.c)
            else:
                # Fallback: calcular manualmente si las listas no están disponibles
                b_actual_cm = d.b
                c_prima_actual_cm = getattr(d, 'c_prima', d.c)
                if i > 0:  # i es el step_index
                    # Sumar 2*e para todos los escalones desde el 2do (índice 1) hasta el actual
                    cumulative_e_cm = sum(d.espesores[1:i + 1]) * 2.0
                    b_actual_cm += cumulative_e_cm
                    c_prima_actual_cm += cumulative_e_cm
            # --- FIN DE LA MODIFICACIÓN ---
    
            # Calcular el ancho del paquete de laminaciones para este escalón
            ancho_paquete_cm = (espesor_escalon * 2.0) if espesor_escalon else espesor_lamina_cm
            
            # Número de láminas considerando el espesor de cada lámina
            # Fórmula: N_láminas = ancho_paquete / espesor_lámina
            num_laminas = int(math.ceil(ancho_paquete_cm / espesor_lamina_cm)) if espesor_lamina_cm > 0 else 0
    
            ancho_escalon_cm = d.anchos[i]
    
            piezas_defs = {}
            cut_type = getattr(d, 'cut_type', 'Recto')
            
            if getattr(d, 'fases', 3) == 3:
                if cut_type == 'Recto':
                    # Fórmulas corregidas para corte recto usando b_actual_cm y c_prima_actual_cm
                    piezas_defs = {
                        '1': {'l': ancho_escalon_cm + b_actual_cm, 'w': ancho_escalon_cm, 'n_por_capa': 3, 'formula': 'a + b'},
                        '2': {'l': ancho_escalon_cm + c_prima_actual_cm, 'w': ancho_escalon_cm, 'n_por_capa': 2, 'formula': "a + c'"},
                        '3': {'l': ancho_escalon_cm + 2 * c_prima_actual_cm, 'w': ancho_escalon_cm, 'n_por_capa': 1, 'formula': "a + 2*c'"}
                    }
                else:  # Diagonal - geometrías trapezoidales (usar b_actual_cm y c_prima_actual_cm)
                    # Figura 1: trapecio con base menor = b_actual_cm, base mayor = 2*a+b_actual_cm, altura = a
                    area_fig1 = (b_actual_cm + (2 * ancho_escalon_cm + b_actual_cm)) * ancho_escalon_cm / 2.0
                    # Figura 2: trapecio con agujero. Base menor = 2*c'+a, base mayor = 2*c'+3*a, altura = a
                    # Menos triángulo central de altura = a/2, base = a
                    area_trapecio_2 = (2*c_prima_actual_cm + ancho_escalon_cm + 2*c_prima_actual_cm + 3*ancho_escalon_cm) * ancho_escalon_cm / 2.0
                    area_triangulo_central = ancho_escalon_cm * (ancho_escalon_cm/2.0) / 2.0
                    area_fig2 = area_trapecio_2 - area_triangulo_central
                    # Figura 3: rectángulo + 2 triángulos. Rectángulo = a*b_actual_cm, triángulos = a²/2
                    area_fig3 = ancho_escalon_cm * b_actual_cm + (ancho_escalon_cm * ancho_escalon_cm) / 2.0
                    
                    piezas_defs = {
                        '1': {'area': area_fig1, 'w': ancho_escalon_cm, 'n_por_capa': 3, 'formula': 'Trapecio: (b + 2a + b) * a / 2'},
                        '2': {'area': area_fig2, 'w': ancho_escalon_cm, 'n_por_capa': 2, 'formula': 'Trapecio - triángulo central'},
                        '3': {'area': area_fig3, 'w': ancho_escalon_cm, 'n_por_capa': 1, 'formula': 'Rectángulo + 2 triángulos: a*b + a²/2'}
                    }
            elif getattr(d, 'fases', 3) == 1:
                if cut_type == 'Recto':
                    # Monofásico recto: usar b_actual_cm y c_prima_actual_cm
                    piezas_defs = {
                        '1': {'l': ancho_escalon_cm + b_actual_cm, 'w': ancho_escalon_cm, 'n_por_capa': 2, 'formula': 'a + b'},
                        '2': {'l': ancho_escalon_cm + c_prima_actual_cm, 'w': ancho_escalon_cm, 'n_por_capa': 2, 'formula': "a + c'"}
                    }
                else:  # Diagonal - geometrías trapezoidales para monofásico (usar valores actualizados)
                    # Figura 1: trapecio con base menor = b_actual_cm, base mayor = 2*a+b_actual_cm, altura = a
                    area_fig1_mono = (b_actual_cm + (2 * ancho_escalon_cm + b_actual_cm)) * ancho_escalon_cm / 2.0
                    # Figura 2: trapecio con base menor = c_prima_actual_cm, base mayor = 2*a+c_prima_actual_cm, altura = a
                    area_fig2_mono = (c_prima_actual_cm + (2 * ancho_escalon_cm + c_prima_actual_cm)) * ancho_escalon_cm / 2.0
                    
                    piezas_defs = {
                        '1': {'area': area_fig1_mono, 'w': ancho_escalon_cm, 'n_por_capa': 2, 'formula': 'Trapecio: (b + 2a + b) * a / 2'},
                        '2': {'area': area_fig2_mono, 'w': ancho_escalon_cm, 'n_por_capa': 2, 'formula': "Trapecio: (c' + 2a + c') * a / 2"}
                    }

            if not piezas_defs:
                continue

            peso_total_escalon = 0.0
            detalles_escalon = []

            for nombre, pieza in piezas_defs.items():
                num_piezas_total = num_laminas * pieza['n_por_capa']
                # Usar área para geometrías trapezoidales o l*w para rectangulares
                if 'area' in pieza:
                    volumen_una_lamina = pieza['area'] * espesor_lamina_cm
                    largo_efectivo = pieza['area'] / pieza['w']  # Para mostrar en las dimensiones
                else:
                    volumen_una_lamina = pieza['l'] * pieza['w'] * espesor_lamina_cm
                    largo_efectivo = pieza['l']
                # Aplicar factor de apilamiento
                peso_total_tipo = volumen_una_lamina * rho_kg_cm3 * num_piezas_total * factor_apilamiento

                # --- INICIO DE LA CORRECCIÓN ---
                # Se definen las fórmulas y valores por separado, usando las claves
                # que el renderer.py está esperando.
                
                # 1. Datos para el cálculo del NÚMERO DE PIEZAS (detallando ancho de lámina)
                formula_num_piezas = r"N_{piezas} = \frac{\text{ancho\_paquete}}{\text{espesor\_lamina}} \times n_{piezas\_por\_capa}"
                valores_num_piezas = fr"N_{{{nombre}}} = \frac{{{ancho_paquete_cm:.2f} \text{{ cm}}}}{{{espesor_lamina_cm:.4f} \text{{ cm}}}} \times {pieza['n_por_capa']} = {num_laminas} \times {pieza['n_por_capa']}"
                resultado_num_piezas = f"N = {num_piezas_total}"

                # 2. Datos para el cálculo del PESO (incluyendo factor de apilamiento)
                if 'area' in pieza:
                    formula_peso = r"Q_{pieza} = \text{Área} \times e_{lam} \times N_{piezas} \times \rho_{acero} \times f_{apilamiento}"
                    valores_peso = (
                        fr"Q_{{{nombre}}} = {pieza['area']:.2f} \times {espesor_lamina_cm:.4f} "
                        fr"\times {num_piezas_total} \times {rho_kg_cm3:.5f} \times {factor_apilamiento:.3f}"
                    )
                else:
                    formula_peso = r"Q_{pieza} = (l \times w \times e_{lam}) \times N_{piezas} \times \rho_{acero} \times f_{apilamiento}"
                    valores_peso = (
                        fr"Q_{{{nombre}}} = ({pieza['l']:.2f} \times {pieza['w']:.2f} \times {espesor_lamina_cm:.4f}) "
                        fr"\times {num_piezas_total} \times {rho_kg_cm3:.5f} \times {factor_apilamiento:.3f}"
                    )

                # Agregar información sobre la fórmula de largo específica
                formula_largo = pieza.get('formula', 'L = ?')
                
                # Preparar el detalle de la pieza
                detalle_pieza = {
                    'nombre': f'Figura {nombre}',
                    'num_piezas': num_piezas_total,
                    'peso_kg': peso_total_tipo,
                    'ancho_lamina_cm': ancho_escalon_cm,
                    'espesor_lamina_mm': espesor_lamina_mm,
                    'factor_apilamiento': factor_apilamiento,
                    'largo_cm': largo_efectivo,
                    'formula_largo': formula_largo,
                    'tipo_corte': cut_type,
                    # Guardar ambos conjuntos de datos en el diccionario con las claves correctas
                    'formula_num_piezas': formula_num_piezas,
                    'valores_num_piezas': valores_num_piezas,
                    'resultado_num_piezas': resultado_num_piezas,
                    'formula_peso': formula_peso,
                    'valores_peso': valores_peso,
                }
                
                # Agregar área si existe para geometrías trapezoidales
                if 'area' in pieza:
                    detalle_pieza['area'] = pieza['area']
                
                detalles_escalon.append(detalle_pieza)
                # --- FIN DE LA CORRECCIÓN ---
                peso_total_escalon += peso_total_tipo

            plot_path = None
            try:
                # Proveer al generador de gráficos los detalles de las piezas calculadas
                # para que los plotters usen las longitudes exactas ya determinadas.
                # Se guarda temporalmente en el objeto 'd' y se elimina después.
                if isinstance(work_dir, str) and work_dir:
                    plot_output_dir = os.path.join(work_dir, 'temp', f'step_{i + 1}')
                    os.makedirs(plot_output_dir, exist_ok=True)
                    d._detalles_para_plot = detalles_escalon
                    plot_path = lamination_plotters.generate_plot(d, output_dir=plot_output_dir, step_index=i)
                    if hasattr(d, '_detalles_para_plot'):
                        delattr(d, '_detalles_para_plot')
                else:
                    d._detalles_para_plot = detalles_escalon
                    plot_path = lamination_plotters.generate_plot(d, output_dir=f'temp/step_{i + 1}', step_index=i)
                    if hasattr(d, '_detalles_para_plot'):
                        delattr(d, '_detalles_para_plot')
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
        # Usar densidad opcional del acero si está disponible para el cálculo de fallback
        if d.usar_valores_opcionales and d.rho_acero_opcional:
            rho_hierro_kg_cm3 = d.rho_acero_opcional
        else:
            rho_hierro_kg_cm3 = 7.65 / 1000.0
            
        a1 = d.anchos[0] if getattr(d, 'anchos', None) else getattr(d, 'D', 0)
        if getattr(d, 'fases', 3) == 3:
            volumen_hierro = (3 * d.An * d.b) + (2 * d.An * getattr(d, 'L_trifasico', (2 * d.c + 2 * d.D + a1)))
            d.Qr = volumen_hierro * rho_hierro_kg_cm3
        else:
            volumen_hierro = (2 * d.An * d.b) + (2 * d.An * getattr(d, 'L_monofasico', (d.c + d.D + a1)))
            d.Qr = volumen_hierro * rho_hierro_kg_cm3