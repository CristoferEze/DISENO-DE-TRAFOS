# src/design_phases/windings_and_taps/renderer.py
# -*- coding: utf-8 -*-

from pylatex import Section, Subsection, Command
from pylatex.utils import NoEscape

def run(doc, d, add_step):
    """Añade la sección de reporte de devanados al documento LaTeX."""
    with doc.create(Section('Devanados y Corrientes', numbering=False)):
        S_dev_VA = (d.S * 1000) / d.fases
        
        add_step(doc, "Espiras Secundario ($N_2$)", r"N_2 = \frac{E_{2,fase} \cdot 10^8}{4.44 \cdot f \cdot \Phi}", f"N_2 = \\frac{{{d.E2_fase:.2f} \\cdot 10^8}}{{4.44 \\cdot {d.f} \\cdot {d.flujo:,.0f}}}", f"N_2 = {d.N2_fase:.0f}", "espiras")
        add_step(doc, "Corriente Primaria de Fase ($I_{1,fase}$)", r"I_{1,fase} = \frac{S_{devanado}}{E_{1,fase}}", f"I_{{1,fase}} = \\frac{{{S_dev_VA:,.0f}}}{{{d.E1_fase:.2f}}}", f"I_{{1,fase}} = {d.I1_fase_nom:.2f}", "A")
        add_step(doc, "Corriente Secundaria de Fase ($I_{2,fase}$)", r"I_{2,fase} = \frac{S_{devanado}}{E_{2,fase}}", f"I_{{2,fase}} = \\frac{{{S_dev_VA:,.0f}}}{{{d.E2_fase:.2f}}}", f"I_{{2,fase}} = {d.I2_fase:.2f}", "A")
        add_step(doc, "Sección Conductor Primario ($s_1$)", r"s_1 = \frac{I_{1,fase}}{J}", f"s_1 = \\frac{{{d.I1_fase_nom:.2f}}}{{{d.J:.2f}}}", f"s_1 = {d.s1:.2f}", "mm^2")
        # Mostrar calibre AWG seleccionado para el primario
        doc.append(NoEscape(fr"\textbf{{Calibre Seleccionado (Primario):}} AWG \textbf{{{getattr(d, 'awg1', 'No encontrado')}}}"))
        doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.4pt']))
        add_step(doc, "Sección Conductor Secundario ($s_2$)", r"s_2 = \frac{I_{2,fase}}{J}", f"s_2 = \\frac{{{d.I2_fase:.2f}}}{{{d.J:.2f}}}", f"s_2 = {d.s2:.2f}", "mm^2")
        # Mostrar calibre AWG seleccionado para el secundario
        doc.append(NoEscape(fr"\textbf{{Calibre Seleccionado (Secundario):}} AWG \textbf{{{getattr(d, 'awg2', 'No encontrado')}}}"))
        doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.4pt']))

    # --- NUEVA SECCIÓN: Peso del Cobre (por bobinado) ---
    with doc.create(Section('Peso del Cobre (Bobinados)', numbering=False)):
        # Radio medio y longitud media de espira
        add_step(doc, "Radio Medio de Bobina ($r_m$)", r"r_m = \frac{D}{2} + \frac{c}{4}",
                 f"r_m = \\frac{{{d.D:.2f}}}{{2}} + \\frac{{{d.c:.2f}}}{{4}}",
                 f"r_m = {getattr(d, 'rm', 0.0):.2f}", "cm")

        add_step(doc, "Longitud Media de Espira ($l_m$)", r"l_m = 2 \pi r_m",
                 f"l_m = 2 \\pi \\cdot {getattr(d, 'rm', 0.0):.2f}",
                 f"l_m = {getattr(d, 'lm', 0.0)*100:.2f}", "cm")

        with doc.create(Subsection("Bobinado Primario", numbering=False)):
            N1_max = d.tap_data[max(d.tap_data.keys())]['N_espiras'] if getattr(d, 'tap_data', None) else 0
            add_step(doc, "Longitud Total ($L_{b1}$)", r"L_{b1} = l_m \cdot N_1",
                     f"L_{{b1}} = {getattr(d, 'lm', 0.0):.2f} \cdot {N1_max}",
                     f"L_{{b1}} = {getattr(d, 'Lb1', 0.0):.2f}", "m")
            add_step(doc, "Peso del Bobinado ($Q_{b1}$)", r"Q_{b1} = L_{b1} \cdot (\text{peso/m})",
                     f"Q_{{b1}} = {getattr(d, 'Lb1', 0.0):.2f} \cdot {getattr(d, 'peso_conductor_primario_kg_m', 0.0)}",
                     f"Q_{{b1}} = {getattr(d, 'Qb1', 0.0):.2f}", "kg")

        with doc.create(Subsection("Bobinado Secundario", numbering=False)):
            add_step(doc, "Longitud Total ($L_{b2}$)", r"L_{b2} = l_m \cdot N_2",
                     f"L_{{b2}} = {getattr(d, 'lm', 0.0):.2f} \cdot {getattr(d, 'N2_fase', 0):.2f}",
                     f"L_{{b2}} = {getattr(d, 'Lb2', 0.0):.2f}", "m")
            add_step(doc, "Peso del Bobinado ($Q_{b2}$)", r"Q_{b2} = L_{b2} \cdot (\text{peso/m})",
                     f"Q_{{b2}} = {getattr(d, 'Lb2', 0.0):.2f} \cdot {getattr(d, 'peso_conductor_secundario_kg_m', 0.0)}",
                     f"Q_{{b2}} = {getattr(d, 'Qb2', 0.0):.2f}", "kg")

        doc.append(NoEscape(fr"\textbf{{Peso Total del Cobre}}: $Q_c = Q_{{b1}} + Q_{{b2}} = {getattr(d, 'Qb1', 0.0):.2f} + {getattr(d, 'Qb2', 0.0):.2f} = \mathbf{{{getattr(d, 'Qc_por_bobinado', 0.0):.2f}}}$ kg"))

    if d.fases == 3 and getattr(d, 'tap_data', None):
        with doc.create(Section('Resultados por Toma (TAPs)', numbering=False)):
            
            with doc.create(Subsection("Número de Espiras en Primario", numbering=False)):
                for pct in sorted(d.tap_data.keys(), reverse=True):
                    data = d.tap_data[pct]
                    linea = f"\\textbullet\\ Toma ({pct:+.1f}\\%) : V\\_linea = {data['Vlinea']:.0f} V $\\rightarrow$ N\\_espiras = {data['N_espiras']}"
                    doc.append(NoEscape(linea))
                    doc.append(Command('newline'))
            
            if getattr(d, 'tap_currents', None):
                with doc.create(Subsection("Corriente de Fase en Primario por Toma", numbering=False)):
                    for pct in sorted(d.tap_currents.keys(), reverse=True):
                        current = d.tap_currents[pct]
                        linea = f"\\textbullet\\ Toma ({pct:+.1f}\\%) : $I_{{1,fase}} = {current:.2f}$ A"
                        doc.append(NoEscape(linea))
                        doc.append(Command('newline'))

            if getattr(d, 'tap_distribution', None) and d.tap_distribution:
                dist = d.tap_distribution
                with doc.create(Subsection("Distribución de Espiras del Devanado Primario", numbering=False)):
                    doc.append(NoEscape(f"\\textbullet\\ Sección H1 a tap {dist['taps'][0]['from']:+.1f}\\%: {dist['principal_start']} espiras"))
                    doc.append(Command('newline'))
                    for tap_info in dist['taps']:
                        doc.append(NoEscape(f"\\textbullet\\ De tap {tap_info['from']:+.1f}\\% a {tap_info['to']:+.1f}\\%: {tap_info['turns']} espiras"))
                        # --- INICIO DE LA CORRECCIÓN ---
                        # Se añade el Command('newline') que faltaba en este bucle.
                        doc.append(Command('newline'))
                        # --- FIN DE LA CORRECCIÓN ---
                    doc.append(NoEscape(f"\\textbullet\\ De tap {dist['taps'][-1]['to']:+.1f}\\% a H2: {dist['principal_end']} espiras"))
                    doc.append(Command('newline'))
                    doc.append(Command('vspace', '0.5em'))
                    doc.append(NoEscape(f"Verificación Total: {dist['total_check']} (debe ser N\\_max={dist['N_max']})"))