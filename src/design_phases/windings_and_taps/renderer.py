# src/design_phases/windings_and_taps/renderer.py
# -*- coding: utf-8 -*-

from pylatex import Section, Subsection
from pylatex.utils import NoEscape
from pylatex import Command

def run(doc, d, add_step):
    """Añade la sección de reporte de devanados al documento LaTeX."""
    with doc.create(Section('Devanados y Corrientes', numbering=False)):
        add_step(doc, "Espiras Secundario ($N_2$)", r"N_2 = \frac{E_{2,fase} \cdot 10^8}{4.44 \cdot f \cdot \Phi}", f"N_2 = \\frac{{{d.E2_fase:.2f} \\cdot 10^8}}{{4.44 \\cdot {d.f} \\cdot {d.flujo:,.0f}}}", f"N_2 = {d.N2_fase:.0f}", "espiras")
        S_dev_VA = (d.S * 1000) / d.fases
        add_step(doc, "Corriente Primaria de Fase ($I_{1,fase}$)", r"I_{1,fase} = \frac{S_{devanado}}{E_{1,fase}}", f"I_{{1,fase}} = \\frac{{{S_dev_VA:,.0f}}}{{{d.E1_fase:.2f}}}", f"I_{{1,fase}} = {d.I1_fase_nom:.2f}", "A")
        add_step(doc, "Corriente Secundaria de Fase ($I_{2,fase}$)", r"I_{2,fase} = \frac{S_{devanado}}{E_{2,fase}}", f"I_{{2,fase}} = \\frac{{{S_dev_VA:,.0f}}}{{{d.E2_fase:.2f}}}", f"I_{{2,fase}} = {d.I2_fase:.2f}", "A")
        add_step(doc, "Sección Conductor Primario ($s_1$)", r"s_1 = \frac{I_{1,fase}}{J}", f"s_1 = \\frac{{{d.I1_fase_nom:.2f}}}{{{d.J:.2f}}}", f"s_1 = {d.s1:.2f}", "mm^2")
        add_step(doc, "Sección Conductor Secundario ($s_2$)", r"s_2 = \frac{I_{2,fase}}{J}", f"s_2 = \\frac{{{d.I2_fase:.2f}}}{{{d.J:.2f}}}", f"s_2 = {d.s2:.2f}", "mm^2")

    with doc.create(Section('Resultados por Toma (TAPs)', numbering=False)):
        # Número de espiras por toma
        with doc.create(Subsection("Número de Espiras en Primario", numbering=False)):
            for pct in sorted(d.tap_data.keys(), reverse=True):
                data = d.tap_data[pct]
                linea_tap = f"\\textbullet\\ Toma ({pct:+.1f}\\%) : V\\_linea = {data['Vlinea']:.0f} V, N\\_espiras = {data['N_espiras']}"
                doc.append(NoEscape(linea_tap))
                doc.append(Command('newline'))
        
        # Corrientes de fase por toma
        if getattr(d, 'tap_currents', None):
            doc.append(Command('vspace', '1em'))
            with doc.create(Subsection("Corriente de Fase en Primario por Toma", numbering=False)):
                for pct in sorted(d.tap_currents.keys(), reverse=True):
                    current = d.tap_currents[pct]
                    linea_curr = f"\\textbullet\\ Toma ({pct:+.1f}\\%) : $I_{{1,fase}} = {current:.2f}$ A"
                    doc.append(NoEscape(linea_curr))
                    doc.append(Command('newline'))

        # Distribución de espiras
        if getattr(d, 'tap_distribution', None) and d.tap_distribution:
            dist = d.tap_distribution
            doc.append(Command('vspace', '1em'))
            with doc.create(Subsection("Distribución de Espiras del Devanado Primario", numbering=False)):
                doc.append(NoEscape(f"\\textbullet\\ Sección H1 (inicio) a tap {dist['taps'][0]['from']:+.1f}\\%: {dist['principal_start']} espiras"))
                doc.append(Command('newline'))
                for tap_info in dist['taps']:
                    doc.append(NoEscape(f"\\textbullet\\ De tap {tap_info['from']:+.1f}\\% a tap {tap_info['to']:+.1f}\\%: {tap_info['turns']} espiras"))
                    doc.append(Command('newline'))
                doc.append(NoEscape(f"\\textbullet\\ De tap {dist['taps'][-1]['to']:+.1f}\\% a H2 (final): {dist['principal_end']} espiras"))
                doc.append(Command('newline'))
                doc.append(Command('vspace', '0.5em'))
                doc.append(NoEscape(f"Verificación Total: {dist['total_check']} (debe ser igual a N\\_max={dist['N_max']})"))