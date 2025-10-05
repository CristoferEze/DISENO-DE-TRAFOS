# src/design_phases/input_data/renderer.py
# -*- coding: utf-8 -*-

from pylatex import Section, Command, Math
from pylatex.utils import NoEscape, bold

def run(doc, d):
    """Añade el encabezado y la sección de datos de entrada al documento."""
    doc.append(NoEscape(r"\begin{center}"))
    doc.append(NoEscape(r"{\Large \bfseries Reporte de Diseño de Transformador}"))
    doc.append(Command('newline'))
    doc.append(NoEscape(r"{\large Calculadora Automática}"))
    doc.append(NoEscape(r"\end{center}"))
    doc.append(Command('vspace', '1em'))
    doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.8pt']))

    with doc.create(Section('Datos de Entrada y Parámetros Base', numbering=False)):
        doc.append(bold("Potencia (S): ")); doc.append(f"{d.S} kVA, ")
        doc.append(bold("Tensión Primaria (E1): ")); doc.append(f"{d.E1_linea} V")
        doc.append(Command('newline'))
        doc.append(bold("Tensión Secundario (E2): ")); doc.append(f"{d.E2_linea} V, ")
        doc.append(bold("Frecuencia (f): ")); doc.append(f"{d.f} Hz")
        doc.append(Command('newline'))
        doc.append(bold("Conexión: ")); doc.append(d.conn.replace('_', r'\_') + ", ")
        doc.append(bold("Tipo de Acero: ")); doc.append(d.acero.replace('_', r'\_'))
        doc.append(Command('vspace', '0.5em'))
        doc.append(Command('newline'))
        doc.append("Parámetros seleccionados de tablas:")
        doc.append(Command('newline'))

        # CORREGIDO: Usar fa_original para mostrar el valor sin redondear
        fa_display = getattr(d, 'fa_original', getattr(d, 'fa', 0.975))
        parametros_base = (
            f"B = {d.B_kgauss*1000:.0f} \\, \\mathrm{{gauss}}, "
            f"J = {d.J:.2f} \\, \\mathrm{{A/mm^2}}, "
            f"C = {d.C:.2f}, f_a = {fa_display:.3f}, K_r = {d.Kr:.3f}"
        )
        doc.append(Math(data=[NoEscape(parametros_base)], escape=False))

    doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.8pt']))