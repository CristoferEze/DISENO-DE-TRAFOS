# src/design_phases/losses_and_performance/renderer.py
# -*- coding: utf-8 -*-

from pylatex import Section, Subsection, Command
from pylatex.utils import NoEscape

def run(doc, d, add_step):
    """Añade la sección de pérdidas y rendimiento a plena carga al reporte."""
    with doc.create(Section('Pérdidas y Rendimiento a Plena Carga', numbering=False)):

        with doc.create(Subsection(NoEscape(r'Pérdidas en el Cobre ($W_c$)'), numbering=False)):
            add_step(doc, r"Pérdidas Específicas ($P_c$)", r"P_c = 2.44 \cdot J^2",
                     fr"P_c = 2.44 \cdot ({d.J:.2f})^2",
                     fr"P_c = {getattr(d, 'Pc', 0.0):.2f}", r"W/kg")

            add_step(doc, r"Pérdidas Totales ($W_c$)", r"W_c = Q_c \cdot P_c",
                     fr"W_c = {getattr(d, 'Qc_por_bobinado', 0.0):.2f} \cdot {getattr(d, 'Pc', 0.0):.2f}",
                     fr"W_c = {getattr(d, 'Wc', 0.0):.2f}", r"W")

        with doc.create(Subsection(NoEscape(r'Pérdidas en el Hierro ($W_f$)'), numbering=False)):
            doc.append(NoEscape(r"\textbf{Pérdidas Específicas ($P_f$)}"))
            doc.append(NoEscape(fr"Para acero \textbf{{{getattr(d, 'acero', '?')}}} a ${getattr(d, 'B_kgauss', 0.0):.2f}$ kGauss, el valor de tabla es:"))
            doc.append(NoEscape(fr"$$ P_f = {getattr(d, 'Pf', 0.0):.3f} \; \mathrm{{W/kg}} $$"))
            doc.append(Command('vspace', '0.5em'))

            add_step(doc, r"Pérdidas Totales ($W_f$)", r"W_f = Q_r \cdot P_f",
                     fr"W_f = {getattr(d, 'Qr', 0.0):.2f} \cdot {getattr(d, 'Pf', 0.0):.3f}",
                     fr"W_f = {getattr(d, 'Wf', 0.0):.2f}", r"W")

        with doc.create(Subsection(NoEscape(r'Rendimiento ($\eta$)'), numbering=False)):
            P_salida_W = getattr(d, 'S', 0.0) * 1000.0
            P_entrada_W = P_salida_W + getattr(d, 'Wc', 0.0) + getattr(d, 'Wf', 0.0)
            add_step(doc, r"Rendimiento ($\eta$)",
                     r"\eta = \frac{P_{salida}}{P_{salida} + W_c + W_f} \times 100\%",
                     fr"\eta = \frac{{{P_salida_W:,.0f}}}{{{P_salida_W:,.0f} + {getattr(d, 'Wc', 0.0):.2f} + {getattr(d, 'Wf', 0.0):.2f}}} \times 100\%",
                     fr"\eta = {getattr(d, 'rendimiento', 0.0):.4f}", r"\%")