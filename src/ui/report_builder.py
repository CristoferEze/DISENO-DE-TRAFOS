# src/ui/report_builder.py
# -*- coding: utf-8 -*-

from pylatex import Document, Subsection, Math, Command, Package
from pylatex.utils import NoEscape

def add_calculation_step(doc, titulo, formula, valores, resultado, unidad):
    """
    Función auxiliar para añadir un bloque de cálculo estandarizado de forma simple.
    """
    unidad_safe = unidad if unidad is not None else ""
    unidad_latex = f"\\mathrm{{{unidad_safe.replace('^2', '^{{2}}')}}}" if unidad_safe else ""
    
    with doc.create(Subsection(NoEscape(titulo), numbering=False)):
        doc.append(Math(data=[NoEscape(formula)], escape=False))
        doc.append(Math(data=[NoEscape(valores)], escape=False))
        doc.append(Math(data=[NoEscape(f"{resultado} \\; {unidad_latex}")], escape=False))
    
    doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.4pt']))

def generate_full_report_document(diseno, work_dir=None):
    """Orquesta la construcción de un documento LaTeX, manejando cálculos y renderizado.
    Si work_dir se proporciona, cambia temporalmente el cwd a ese directorio para que
    los plotters escriban sus archivos donde pdflatex los encontrará.
    """
    
    import os
    prev_cwd = None
    try:
        if work_dir:
            prev_cwd = os.getcwd()
            os.makedirs(work_dir, exist_ok=True)
            os.chdir(work_dir)
    
        geometry_options = {
            "paperheight": "50in",
            "paperwidth": "8.5in",
            "margin": "1in"
        }
        
        doc = Document(geometry_options=geometry_options)
        doc.packages.append(Package('graphicx'))
        doc.preamble.append(Command('pagestyle', 'empty'))
     
        # --- 1. FASE DE CÁLCULO ---
        # Importar los módulos de CÁLCULO
        from design_phases.nucleus_and_window import calculation as nucleus_calc
        from design_phases.core_and_lamination_weights import calculation as core_weights_calc
        # (Aquí irían otros módulos de cálculo como windings, losses, etc.)
        # from design_phases.windings_and_taps import calculation as windings_calc
        
        # Ejecutar los cálculos en el orden de dependencia correcto.
        # El objeto 'diseno' se enriquece en cada paso.
        doc.append(NoEscape('% Fase de Cálculo: Poblando el objeto de diseño'))
        nucleus_calc.run(diseno)           # Calcula 'a' y 'e', necesarios para el siguiente paso
        core_weights_calc.run(diseno)      # Calcula el peso de laminaciones usando 'a' y 'e'
        # windings_calc.run(diseno)
     
        # --- 2. FASE DE RENDERIZADO ---
        # Importar los módulos de RENDERIZADO
        from design_phases.input_data import renderer as input_renderer
        from design_phases.nucleus_and_window import renderer as nucleus_renderer
        from design_phases.windings_and_taps import renderer as windings_renderer
        from design_phases.core_and_lamination_weights import renderer as core_weights_renderer
        from design_phases.losses_and_performance import renderer as losses_perf_renderer
        from design_phases.daily_performance import renderer as daily_perf_renderer
     
        # Ahora que 'diseno' está completo, renderizar cada sección.
        # Los renderizadores solo leen el objeto 'diseno' y escriben en 'doc'.
        doc.append(NoEscape('% Fase de Renderizado: Construyendo el documento'))
        input_renderer.run(doc, diseno)
        nucleus_renderer.run(doc, diseno, add_calculation_step)
        windings_renderer.run(doc, diseno, add_calculation_step)
        core_weights_renderer.run(doc, diseno, add_calculation_step) # Ahora tendrá los datos que necesita
        losses_perf_renderer.run(doc, diseno, add_calculation_step)
        daily_perf_renderer.run(doc, diseno)
     
        return doc
    finally:
        if prev_cwd:
            try:
                os.chdir(prev_cwd)
            except Exception:
                pass