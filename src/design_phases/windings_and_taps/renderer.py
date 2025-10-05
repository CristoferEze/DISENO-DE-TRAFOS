# src/design_phases/windings_and_taps/renderer.py
# -*- coding: utf-8 -*-
# src/design_phases/windings_and_taps/renderer.py
# -*- coding: utf-8 -*-

from pylatex import Section, Subsection, Command, Math, Itemize, Figure
from pylatex.utils import NoEscape, bold
import os
from diagrams.generator import generate_connection_diagram

def run(doc, d, add_step):
    """Añade la sección de reporte de devanados al documento LaTeX."""
    
    # Función auxiliar para formatear según configuración de redondeo
    def formatear_numero(valor, decimales_default=2):
        if getattr(d, 'redondear_2_decimales', False):
            return f"{valor:.2f}"
        else:
            return f"{valor:.{decimales_default}f}"
    
    with doc.create(Section('Devanados y Corrientes', numbering=False)):
        S_dev_VA = (d.S * 1000) / d.fases

        add_step(doc, "Espiras Secundario ($N_2$)", r"N_2 = \frac{E_{2,fase} \cdot 10^8}{4.44 \cdot f \cdot \Phi}", f"N_2 = \\frac{{{formatear_numero(d.E2_fase)} \\cdot 10^8}}{{4.44 \\cdot {d.f} \\cdot {d.flujo:,.0f}}}", f"N_2 = {d.N2_fase:.0f}", "espiras")
        add_step(doc, "Corriente Primaria de Fase ($I_{1,fase}$)", r"I_{1,fase} = \frac{S_{devanado}}{E_{1,fase}}", f"I_{{1,fase}} = \\frac{{{S_dev_VA:,.0f}}}{{{formatear_numero(d.E1_fase)}}}", f"I_{{1,fase}} = {formatear_numero(d.I1_fase_nom)}", "A")
        add_step(doc, "Corriente Secundaria de Fase ($I_{2,fase}$)", r"I_{2,fase} = \frac{S_{devanado}}{E_{2,fase}}", f"I_{{2,fase}} = \\frac{{{S_dev_VA:,.0f}}}{{{formatear_numero(d.E2_fase)}}}", f"I_{{2,fase}} = {formatear_numero(d.I2_fase)}", "A")
        add_step(doc, "Sección Conductor Primario ($s_1$)", r"s_1 = \frac{I_{1,fase}}{J}", f"s_1 = \\frac{{{formatear_numero(d.I1_fase_nom)}}}{{{formatear_numero(d.J)}}}", f"s_1 = {formatear_numero(d.s1)}", "mm^2")

        # --- MODIFICADO: Ajuste de saltos de línea para el calibre y método ---
        doc.append(Command('vspace', '0.5em'))
        doc.append(Command('newline'))
        doc.append(NoEscape(fr"\textbf{{Calibre Seleccionado (Primario):}} AWG \textbf{{{getattr(d, 'awg1', 'No encontrado')}}}"))
        doc.append(Command('newline'))
        if hasattr(d, 'metodo_peso_primario'):
            doc.append(NoEscape(fr"\textit{{Método de cálculo de peso: {d.metodo_peso_primario}}}"))
            doc.append(Command('newline'))
        doc.append(Command('vspace', '0.5em'))
        doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.4pt']))
        
        add_step(doc, "Sección Conductor Secundario ($s_2$)", r"s_2 = \frac{I_{2,fase}}{J}", f"s_2 = \\frac{{{formatear_numero(d.I2_fase)}}}{{{formatear_numero(d.J)}}}", f"s_2 = {formatear_numero(d.s2)}", "mm^2")

        # --- MODIFICADO: Ajuste de saltos de línea para el calibre y método ---
        doc.append(Command('vspace', '0.5em'))
        doc.append(Command('newline'))
        doc.append(NoEscape(fr"\textbf{{Calibre Seleccionado (Secundario):}} AWG \textbf{{{getattr(d, 'awg2', 'No encontrado')}}}"))
        doc.append(Command('newline'))
        if hasattr(d, 'metodo_peso_secundario'):
            doc.append(NoEscape(fr"\textit{{Método de cálculo de peso: {d.metodo_peso_secundario}}}"))
            doc.append(Command('newline'))
        doc.append(Command('vspace', '0.5em'))
        doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.4pt']))

    # Agregar diagrama de conexionado
    with doc.create(Section('Diagrama de Conexionado', numbering=False)):
        try:
            # Generar el diagrama (asumiendo que está en el directorio de trabajo actual)
            connection_path = generate_connection_diagram(d, output_dir='.')
            if connection_path and os.path.exists(connection_path):
                relative_path = os.path.relpath(connection_path).replace('\\', '/')
                with doc.create(Figure(position='H')) as fig:
                    fig.add_image(relative_path, width=NoEscape(r'0.7\textwidth'))
                    fig.add_caption('Diagrama de conexionado del transformador con espiras en bobinas.')
        except Exception as e:
            # Escapar caracteres especiales de LaTeX en mensajes de error
            error_msg = str(e).replace('_', r'\_').replace('%', r'\%').replace('&', r'\&').replace('#', r'\#').replace('{', r'\{').replace('}', r'\}')
            doc.append(NoEscape(f"Error al generar el diagrama de conexionado: {error_msg}"))

    with doc.create(Section('Peso del Cobre (Bobinados)', numbering=False)):
        add_step(doc, "Radio Medio de Bobina ($r_m$)", r"r_m = \frac{D}{2} + \frac{c}{4}",
                 f"r_m = \\frac{{{formatear_numero(d.D)}}}{{2}} + \\frac{{{formatear_numero(d.c)}}}{{4}}",
                 f"r_m = {formatear_numero(getattr(d, 'rm', 0.0))}", "cm")
        add_step(doc, "Longitud Media de Espira ($l_m$)", r"l_m = 2 \pi r_m",
                 f"l_m = 2 \\pi \\cdot {formatear_numero(getattr(d, 'rm', 0.0))}",
                 f"l_m = {formatear_numero(getattr(d, 'lm', 0.0))}", "m")

        # --- MODIFICADO: Se elimina el espacio excesivo entre cálculos de longitud y peso ---
        def add_simple_calc(title, formula, values, result, unit):
            doc.append(NoEscape(fr"\textbf{{{title}}}"))
            doc.append(Math(data=[NoEscape(formula)], escape=False))
            doc.append(Math(data=[NoEscape(values)], escape=False))
            unit_latex = f"\\; \\mathrm{{{unit.replace('^2', '^{{2}}')}}}" if unit else ""
            doc.append(Math(data=[NoEscape(f"{result}{unit_latex}")], escape=False))
            doc.append(Command('vspace', '0.5em'))

        with doc.create(Subsection("Bobinado Primario", numbering=False)):
            N1_max = d.tap_data[max(d.tap_data.keys())]['N_espiras'] if getattr(d, 'tap_data', None) else 0
            add_simple_calc("Longitud Total ($L_{b1}$)",
                            r"L_{b1} = l_m \cdot N_1",
                            f"L_{{b1}} = {formatear_numero(getattr(d, 'lm', 0.0))} \\cdot {N1_max}",
                            f"{formatear_numero(getattr(d, 'Lb1', 0.0))}", "m")
            add_simple_calc("Peso del Bobinado ($Q_{b1}$)",
                            r"Q_{b1} = L_{b1} \cdot (\text{peso/m})",
                            f"Q_{{b1}} = {formatear_numero(getattr(d, 'Lb1', 0.0))} \\cdot {formatear_numero(getattr(d, 'peso_conductor_primario_kg_m', 0.0))}",
                            f"{formatear_numero(getattr(d, 'Qb1', 0.0))}", "kg")
            doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.4pt']))

        with doc.create(Subsection("Bobinado Secundario", numbering=False)):
            add_simple_calc("Longitud Total ($L_{b2}$)",
                            r"L_{b2} = l_m \cdot N_2",
                            f"L_{{b2}} = {formatear_numero(getattr(d, 'lm', 0.0))} \\cdot {getattr(d, 'N2_fase', 0):.0f}",
                            f"{formatear_numero(getattr(d, 'Lb2', 0.0))}", "m")
            add_simple_calc("Peso del Bobinado ($Q_{b2}$)",
                            r"Q_{b2} = L_{b2} \cdot (\text{peso/m})",
                            f"Q_{{b2}} = {formatear_numero(getattr(d, 'Lb2', 0.0))} \\cdot {formatear_numero(getattr(d, 'peso_conductor_secundario_kg_m', 0.0))}",
                            f"{formatear_numero(getattr(d, 'Qb2', 0.0))}", "kg")
            doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.4pt']))

        # Mostrar peso total del cobre calculado por bobinado
        doc.append(NoEscape(fr"\textbf{{Peso Total del Cobre}}: $Q_c = Q_{{b1}} + Q_{{b2}} = {formatear_numero(getattr(d, 'Qb1', 0.0))} + {formatear_numero(getattr(d, 'Qb2', 0.0))} = \mathbf{{{formatear_numero(getattr(d, 'Qc_por_bobinado', 0.0))}}}$ kg"))
        doc.append(Command('vspace', '0.3em'))

        # Comparación con la fórmula propuesta: Q_c = 0.021 * Kc * b * c * (2*D + c)
        try:
            Kc_val = getattr(d, 'Kc', 0.0)
            b_val = getattr(d, 'b', 0.0)
            c_val = getattr(d, 'c', 0.0)
            D_val = getattr(d, 'D', 0.0)
            Qc_formula = 0.021 * Kc_val * b_val * c_val * (2 * D_val + c_val)
            Qc_formula_str = formatear_numero(Qc_formula)
            Qc_calc = float(getattr(d, 'Qc_por_bobinado', 0.0))
            diff_abs = Qc_calc - Qc_formula
            diff_pct = (diff_abs / Qc_formula * 100.0) if Qc_formula != 0 else 0.0
            diff_pct_str = formatear_numero(diff_pct)
            doc.append(NoEscape(fr"\textbf{{Comparación con fórmula estimada}}: $Q_c^{{fórmula}} = 0.021 \cdot K_c \cdot b \cdot c \cdot (2D + c) = \mathbf{{{Qc_formula_str}}}$ kg; Diferencia = {diff_pct_str}\%"))
        except Exception:
            doc.append(NoEscape(r"\textbf{Comparación con fórmula estimada}: No disponible (datos incompletos)"))

    # Solo mostrar sección de TAPs si existen TAPs configurados
    if d.fases == 3 and getattr(d, 'tap_data', None) and getattr(d, 'taps_pct', None):
        with doc.create(Section('Resultados por Toma (TAPs)', numbering=False)):
            with doc.create(Subsection("Número de Espiras en Primario", numbering=False)):
                with doc.create(Itemize()) as itemize:
                    for pct in sorted(d.tap_data.keys(), reverse=True):
                        data = d.tap_data[pct]
                        itemize.add_item(NoEscape(f"Toma ({pct:+.1f}\\%) : V\\_linea = {data['Vlinea']:.0f} V $\\rightarrow$ N\\_espiras = {data['N_espiras']}"))
            if getattr(d, 'tap_currents', None):
                with doc.create(Subsection("Corriente de Fase en Primario por Toma", numbering=False)):
                    with doc.create(Itemize()) as itemize:
                        for pct in sorted(d.tap_currents.keys(), reverse=True):
                            current = d.tap_currents[pct]
                            itemize.add_item(NoEscape(f"Toma ({pct:+.1f}\\%) : $I_{{1,fase}} = {formatear_numero(current)}$ A"))
            if getattr(d, 'tap_distribution', None) and d.tap_distribution:
                dist = d.tap_distribution
                with doc.create(Subsection("Distribución de Espiras del Devanado Primario", numbering=False)):
                    with doc.create(Itemize()) as itemize:
                        itemize.add_item(NoEscape(f"Sección H1 a tap {dist['taps'][0]['from']:+.1f}\\%: {dist['principal_start']} espiras"))
                        for tap_info in dist['taps']:
                            itemize.add_item(NoEscape(f"De tap {tap_info['from']:+.1f}\\% a {tap_info['to']:+.1f}\\%: {tap_info['turns']} espiras"))
                        itemize.add_item(NoEscape(f"De tap {dist['taps'][-1]['to']:+.1f}\\% a H2: {dist['principal_end']} espiras"))
                    
                    doc.append(Command('vspace', '0.5em'))
                    doc.append(NoEscape(f"Verificación Total: {dist['total_check']} (debe ser N\\_max={dist['N_max']})"))