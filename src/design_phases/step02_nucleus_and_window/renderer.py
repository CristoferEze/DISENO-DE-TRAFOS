# src/design_phases/nucleus_and_window/renderer.py
# -*- coding: utf-8 -*-

from pylatex import Section, Subsection, Math, Command, Figure, Itemize
from pylatex.utils import NoEscape
import os
import math

def run(doc, d, add_step):
    """Añade la sección de reporte de esta fase al documento LaTeX."""
    with doc.create(Section('Cálculo del Núcleo y Ventana', numbering=False)):
        if d.fases == 3 and 'D' not in d.conn1:
            add_step(doc, r"Tensión Fase Primaria ($E_{1,fase}$)", r"E_{1,fase} = \frac{E_{1,linea}}{\sqrt{3}}", f"E_{{1,fase}} = \\frac{{{d.E1_linea:.0f}}}{{\\sqrt{{3}}}}", f"E_{{1,fase}} = {d.E1_fase:.2f}", "V")
        else:
            with doc.create(Subsection(NoEscape(r"Tensión de Fase Primaria ($E_{1,fase}$)"), numbering=False)):
                doc.append(Math(data=[NoEscape(f"E_{{1,fase}} = E_{{1,linea}} = {d.E1_fase:.2f} \\; \\mathrm{{V}}")], escape=False))
            doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.4pt']))
            doc.append(Command('newline'))

        E1_kv = d.E1_fase / 1000.0
        kc_n = 8 if d.S <= 10 else (10 if 10 < d.S <= 250 else 12)
        # Mostrar Kc original y redondeado
        kc_display = f"K_c = {getattr(d, 'Kc_original', d.Kc):.4f} \\rightarrow {d.Kc}"
        add_step(doc, "Coef. Plenitud Cobre ($K_c$)", r"K_c = \left( \frac{k_{c,n}}{30 + E_{1,kV}} \right)", f"K_c = \\left( \\frac{{{kc_n}}}{{30 + {E1_kv:.2f}}} \\right)", kc_display, "")
        
        # Mostrar flujo magnético en kilolineas
        flujo_display = f"\\Phi = {getattr(d, 'flujo_kilolineas', d.flujo/1000)}"
        add_step(doc, r"Flujo Magnético ($\Phi$)", r"\Phi = C \cdot \sqrt{\frac{S}{f}} \cdot 10^3", f"\\Phi = {d.C:.2f} \\cdot \\sqrt{{\\frac{{{d.S}}}{{{d.f}}}}} \\cdot 10^3", flujo_display, "kilolineas")

        # Mostrar unidades explícitas: flujo en kilolineas y B en gauss
        add_step(doc, "Área Neta ($A_n$)", r"A_n = \frac{\Phi}{B}", f"A_n = \\frac{{{d.flujo:,.0f} \\; \\mathrm{{kilolineas}}}}{{{d.B_kgauss*1000:.0f} \\; \\mathrm{{gauss}}}}", f"A_n = {d.An:.2f}", "cm^2")
        # CORREGIDO: Usar fa_original para mostrar el valor sin redondear en fórmulas
        fa_display = getattr(d, 'fa_original', getattr(d, 'fa', 0.975))
        add_step(doc, "Área Bruta ($A_b$)", r"A_b = \frac{A_n}{f_a}", f"A_b = \\frac{{{d.An:.2f} \\; \\mathrm{{cm^2}}}}{{{fa_display:.3f}}}", f"A_b = {d.Ab:.2f}", "cm^2")

        # Mostrar Kf (antes Kr) sin redondear - usar siempre el valor original
        # Para presentación pedida: mantener 3 cifras decimales
        kf_original = getattr(d, 'Kr_original', d.Kr)
        kf_display = f"K_f = {kf_original:.3f}"
        with doc.create(Subsection(NoEscape(f"Coeficiente de Plenitud del Hierro ($K_f$)"), numbering=False)):
            doc.append(Math(data=[NoEscape(kf_display)], escape=False))
        doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.4pt']))
        doc.append(Command('newline'))

        # Agregar cálculo del diámetro circunscrito D usando Kf original sin redondear
        kf_original = getattr(d, 'Kr_original', d.Kr)
        add_step(doc, "Diámetro Circunscrito ($D$)", r"D = 2 \sqrt{\frac{A_n}{\pi \cdot K_f}}", f"D = 2 \\sqrt{{\\frac{{{d.An:.2f} \\; \\mathrm{{cm^2}}}}{{\\pi \\cdot {kf_original:.6f}}}}}", f"D = {d.D:.2f}", "cm")

        with doc.create(Subsection(NoEscape(f"Cálculo de escalones con su valor a y e"), numbering=False)):
            if not getattr(d, 'anchos', None) or not getattr(d, 'espesores', None):
                doc.append("No hay dimensiones calculadas.")
            else:
                # Mostrar el desarrollo del cálculo de a_i y e_i paso a paso
                for i, (ancho, espesor) in enumerate(zip(d.anchos, d.espesores)):
                    factor = ancho / d.D if d.D else 0
                    # suma_previos = 2 * sum(e_j for j < i)
                    suma_previos = 2.0 * sum(d.espesores[:i]) if i > 0 else 0.0
                    sqrt_term = math.sqrt(d.D**2 - ancho**2) if d.D > ancho else 0.0
                    # Mostrar cálculo del ancho a_i
                    add_step(doc,
                             f"Ancho $a_{{{i+1}}}$",
                             r"a_i = \beta_i \times D",
                             f"a_{{{i+1}}} = {factor:.3f} \\times {d.D:.2f}",
                             f"a_{{{i+1}}} = {ancho:.2f}",
                             "cm")
                    # Mostrar cálculo del espesor e_i con la expresión desarrollada
                    add_step(doc,
                             f"Espesor $e_{{{i+1}}}$",
                             r"e_i = \frac{\sqrt{D^2 - a_i^2} - 2\sum_{j=1}^{i-1} e_j}{2}",
                             rf"e_{{{i+1}}} = (\sqrt{{{d.D:.2f}^2 - {ancho:.2f}^2}} - {suma_previos:.2f}) / 2 = ({sqrt_term:.2f} - {suma_previos:.2f}) / 2",
                             f"e_{{{i+1}}} = {espesor:.2f}",
                             "cm")

                doc.append("Área Neta de Verificación:")
                doc.append(Math(data=[NoEscape(f"A_{{n,verif}} = {d.An_verificacion:.2f} \\; \\mathrm{{cm^2}} \\approx {d.An:.2f} \\; \\mathrm{{cm^2}}")], escape=False))
                
                # Resumen compacto: tabla con a_i y e_i lado a lado
                try:
                    doc.append(Command('vspace', '0.5em'))
                    # Escapar guiones bajos para no introducir subíndices fuera del modo matemático
                    doc.append(NoEscape(r"\textbf{Resumen compacto de anchos y espesores (a\_i, e\_i):}"))
                    doc.append(NoEscape(r"\begin{center}"))
                    doc.append(NoEscape(r"\begin{tabular}{c c c c}"))
                    doc.append(NoEscape(r"\hline"))
                    doc.append(NoEscape(r"Escal\'on & $\beta_i$ & $a_i$ (cm) & $e_i$ (cm) \\\\"))
                    doc.append(NoEscape(r"\hline"))
                    for i, (ancho_i, espesor_i) in enumerate(zip(d.anchos, d.espesores)):
                        beta_i = (ancho_i / d.D) if getattr(d, 'D', 0) else 0.0
                        row = f"{i+1} & {beta_i:.3f} & {ancho_i:.2f} & {espesor_i:.2f} \\\\"
                        doc.append(NoEscape(row))
                    doc.append(NoEscape(r"\hline"))
                    doc.append(NoEscape(r"\end{tabular}"))
                    doc.append(NoEscape(r"\end{center}"))
                    doc.append(Command('vspace', '0.5em'))
                except Exception:
                    # Si algo falla al crear la tabla, no detener el render; mostrar un mensaje simple
                    doc.append(NoEscape(r"\textit{No fue posible generar la tabla de resumen de anchos/espesores.}"))
                # Mostrar el gráfico de la sección transversal del núcleo si existe.
                # Aceptamos rutas absolutas o nombres relativos (cuando LaTeX compila en temp_dir).
                try:
                    core_full_path = (
                        getattr(d, 'core_plot_path', None)
                        or getattr(d, 'core_plot_filename', None)
                        or (getattr(d, 'core_plot_paths', [None])[-1] if getattr(d, 'core_plot_paths', None) else None)
                    )
                    if core_full_path:
                        # Si es absoluta y existe, úsala; si es relativa, la dejaremos tal cual
                        use_path = core_full_path
                        if os.path.isabs(core_full_path):
                            if not os.path.exists(core_full_path):
                                use_path = None
                        if use_path:
                            safe_core_path = use_path.replace('\\', '/')
                            with doc.create(Figure(position='H')) as fig:
                                fig.add_image(safe_core_path, width=NoEscape(r'0.5\textwidth'))
                                fig.add_caption('Sección transversal del núcleo.')
                        else:
                            # Escapar caracteres especiales de LaTeX en mensajes de error
                            error_path = str(core_full_path).replace('_', r'\_').replace('%', r'\%').replace('&', r'\&').replace('#', r'\#').replace('{', r'\{').replace('}', r'\}')
                            doc.append(NoEscape(fr"\textit{{No se encontró la imagen absoluta de la sección transversal del núcleo: {error_path}}}"))
                except Exception as e:
                    # Escapar caracteres especiales de LaTeX en mensajes de error
                    error_msg = str(e).replace('_', r'\_').replace('%', r'\%').replace('&', r'\&').replace('#', r'\#').replace('{', r'\{').replace('}', r'\}')
                    doc.append(NoEscape(fr"\textit{{Error al incluir gráficos: {error_msg}}}"))

        doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.4pt']))
        doc.append(Command('newline'))
        
        with doc.create(Subsection("Dimensiones de la Ventana", numbering=False)):
            S_VA_str = f"{d.S*1000:,.0f}"
            An_str = f"{d.An:.3f}"
            # Usar la constante correcta según el tipo de transformador
            constante = getattr(d, 'constante_ventana', 3.33)
            add_step(doc, "Área Ventana ($A_w$)", fr"A_w = \frac{{S_{{VA}}}}{{{constante} \cdot f \cdot B_T \cdot J \cdot K_c \cdot A_n}}", f"A_w = \\frac{{{S_VA_str} \\; \\mathrm{{VA}}}}{{{constante} \\cdot {d.f} \\cdot {d.B_tesla:.2f} \\; \\mathrm{{T}} \\cdot {d.J:.2f} \\; \\mathrm{{A/mm^2}} \\cdot {d.Kc:.4f} \\cdot {An_str} \\; \\mathrm{{cm^2}}}}", f"A_w = {d.Aw:.2f}", "cm^2")
            add_step(doc, "Alto de Ventana (b)", r"b = \sqrt{R_w \cdot A_w}", f"b = \\sqrt{{{d.rel_rw:.2f} \\cdot {d.Aw:.2f}}}", f"b = {d.b:.2f}", "cm")
            add_step(doc, "Distancia entre Ejes (M)", r"M = \frac{A_w}{b} + D", f"M = \\frac{{{d.Aw:.2f}}}{{{d.b:.2f}}} + {d.D:.2f}", f"M = {d.M:.2f}", "cm")
            add_step(doc, "Ancho de Ventana (c)", r"c = M - D", f"c = {d.M:.2f} - {d.D:.2f}", f"c = {d.c:.2f}", "cm")
            if getattr(d, 'c_prima', None) is not None:
                add_step(doc, "Ancho de Ventana (c')", r"c' = M - a_1", f"c' = {d.M:.2f} - {d.anchos[0]:.2f}", f"c' = {d.c_prima:.2f}", "cm")