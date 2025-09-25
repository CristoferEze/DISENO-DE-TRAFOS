# src/ui/report_builder.py
# -*- coding: utf-8 -*-

from pylatex import Document, Subsection, Math, Command
from pylatex.utils import NoEscape

def add_calculation_step(doc, titulo, formula, valores, resultado, unidad):
    """
    Función auxiliar para añadir un bloque de cálculo estandarizado.
    """
    unidad_safe = unidad if unidad is not None else ""
    unidad_latex = f"\\mathrm{{{unidad_safe.replace('^2', '^{{2}}')}}}" if unidad_safe else ""
    
    with doc.create(Subsection(NoEscape(titulo), numbering=False)):
        doc.append(Math(data=[NoEscape(formula)], escape=False))
        doc.append(Math(data=[NoEscape(valores)], escape=False))
        doc.append(Math(data=[NoEscape(f"{resultado} \\; {unidad_latex}")], escape=False))
    
    doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.4pt']))

def generate_full_report_document(diseno):
    """Orquesta la construcción del documento LaTeX completo."""
    geometry_options = {"tmargin": "1in", "lmargin": "1in", "paperheight": "40in", "paperwidth": "8.5in"}
    doc = Document(geometry_options=geometry_options, fontenc='T1', inputenc='utf8')
    
    # Importar los renderizadores sólo cuando se genera el documento para evitar
    # problemas de importación circular.
    from design_phases.input_data import renderer as input_renderer
    from design_phases.nucleus_and_window import renderer as nucleus_renderer
    from design_phases.windings_and_taps import renderer as windings_renderer

    # Llama a los renderizadores de cada fase en el orden deseado,
    # pasando la función add_calculation_step cuando sea requerida.
    input_renderer.run(doc, diseno)
    nucleus_renderer.run(doc, diseno, add_calculation_step)
    windings_renderer.run(doc, diseno, add_calculation_step)

    return doc