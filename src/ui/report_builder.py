# src/ui/report_builder.py
# -*- coding: utf-8 -*-

from pylatex import Document, Subsection, Math, Command, Package
from pylatex.utils import NoEscape

def add_calculation_step(doc, titulo, formula, valores, resultado, unidad):
    """
    Función auxiliar para añadir un bloque de cálculo estandarizado de forma simple,
    usando tres entornos Math separados para máxima compatibilidad.
    """
    unidad_safe = unidad if unidad is not None else ""
    unidad_latex = f"\\mathrm{{{unidad_safe.replace('^2', '^{{2}}')}}}" if unidad_safe else ""
    
    with doc.create(Subsection(NoEscape(titulo), numbering=False)):
        # Estrategia simple: un entorno Math por cada línea.
        doc.append(Math(data=[NoEscape(formula)], escape=False))
        doc.append(Math(data=[NoEscape(valores)], escape=False))
        doc.append(Math(data=[NoEscape(f"{resultado} \\; {unidad_latex}")], escape=False))
    
    doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.4pt']))

def generate_full_report_document(diseno):
    """Orquesta la construcción de un documento LaTeX de una sola página larga."""
    
    # --- ENFOQUE FINAL: UNA SOLA PÁGINA LARGA Y SIN PAGINACIÓN ---
    geometry_options = {
        "paperheight": "50in",  # Altura suficiente para evitar saltos de página
        "paperwidth": "8.5in",
        "margin": "1in"
    }
    
    doc = Document(geometry_options=geometry_options)
    
    # Añadir paquetes necesarios que tu TinyTeX ya incluye
    doc.packages.append(Package('graphicx')) # Para las imágenes
    
    # Eliminar encabezados, pies de página y numeración
    doc.preamble.append(Command('pagestyle', 'empty'))

    from design_phases.input_data import renderer as input_renderer
    from design_phases.nucleus_and_window import renderer as nucleus_renderer
    from design_phases.windings_and_taps import renderer as windings_renderer
    from design_phases.weights_and_losses import renderer as weights_renderer

    input_renderer.run(doc, diseno)
    nucleus_renderer.run(doc, diseno, add_calculation_step)
    windings_renderer.run(doc, diseno, add_calculation_step)
    weights_renderer.run(doc, diseno)

    return doc