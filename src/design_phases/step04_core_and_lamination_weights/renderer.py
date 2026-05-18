# src/design_phases/core_and_lamination_weights/renderer.py
# -*- coding: utf-8 -*-

from pylatex import Section, Subsection, Command, Figure
from pylatex.utils import NoEscape, bold
import os

def run(doc, d, add_step):
    """Añade la sección de reporte de pesos del núcleo al documento LaTeX."""
    with doc.create(Section('Peso de Núcleo por Laminaciones', numbering=False)):
        
        if not hasattr(d, 'peso_por_escalon') or not d.peso_por_escalon:
            doc.append("Datos para el cálculo de peso por escalón no disponibles.")
            return

        for step_data in d.peso_por_escalon:
            step_num = step_data['escalon']
            
            with doc.create(Subsection(f"Dimensionado y Peso del Escalón {step_num}", numbering=False)):
                # Mostrar tipo de corte si está disponible
                if step_data['detalles'] and step_data['detalles'][0].get('tipo_corte'):
                    tipo_corte = step_data['detalles'][0]['tipo_corte']
                    doc.append(NoEscape(f"\\textbf{{Tipo de corte:}} {tipo_corte}"))
                    doc.append(Command('newline'))
                    doc.append(Command('vspace', '0.3em'))
                
                if 'detalles' in step_data and step_data['detalles']:
                    for pieza_detalle in step_data['detalles']:
                        
                        # 0. Mostrar información específica de la pieza según el tipo de corte
                        tipo_corte = pieza_detalle.get('tipo_corte', 'Recto')
                        
                        if tipo_corte == 'Diagonal':
                            # Para cortes diagonales, mostrar información de área
                            if 'area' in pieza_detalle:
                                area_cm2 = pieza_detalle['area']
                                doc.append(NoEscape(f"\\textbf{{Área de {pieza_detalle.get('nombre', 'pieza')}:}} {area_cm2:.2f} cm²"))
                                doc.append(Command('newline'))
                            formula_largo = pieza_detalle.get('formula_largo', '')
                            if formula_largo:
                                doc.append(NoEscape(f"\\textbf{{Fórmula:}} {formula_largo}"))
                                doc.append(Command('newline'))
                        else:
                            # Para cortes rectos, mostrar fórmula de largo como antes
                            if pieza_detalle.get('formula_largo'):
                                formula_largo = pieza_detalle['formula_largo']
                                largo_cm = pieza_detalle.get('largo_cm', 0)
                                doc.append(NoEscape(f"\\textbf{{Largo de {pieza_detalle.get('nombre', 'pieza')}:}} $L = {formula_largo} = {largo_cm:.2f}$ cm"))
                                doc.append(Command('newline'))
                        
                        # 1. Renderizar el cálculo del NÚMERO DE PIEZAS
                        try:
                            add_step(
                                doc=doc,
                                titulo=f"Número de Piezas - {pieza_detalle.get('nombre', 'pieza')}",
                                formula=pieza_detalle.get('formula_num_piezas', 'N/A'),
                                valores=pieza_detalle.get('valores_num_piezas', 'N/A'),
                                resultado=pieza_detalle.get('resultado_num_piezas', 'N = ?'),
                                unidad="piezas"
                            )
                        except Exception:
                            pass
                        
                        # 2. Renderizar el cálculo del PESO
                        num_piezas = pieza_detalle.get('num_piezas', 0)
                        try:
                            add_step(
                                doc=doc,
                                titulo=f"Cálculo Peso - {pieza_detalle.get('nombre', 'pieza')} ({num_piezas} piezas)",
                                formula=pieza_detalle.get('formula_peso', 'N/A'),
                                valores=pieza_detalle.get('valores_peso', 'N/A'),
                                resultado=f"Q = {pieza_detalle.get('peso_kg', 0.0):.3f}",
                                unidad="kg"
                            )
                        except Exception:
                            linea = (f"\\textbullet\\ {pieza_detalle.get('nombre', '')}: "
                                     f"{num_piezas} piezas, "
                                     f"Peso: {pieza_detalle.get('peso_kg', 0.0):.3f} kg")
                            doc.append(NoEscape(linea))
                            doc.append(Command('newline'))
                
                # --- INICIO DE LA SIMPLIFICACIÓN Y CORRECCIÓN ---
                plot_path = step_data.get('plot_path')
                if plot_path and os.path.exists(plot_path):
                    try:
                        # 1. Convertir la ruta absoluta a una ruta relativa al directorio actual de trabajo.
                        relative_path = os.path.relpath(plot_path)
                        # 2. Asegurar que la ruta use slashes (/) para ser compatible con LaTeX.
                        safe_plot_path = relative_path.replace('\\', '/')
                        
                        # 3. Usar el entorno Figure con posición H para evitar saltos de página
                        with doc.create(Figure(position='H')) as fig:
                            fig.add_image(safe_plot_path, width=NoEscape(r'0.6\textwidth'))
                            fig.add_caption(f'Dimensionado de laminación para el escalón {step_num}.')

                    except Exception as e:
                        # Escapar caracteres especiales de LaTeX en mensajes de error
                        error_msg = str(e).replace('_', r'\_').replace('%', r'\%').replace('&', r'\&').replace('#', r'\#').replace('{', r'\{').replace('}', r'\}')
                        doc.append(NoEscape(fr"\textit{{Error al incluir imagen del escalón {step_num}: {error_msg}}}"))
                else:
                    doc.append(NoEscape(fr"\textit{{No se encontró la imagen para el escalón {step_num}.}}"))
                # --- FIN DE LA SIMPLIFICACIÓN Y CORRECCIÓN ---
                
                doc.append(Command('vspace', '0.5em'))
                total_escalon = step_data.get('peso_total_escalon', 0.0)
                doc.append(NoEscape(fr"\textbf{{Peso total del escalón {step_num}}}: {total_escalon:.2f} kg"))
                doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.8pt']))
                doc.append(Command('newline'))
 
        doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.8pt']))
        doc.append(Command('newline'))
        doc.append(Command('vspace', '1em'))
        peso_total_nucleo = getattr(d, 'Qr', 0.0)
        doc.append(NoEscape(fr"\textbf{{Peso Total del Núcleo (Hierro)}}: $Q_r = \sum Q_e = \mathbf{{{peso_total_nucleo:.2f}}}$ kg"))