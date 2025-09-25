# src/design_phases/nucleus_and_window/renderer.py
# -*- coding: utf-8 -*-

from pylatex import Section, Subsection, Math, Command
from pylatex.utils import NoEscape
# Este renderer recibirá una función add_step para añadir bloques consistentes.
def run(doc, d, add_step):
    """Añade la sección de reporte de esta fase al documento LaTeX."""
    with doc.create(Section('Cálculo del Núcleo y Ventana', numbering=False)):
        if d.fases == 3 and 'D' not in d.conn1:
            add_step(doc, r"Tensión Fase Primaria ($E_{1,fase}$)", r"E_{1,fase} = \frac{E_{1,linea}}{\sqrt{3}}", f"E_{{1,fase}} = \\frac{{{d.E1_linea:.0f}}}{{\\sqrt{{3}}}}", f"E_{{1,fase}} = {d.E1_fase:.2f}", "V")
        else:
            with doc.create(Subsection(NoEscape(r"Tensión de Fase Primaria ($E_{1,fase}$)"), numbering=False)):
                doc.append(Math(data=[NoEscape(f"E_{{1,fase}} = E_{{1,linea}} = {d.E1_fase:.2f} \\; \\mathrm{{V}}")], escape=False))
            doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.4pt']))

        E1_kv = d.E1_fase / 1000.0
        kc_n = 8 if d.S <= 10 else (10 if 10 < d.S <= 250 else 12)
        add_step(doc, "Coef. Plenitud Cobre ($K_c$)", r"K_c = \left( \frac{k_{c,n}}{30 + E_{1,kV}} \right) \times 1.15", f"K_c = \\left( \\frac{{{kc_n}}}{{30 + {E1_kv:.2f}}} \\right) \\times 1.15", f"K_c = {d.Kc:.4f}", "")
        add_step(doc, r"Flujo Magnético ($\Phi$)", r"\Phi = C \cdot \sqrt{\frac{S}{f}} \cdot 10^6", f"\\Phi = {d.C:.2f} \\cdot \\sqrt{{\\frac{{{d.S}}}{{{d.f}}}}} \\cdot 10^6", f"\\Phi = {d.flujo:,.0f}", "lineas")
        add_step(doc, "Área Neta ($A_n$)", r"A_n = \frac{\Phi}{B}", f"A_n = \\frac{{{d.flujo:,.0f}}}{{{d.B_kgauss*1000:.0f}}}", f"A_n = {d.An:.2f}", "cm^2")
        add_step(doc, "Área Bruta ($A_b$)", r"A_b = \frac{A_n}{f_a}", f"A_b = \\frac{{{d.An:.2f}}}{{{d.fa:.3f}}}", f"A_b = {d.Ab:.2f}", "cm^2")

        # --- NUEVA SECCIÓN: Renderizado de Dimensiones de Escalones ---
        with doc.create(Subsection(NoEscape(f"Dimensiones para {d.num_escalones} Escalones"), numbering=False)):
            # Si no hay datos, se muestra un mensaje simple
            if not getattr(d, 'anchos', None) or not getattr(d, 'espesores', None):
                doc.append(NoEscape("No hay dimensiones calculadas para los escalones."))
            else:
                for i, (ancho, espesor) in enumerate(zip(d.anchos, d.espesores)):
                    doc.append(NoEscape(f"Ancho $a_{{{i+1}}}$: {ancho:.2f} cm, Espesor $e_{{{i+1}}}$: {espesor:.2f} cm"))
                    doc.append(Command('newline'))
                
                doc.append(Command('vspace', '0.5em'))
                doc.append(NoEscape(r"Área Neta de Verificación: \\"))
                doc.append(Math(data=[NoEscape(f"A_{{n,verif}} = {d.An_verificacion:.2f} \\; \\mathrm{{cm^2}} \\approx {d.An:.2f} \\; \\mathrm{{cm^2}}")], escape=False))
        doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.4pt']))
        
        # --- NUEVO: Renderizado completo de las Dimensiones de la Ventana ---
        with doc.create(Subsection("Dimensiones de la Ventana", numbering=False)):
            # Área Ventana
            add_step(
                doc,
                "Área Ventana ($A_w$)",
                r"A_w = \frac{S_{VA}}{3.33 \cdot f \cdot B_T \cdot J \cdot K_c \cdot A_n}",
                f"A_w = \\frac{{{d.S*1000:.0f}}}{{3.33 \\cdot {d.f:.2f} \\cdot {d.B_tesla:.3f} \\cdot {d.J:.3f} \\cdot {d.Kc:.4f} \\cdot {d.An:.3e}}}",
                f"A_w = {d.Aw:.2f}",
                "cm^2"
            )

            # Alto de la ventana (b)
            add_step(
                doc,
                "Alto de Ventana (b)",
                r"b = \sqrt{R_w \cdot A_w}",
                f"b = \\sqrt{{{d.rel_rw:.3f} \\cdot {d.Aw:.2f}}}",
                f"b = {d.b:.2f}",
                "cm"
            )

            # Distancia entre ejes (M)
            add_step(
                doc,
                "Distancia entre Ejes (M)",
                r"M = \frac{A_w}{b} + D",
                f"M = \\frac{{{d.Aw:.2f}}}{{{d.b:.2f}}} + {d.D:.2f}",
                f"M = {d.M:.2f}",
                "cm"
            )

            # Ancho de ventana (c)
            add_step(
                doc,
                "Ancho de Ventana (c)",
                r"c = M - D",
                f"c = {d.M:.2f} - {d.D:.2f}",
                f"c = {d.c:.2f}",
                "cm"
            )

            # Ancho de ventana modificado c'
            if getattr(d, 'c_prima', None) is not None:
                add_step(
                    doc,
                    "Ancho de Ventana (c')",
                    r"c' = M - a_1",
                    f"c' = {d.M:.2f} - {d.anchos[0]:.2f}" if getattr(d, 'anchos', None) else "c' = M - a_1",
                    f"c' = {d.c_prima:.2f}",
                    "cm"
                )