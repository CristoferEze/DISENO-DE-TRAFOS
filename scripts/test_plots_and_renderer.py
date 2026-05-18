import tempfile
import os
import subprocess
import sys
from pylatex import Document
from pylatex.utils import NoEscape
import pytinytex

# Import renderer and plotters
from design_phases.step02_nucleus_and_window import core_plotter, renderer as nucleus_renderer
from diagrams import generator as conn_generator


def add_calculation_step(doc, titulo, formula, valores, resultado, unidad):
    # Minimal compatible implementation used by the renderer
    doc.append(NoEscape(f"\\textbf{{{titulo}}}"))
    doc.append(NoEscape('\\newline'))
    doc.append(NoEscape(f"{valores}"))
    doc.append(NoEscape('\\newline'))
    unidad_safe = unidad if unidad is not None else ""
    if unidad_safe:
        if "\\" in unidad_safe:
            unidad_latex = unidad_safe
        else:
            unidad_latex = f"\\mathrm{{{unidad_safe}}}"
    else:
        unidad_latex = ""
    doc.append(NoEscape(f"{resultado} \\; {unidad_latex}"))
    doc.append(NoEscape('\\newline'))


class DummyDesign:
    pass

# Build a dummy design with reasonable defaults matching what renderer expects
d = DummyDesign()
# Basic electricals
d.fases = 3
d.conn1 = 'D'
d.E1_linea = 10500
d.E1_fase = 10500
d.S = 25
d.C = 2.5
# flujo
d.flujo = 1e6
d.flujo_kilolineas = d.flujo / 1000
# B
d.B_kgauss = 1.7
d.B_tesla = d.B_kgauss / 10.0
# corriente
d.J = 3.0
# areas
d.An = 100.0
d.fa_original = 0.975
d.Ab = d.An / d.fa_original
# Kr
d.Kr_original = 0.85
d.Kr = d.Kr_original
# dimensiones
d.D = 20.0
# escalones (a_i) and e_i
# provide a couple of steps
d.anchos = [0.5 * d.D, 0.3 * d.D, 0.15 * d.D]
# compute espesor example
import math
d.espesores = []
suma = 0.0
for a in d.anchos:
    e = (math.sqrt(d.D**2 - a**2) - suma) / 2.0
    d.espesores.append(e)
    suma += 2 * e

d.An_verificacion = 2 * d.fa_original * sum([d.anchos[i] * d.espesores[i] for i in range(len(d.anchos))])
# core plot path optional
# produce core plot in temp
core_path = core_plotter.generate_core_plot(d)
if isinstance(core_path, list):
    d.core_plot_path = core_path[-1]
else:
    d.core_plot_path = core_path

# generate connection diagram
conn_path = conn_generator.generate_connection_diagram(d)

# Now render LaTeX for nucleus
with tempfile.TemporaryDirectory() as temp_dir:
    try:
        doc = Document()
        # call renderer
        nucleus_renderer.run(doc, d, add_calculation_step)
        tex = doc.dumps()
        tex_path = os.path.join(temp_dir, 'reporte.tex')
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(tex)
        print('Wrote:', tex_path)

        compiler = pytinytex.get_pdf_latex_engine() or 'pdflatex'
        print('Using compiler:', compiler)
        cmd = [compiler, '--interaction=nonstopmode', tex_path]
        proc = subprocess.run(cmd, cwd=temp_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = proc.stdout.decode('utf-8', errors='replace')
        print('Returncode:', proc.returncode)
        if proc.returncode != 0:
            print('pdflatex output:\n', out)
        else:
            print('pdflatex succeeded. Files in temp:')
            print(os.listdir(temp_dir))
    except Exception as e:
        print('Exception during test:', e)
        import traceback
        traceback.print_exc()
