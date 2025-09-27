# src/design_phases/nucleus_and_window/renderer.py
# -*- coding: utf-8 -*-

from pylatex import Section, Subsection, Math, Command, Figure
from pylatex.utils import NoEscape
import os

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

        with doc.create(Subsection(NoEscape(f"Dimensiones para {d.num_escalones} Escalones"), numbering=False)):
            if not getattr(d, 'anchos', None) or not getattr(d, 'espesores', None):
                doc.append("No hay dimensiones calculadas.")
            else:
                for i, (ancho, espesor) in enumerate(zip(d.anchos, d.espesores)):
                    # Corregido el error de tipeo 'espor' a 'espesor'
                    linea = f"\\textbullet\\ Ancho $a_{{{i+1}}}$: {ancho:.2f} cm, Espesor $e_{{{i+1}}}$: {espesor:.2f} cm"
                    doc.append(NoEscape(linea))
                    doc.append(Command('newline'))
                
                doc.append(Command('vspace', '0.5em'))
                doc.append(NoEscape(r"Área Neta de Verificación: \\"))
                doc.append(Math(data=[NoEscape(f"A_{{n,verif}} = {d.An_verificacion:.2f} \\; \\mathrm{{cm^2}} \\approx {d.An:.2f} \\; \\mathrm{{cm^2}}")], escape=False))
                
                # --- AÑADIR LOS GRÁFICOS (SOLUCIÓN DEFINITIVA) ---
                try:
                    core_full_path = getattr(d, 'core_plot_path', None) or getattr(d, 'core_plot_filename', None)
                    if core_full_path:
                        # USA os.path.basename PARA EXTRAER SOLO EL NOMBRE DEL ARCHIVO
                        core_basename = os.path.basename(core_full_path)
                        with doc.create(Figure(position='h!')) as fig:
                            fig.add_image(core_basename, width=NoEscape(r'0.6\textwidth'))
                            fig.add_caption('Sección transversal del núcleo.')

                    lam_full_path = getattr(d, 'lamination_plot_path', None) or getattr(d, 'lamination_plot_filename', None)
                    if lam_full_path:
                        # HACE LO MISMO PARA EL OTRO GRÁFICO
                        lam_basename = os.path.basename(lam_full_path)
                        with doc.create(Figure(position='h!')) as fig:
                            fig.add_image(lam_basename, width=NoEscape(r'0.7\textwidth'))
                            fig.add_caption('Dimensiones de las piezas de laminación.')

                except Exception as e:
                    doc.append(NoEscape(fr"\textit{{Error al incluir gráficos: {e}}}"))

        doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.4pt']))
        
        with doc.create(Subsection("Dimensiones de la Ventana", numbering=False)):
            S_VA_str = f"{d.S*1000:,.0f}"
            An_str = f"{d.An:.3f}"
            add_step(doc, "Área Ventana ($A_w$)", r"A_w = \frac{S_{VA}}{3.33 \cdot f \cdot B_T \cdot J \cdot K_c \cdot A_n}", f"A_w = \\frac{{{S_VA_str}}}{{3.33 \\cdot {d.f} \\cdot {d.B_tesla:.2f} \\cdot {d.J:.2f} \\cdot {d.Kc:.4f} \\cdot {An_str}}}", f"A_w = {d.Aw:.2f}", "cm^2")
            add_step(doc, "Alto de Ventana (b)", r"b = \sqrt{R_w \cdot A_w}", f"b = \\sqrt{{{d.rel_rw:.2f} \\cdot {d.Aw:.2f}}}", f"b = {d.b:.2f}", "cm")
            add_step(doc, "Distancia entre Ejes (M)", r"M = \frac{A_w}{b} + D", f"M = \\frac{{{d.Aw:.2f}}}{{{d.b:.2f}}} + {d.D:.2f}", f"M = {d.M:.2f}", "cm")
            add_step(doc, "Ancho de Ventana (c)", r"c = M - D", f"c = {d.M:.2f} - {d.D:.2f}", f"c = {d.c:.2f}", "cm")
            if getattr(d, 'c_prima', None) is not None:
                add_step(doc, "Ancho de Ventana (c')", r"c' = M - a_1", f"c' = {d.M:.2f} - {d.anchos[0]:.2f}", f"c' = {d.c_prima:.2f}", "cm")