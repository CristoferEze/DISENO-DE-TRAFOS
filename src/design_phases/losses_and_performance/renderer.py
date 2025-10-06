# src/design_phases/losses_and_performance/renderer.py
# -*- coding: utf-8 -*-

from pylatex import Section, Subsection, Command, Itemize
from pylatex.utils import NoEscape

def run(doc, d, add_step):
    """Añade la sección de pérdidas y rendimiento a plena carga al reporte."""
    
    # Función auxiliar para formatear según configuración de redondeo
    def formatear_numero(valor, decimales_default=2):
        if getattr(d, 'redondear_2_decimales', False):
            return f"{valor:.2f}"
        else:
            return f"{valor:.{decimales_default}f}"
    
    with doc.create(Section('Pérdidas y Rendimiento a Plena Carga', numbering=False)):

        with doc.create(Subsection(NoEscape(r'Pérdidas en el Cobre ($W_c$)'), numbering=False)):
            # Mostrar cómo se obtuvo Pc
            pc_method = getattr(d, 'Pc_calculation_method', 'Fórmula empírica (2.44 × J²)')
            doc.append(NoEscape(fr"\textbf{{Pérdidas Específicas ($P_c$) - {pc_method}}}"))
            
            if getattr(d, 'usar_valores_opcionales', False) and getattr(d, 'Pc_manual', None) is not None:
                doc.append(NoEscape(fr"Valor manual ingresado: $P_c = {formatear_numero(getattr(d, 'Pc', 0.0))}$ W/kg"))
            else:
                add_step(doc, r"Pérdidas Específicas ($P_c$)", r"P_c = 2.44 \cdot J^2",
                         fr"P_c = 2.44 \cdot ({formatear_numero(getattr(d, 'J', 0.0))})^2",
                         fr"P_c = {formatear_numero(getattr(d, 'Pc', 0.0))}", r"W/kg")

            # Mostrar peso de cobre usado en pérdidas: fórmula empírica y total (considerando fases)
            add_step(doc, r"Peso de Cobre para pérdidas (empírico)",
                     r"Q_c = " + ("0.014" if getattr(d, 'fases', 3) == 1 else "0.021") + r" \cdot K_c \cdot b \cdot c \cdot (2D + c)",
                     fr"Q_c = {('0.014' if getattr(d, 'fases', 3) == 1 else '0.021')} \cdot {formatear_numero(getattr(d, 'Kc', 1.0))} \cdot {formatear_numero(getattr(d, 'b', 0.0))} \cdot {formatear_numero(getattr(d, 'c', 0.0))} \cdot (2 \cdot {formatear_numero(getattr(d, 'D', 0.0))} + {formatear_numero(getattr(d, 'c', 0.0))})",
                     fr"Q_c = {formatear_numero(getattr(d, 'Qc_empirical_por_formula', 0.0))}", "kg")

            # Pérdidas en W usando la masa empírica del cobre
            add_step(doc, r"Pérdidas Totales ($W_c$)", r"W_c = Q_c \cdot P_c",
                     fr"W_c = {formatear_numero(getattr(d, 'Qc_empirical_por_formula', 0.0))} \cdot {formatear_numero(getattr(d, 'Pc', 0.0))}",
                     fr"W_c = {formatear_numero(getattr(d, 'Wc', 0.0))}", r"W")

            # También mostrar el peso físico calculado paso a paso (para referencia)
            doc.append(NoEscape(fr"\textbf{{Peso físico calculado (por bobinado):}} {formatear_numero(getattr(d, 'Qc_por_bobinado', 0.0))} kg"))
            doc.append(NoEscape(fr"\textbf{{Peso físico total (considerando fases):}} {formatear_numero(getattr(d, 'Qc_total', getattr(d, 'Qc_por_bobinado', 0.0)))} kg"))

        with doc.create(Subsection(NoEscape(r'Pérdidas en el Hierro ($W_f$)'), numbering=False)):
            # Mostrar cómo se obtuvo Pf
            pf_method = getattr(d, 'Pf_calculation_method', f'Valor de tabla para acero {getattr(d, "acero", "?")}')
            doc.append(NoEscape(fr"\textbf{{Pérdidas Específicas ($P_f$) - {pf_method}}}"))
            
            if getattr(d, 'usar_valores_opcionales', False) and getattr(d, 'Pf_manual', None) is not None:
                doc.append(NoEscape(fr"Valor manual ingresado: $P_f = {formatear_numero(getattr(d, 'Pf', 0.0), 3)}$ W/kg"))
            elif getattr(d, 'usar_valores_opcionales', False) and getattr(d, 'Pf_opcional', 0):
                doc.append(NoEscape(fr"Valor opcional de tabla: $P_f = {formatear_numero(getattr(d, 'Pf', 0.0), 3)}$ W/kg"))
            else:
                doc.append(NoEscape(fr"Para acero \textbf{{{getattr(d, 'acero', '?')}}} a ${formatear_numero(getattr(d, 'B_kgauss', 0.0))}$ kGauss, el valor de tabla es:"))
                doc.append(NoEscape(fr"$$ P_f = {formatear_numero(getattr(d, 'Pf', 0.0), 3)} \; \mathrm{{W/kg}} $$"))
            doc.append(Command('vspace', '0.5em'))
 
            # Masa de hierro usada para pérdidas (fórmula empírica) - usar Kf original sin redondear
            kf_used = getattr(d, 'Kf_used_for_Qf', getattr(d, 'Kr_original', getattr(d, 'Kr', 1.0)))
            add_step(doc, r"Masa de hierro (empírica) $Q_f$",
                     r"Q_f = " + ("0.012" if getattr(d, 'fases', 3) == 1 else "0.006") + r" \cdot K_f \cdot D^2 \cdot (3b + 4c + 5.87D)",
                     fr"Q_f = {('0.012' if getattr(d, 'fases', 3) == 1 else '0.006')} \cdot {kf_used:.6f} \cdot {formatear_numero(getattr(d, 'D', 0.0))}^2 \cdot (3 \cdot {formatear_numero(getattr(d, 'b', 0.0))} + 4 \cdot {formatear_numero(getattr(d, 'c', 0.0))} + 5.87 \cdot {formatear_numero(getattr(d, 'D', 0.0))})",
                     fr"Q_f = {formatear_numero(getattr(d, 'Qf_empirical', 0.0))}", "kg")

            # Mostrar detalle físico de Qr (opcional) y luego usar Qf empírica para las pérdidas
            if getattr(d, 'peso_por_escalon', None):
                doc.append(NoEscape(r"\textbf{Detalle de pesos que componen }$Q_r$:"))
                with doc.create(Itemize()) as it:
                    for esc in d.peso_por_escalon:
                        peso = esc.get('peso_total_escalon', 0.0)
                        it.add_item(NoEscape(fr"Escalón {esc.get('escalon', '?')}: {formatear_numero(peso)} kg"))
                terms = " + ".join([f"{esc.get('peso_total_escalon',0.0):.3f}" for esc in d.peso_por_escalon])
                doc.append(NoEscape(fr"$$ Q_r = {terms} = {formatear_numero(getattr(d,'Qr',0.0))}\; \mathrm{{kg}} $$"))
                doc.append(Command('vspace', '0.5em'))

            # Pérdidas en W usando la masa empírica de hierro
            add_step(doc, r"Pérdidas Totales ($W_f$)", r"W_f = Q_f \cdot P_f",
                     fr"W_f = {formatear_numero(getattr(d, 'Qf_empirical', 0.0))} \cdot {formatear_numero(getattr(d, 'Pf', 0.0), 3)}",
                     fr"W_f = {formatear_numero(getattr(d, 'Wf', 0.0))}", r"W")

        with doc.create(Subsection(NoEscape(r'Rendimiento ($\eta$)'), numbering=False)):
            P_salida_W = getattr(d, 'S', 0.0) * 1000.0
            P_entrada_W = P_salida_W + getattr(d, 'Wc', 0.0) + getattr(d, 'Wf', 0.0)
            add_step(doc, r"Rendimiento ($\eta$)",
                     r"\eta = \frac{P_{salida}}{P_{salida} + W_c + W_f} \times 100\%",
                     fr"\eta = \frac{{{P_salida_W:,.0f}}}{{{P_salida_W:,.0f} + {formatear_numero(getattr(d, 'Wc', 0.0))} + {formatear_numero(getattr(d, 'Wf', 0.0))}}} \times 100\%",
                     fr"\eta = {formatear_numero(getattr(d, 'rendimiento', 0.0), 4)}", r"\%")