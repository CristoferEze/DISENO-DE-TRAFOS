# src/design_phases/core_and_lamination_weights/renderer.py
# -*- coding: utf-8 -*-

from pylatex import Section, Subsection, Command, Figure
from pylatex.utils import NoEscape, bold
import os
from . import lamination_plotters

def run(doc, d, add_step):
    """Añade la sección de reporte de pesos del núcleo al documento LaTeX."""
    with doc.create(Section('Peso de Núcleo por Laminaciones', numbering=False)):
        
        if not hasattr(d, 'peso_por_escalon') or not d.peso_por_escalon:
            doc.append("Datos para el cálculo de peso por escalón no disponibles.")
            return

        # Itera sobre los datos calculados para cada escalón
        for step_data in d.peso_por_escalon:
            step_num = step_data['escalon']
            
            with doc.create(Subsection(f"Dimensionado y Peso del Escalón {step_num}", numbering=False)):
                # 1. Mostrar los cálculos detallados de las piezas de este escalón (primero)
                if 'detalles' in step_data and step_data['detalles']:
                    for pieza_detalle in step_data['detalles']:
                        titulo = f"Cálculo Peso - {pieza_detalle.get('nombre', 'pieza')}"
                        formula = pieza_detalle.get('formula', 'N/A')
                        valores = pieza_detalle.get('valores', 'N/A')
                        resultado = f"Q = {pieza_detalle.get('peso_kg', 0.0):.3f}"
                        # use the provided add_step helper for consistent formatting
                        try:
                            add_step(
                                doc=doc,
                                titulo=titulo,
                                formula=formula,
                                valores=valores,
                                resultado=resultado,
                                unidad="kg"
                            )
                        except Exception:
                            # Fallback: append a simple line if add_step is unavailable or falla
                            linea = (f"\\textbullet\\ {pieza_detalle.get('nombre', '')}: "
                                     f"{pieza_detalle.get('num_piezas', 0)} piezas, "
                                     f"Peso: {pieza_detalle.get('peso_kg', 0.0):.3f} kg")
                            doc.append(NoEscape(linea))
                            doc.append(Command('newline'))
                
                # 2. Incluir la imagen correspondiente DESPUÉS de los cálculos
                plot_path = step_data.get('plot_path')
                if plot_path and os.path.exists(plot_path):
                    try:
                        safe_plot_path = plot_path.replace('\\', '/')
                        with doc.create(Figure(position='h!')) as fig:
                            fig.add_image(safe_plot_path, width=NoEscape(r'0.7\textwidth'))
                            fig.add_caption(f'Dimensionado de laminación para el escalón {step_num}.')
                    except Exception as e:
                        doc.append(NoEscape(fr"\textit{{Error al incluir imagen del escalón {step_num}: {e}}}"))
                else:
                    doc.append(NoEscape(fr"\textit{{No se encontró la imagen para el escalón {step_num}.}}"))
                
                # 3. Mostrar el peso total del escalón (resumen final del escalón)
                doc.append(Command('vspace', '0.5em'))
                total_escalon = step_data.get('peso_total_escalon', 0.0)
                doc.append(NoEscape(fr"\textbf{{Peso total del escalón {step_num}}}: {total_escalon:.2f} kg"))
                doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.8pt']))

        doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.8pt']))
        doc.append(Command('vspace', '1em'))
        # Mostrar el peso total final del núcleo
        peso_total_nucleo = getattr(d, 'Qr', 0.0)
        doc.append(NoEscape(fr"\textbf{{Peso Total del Núcleo (Hierro)}}: $Q_r = \sum Q_e = \mathbf{{{peso_total_nucleo:.2f}}}$ kg"))