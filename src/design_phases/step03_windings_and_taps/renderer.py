# src/design_phases/windings_and_taps/renderer.py
# -*- coding: utf-8 -*-
# src/design_phases/windings_and_taps/renderer.py
# -*- coding: utf-8 -*-

from pylatex import Section, Subsection, Command, Math, Itemize, Figure
from pylatex.utils import NoEscape, bold
import os
import math
from core import database as _database
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
        # --- MODIFICADO: Se añade el cálculo de espiras del primario basado en el secundario y la relación de transformación ---
        add_step(doc, "Espiras Primario ($N_1$)", r"N_1 = N_2 \cdot \frac{E_{1,fase}}{E_{2,fase}}", f"N_1 = {d.N2_fase:.0f} \\cdot \\frac{{{formatear_numero(d.E1_fase)}}}{{{formatear_numero(d.E2_fase)}}}", f"N_1 = {getattr(d, 'N1_fase', 0):.0f}", "espiras")
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
        doc.append(Command('newline'))
        
        add_step(doc, "Sección Conductor Secundario ($s_2$)", r"s_2 = \frac{I_{2,fase}}{J}", f"s_2 = \\frac{{{formatear_numero(d.I2_fase)}}}{{{formatear_numero(d.J)}}}", f"s_2 = {formatear_numero(d.s2)}", "mm^2")

        # --- MODIFICADO: Ajuste de saltos de línea para el calibre y método ---
        doc.append(Command('vspace', '0.5em'))
        doc.append(Command('newline'))
        doc.append(NoEscape(fr"\textbf{{Calibre Seleccionado (Secundario):}} AWG \textbf{{{getattr(d, 'awg2', 'No encontrado')}}}"))
        doc.append(Command('newline'))
        if hasattr(d, 'metodo_peso_secundario'):
            doc.append(NoEscape(fr"\textit{{Método de cálculo de peso: {d.metodo_peso_secundario}}}"))
            doc.append(Command('newline'))
        # Mostrar detalles de pletina si corresponde
        if getattr(d, 'awg2', '') == 'Pletina':
            # Mostrar selección de pletina con desarrollo paso a paso usando los campos exactos en d
            # Priorizar los valores exactos (si existen) introducidos por la fase de cálculo
            p_w = getattr(d, 'pletina2_w_exact', None) or getattr(d, 'pletina2_w', None)
            p_t = getattr(d, 'pletina2_t_exact', None) or getattr(d, 'pletina2_t', None)
            p_s = getattr(d, 's2_adoptada', None) or getattr(d, 's2_real', None) or getattr(d, 's2', None)

            # Mostrar desarrollo y resultados preparados por la fase de cálculo
            doc.append(NoEscape(r"\textbf{Desarrollo de selección de pletina (BT)}"))
            doc.append(Command('newline'))
            # Mostrar la derivación algebraica y el resultado de t_min (valor calculado en la fase de cálculo)
            t_min_val = getattr(d, 't_min_pletina', None)
            if t_min_val is not None:
                doc.append(NoEscape(fr"$3\cdot t^2 \geq s_2 \;\Rightarrow\; t_{{min}} = \sqrt{{\dfrac{{s_2}}{{3}}}} = {t_min_val:.3f}\;\mathrm{{mm}}$"))
            else:
                doc.append(NoEscape(r"$3\cdot t^2 \geq s_2 \;\Rightarrow\; t_{min} = \sqrt{\dfrac{s_2}{3}}$"))
            doc.append(Command('newline'))
            # Mostrar t_min para MT si está calculado
            if hasattr(d, 't_min_pletina_mt'):
                doc.append(NoEscape(r"\textit{t$_{min}$ (MT) redondeado}:"))
                doc.append(NoEscape(fr"${getattr(d, 't_min_pletina_mt', 0.0):.1f}\;\mathrm{{mm}}$"))
            doc.append(Command('newline'))

            # Mostrar candidatos calculados por la fase de cálculo (d.pletina_candidates)
            candidates = getattr(d, 'pletina_candidates', [])
            if candidates:
                doc.append(NoEscape(r"\textit{Candidatos (ancho mm, espesor mm, área mm\textsuperscript{2}; cumple $3 t^2 \ge s_2$): }"))
                doc.append(Command('newline'))
                shown = 0
                for c in candidates:
                    meets_txt = 'Si' if c.get('meets_eq') else 'No'
                    doc.append(NoEscape(fr"- w={c['w']:.2f} mm, t={c['t']:.2f} mm, area={c['area']:.3f} mm\textsuperscript{{2}}, cumple={meets_txt}"))
                    doc.append(Command('newline'))
                    shown += 1
                    if shown >= 8:
                        break
                doc.append(Command('vspace', '0.3em'))
                # Mostrar selección final (preparada en d por la fase de cálculo)
                sel_w = getattr(d, 'pletina2_w_exact', None)
                sel_t = getattr(d, 'pletina2_t_exact', None)
                sel_area = getattr(d, 's2_adoptada', None)
                if sel_w is not None and sel_t is not None and sel_area is not None:
                    sel_w_s = f"{sel_w:.3f}" if isinstance(sel_w, (int, float)) else str(sel_w)
                    sel_t_s = f"{sel_t:.3f}" if isinstance(sel_t, (int, float)) else str(sel_t)
                    sel_area_s = f"{sel_area:.3f}" if isinstance(sel_area, (int, float)) else str(sel_area)
                    doc.append(NoEscape(r"\textbf{Pletina finalmente elegida:}"))
                    doc.append(Command('newline'))
                    doc.append(NoEscape(fr"Ancho = {sel_w_s} mm, Espesor = {sel_t_s} mm, S\_cu = {sel_area_s} mm\textsuperscript{{2}}"))
                    doc.append(Command('newline'))
            else:
                doc.append(NoEscape(r"No se encontraron candidatos de pletina que cumplan el requisito de sección; se aplicó fallback."))
                doc.append(Command('newline'))

            doc.append(Command('vspace', '0.5em'))
        doc.append(Command('vspace', '0.5em'))
        doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.4pt']))
        doc.append(Command('newline'))
        
    # Sección añadida: Bobinado y Aislamiento (antes del diagrama de conexionado)
    with doc.create(Section('Bobinado y Aislamiento', numbering=False)):
        # Sub-sección: Bobinado
        with doc.create(Subsection('Bobinado', numbering=False)):
            # Valores intermedios
            b_mm = getattr(d, 'b', 0.0) * 10
            margen_bt = getattr(d, 'margen_total_bt', 0.0)
            margen_mt = getattr(d, 'margen_total_mt', 0.0)
            Hb2 = getattr(d, 'Hb2', 0.0)
            Hb1 = getattr(d, 'Hb1', 0.0)
            # Usar el valor calculado si existe, si no 0
            Ne_cb2 = int(getattr(d, 'Ne_cb2', 0))
            Ne_cb1 = int(getattr(d, 'Ne_cb1', 0))
            Nc_b2 = float(getattr(d, 'Nc_b2', 0.0))
            Nc_b1 = float(getattr(d, 'Nc_b1', 0.0))
            N2_fase = int(getattr(d, 'N2_fase', 0))
            N1_fase = int(getattr(d, 'N1_fase', 0))
            ancho_c2 = getattr(d, 'ancho_c2_usado', getattr(d, 'ancho_c2_usado', 5.8))
            diam_c1 = getattr(d, 'diam_c1_usado', getattr(d, 'diam_c1_usado', 0.63))

            # Bobina B.T.
            doc.append(NoEscape(r"\textbf{Bobina de B.T.}"))
            doc.append(Math(data=[NoEscape(fr"H_{{b2}} = {formatear_numero(b_mm,1)} - 2({formatear_numero(margen_bt,0)}) = {formatear_numero(Hb2,1)} \,\mathrm{{mm}}")], escape=False))
            # Mostrar el ancho usado en el cálculo (ancho + margen)
            ancho_eff = getattr(d, 'ancho_c2_effectivo', ancho_c2)
            margen_eff = getattr(d, 'conductor_width_margin_mm', 0.2)
            doc.append(Math(data=[NoEscape(fr"N_{{e/cb2}} = \frac{{{formatear_numero(Hb2,1)}}}{{{formatear_numero(ancho_eff,2)}}} = {Ne_cb2} \;\text{{espiras / capa}}")], escape=False))
            # Indicar explicitamente el denominador usado (ancho + margen)
            doc.append(Command('newline'))
            doc.append(NoEscape(fr"(Denominador usado = ancho = {formatear_numero(ancho_c2,2)} mm + margen = {formatear_numero(margen_eff,2)} mm = {formatear_numero(ancho_eff,2)} mm)"))
            doc.append(Command('newline'))
            # Capas y distribución
            capas_completas_bt = int(__import__('math').floor(Nc_b2)) if Nc_b2 else 0
            sobrante_bt = int(N2_fase - capas_completas_bt * Ne_cb2) if Ne_cb2 > 0 else 0
            doc.append(Math(data=[NoEscape(fr"N_{{c/b2}} = \frac{{{N2_fase}}}{{{Ne_cb2}}} = {formatear_numero(Nc_b2,2)} \approx {__import__('math').ceil(Nc_b2)} \;\text{{capas}} / ({capas_completas_bt} \cdot {Ne_cb2} + 1 \cdot {sobrante_bt})")], escape=False))

            # Aislamiento B.T. - mostrar valores calculados por la fase de cálculo
            Vc2 = getattr(d, 'Vc2', None)
            ceil_nc_b2 = getattr(d, 'ceil_Nc_b2', int(__import__('math').ceil(Nc_b2) if Nc_b2 else 1))
            raw_delta2 = getattr(d, 'delta_s2', 0.0)
            round_delta2 = getattr(d, 'delta_s2_rounded', raw_delta2)
            # Mostrar cálculo y resultado (valores ya calculados en core.run)
            doc.append(Math(data=[NoEscape(fr"V_{{c}} = 2 \cdot \left(\frac{{{getattr(d, 'BIL2', 10)}}}{{{ceil_nc_b2}}}\right) \cdot 0.25 = {formatear_numero(Vc2 if Vc2 is not None else 0.0,2)}\;\mathrm{{kV}}")], escape=False))
            # Mostrar delta bruto (2 decimales) y redondeado al decimal superior (1 decimal)
            doc.append(Math(data=[NoEscape(fr"\delta_{{c}} = 3.5 \cdot \left(\frac{{{formatear_numero(Vc2 if Vc2 is not None else 0.0,2)}}}{{{formatear_numero(getattr(d, 'rigidez_papel_presspan', 40.0),1)}}}\right) = {formatear_numero(raw_delta2,2)}\;\mathrm{{mm}}\; (redondeado:\; {formatear_numero(round_delta2,1)}\;\mathrm{{mm}})")], escape=False))

            # Bobina M.T.
            doc.append(NoEscape(r"\vspace{0.5em}"))
            doc.append(NoEscape(r"\textbf{Bobina de M.T.}"))
            doc.append(Math(data=[NoEscape(fr"H_{{b1}} = {formatear_numero(b_mm,1)} - 2({formatear_numero(margen_mt,0)}) = {formatear_numero(Hb1,1)} \,\mathrm{{mm}}")], escape=False))
            doc.append(Math(data=[NoEscape(fr"N_{{e/cb1}} = \frac{{{formatear_numero(Hb1,1)}}}{{{formatear_numero(diam_c1,2)}}} = {Ne_cb1} \;\text{{espiras / capa}}")], escape=False))
            capas_completas_mt = int(__import__('math').floor(Nc_b1)) if Nc_b1 else 0
            sobrante_mt = int(N1_fase - capas_completas_mt * Ne_cb1) if Ne_cb1 > 0 else 0
            doc.append(Math(data=[NoEscape(fr"N_{{c/b1}} = \frac{{{N1_fase}}}{{{Ne_cb1}}} = {formatear_numero(Nc_b1,2)} \approx {__import__('math').ceil(Nc_b1)} \;\text{{capas}} / ({capas_completas_mt} \cdot {Ne_cb1} + 1 \cdot {sobrante_mt})")], escape=False))

            # Aislamiento M.T. - usar valores preparados por la fase de cálculo
            Vc1 = getattr(d, 'Vc1', None)
            ceil_nc_b1 = getattr(d, 'ceil_Nc_b1', int(__import__('math').ceil(Nc_b1) if Nc_b1 else 1))
            raw_delta1 = getattr(d, 'delta_s1', 0.0)
            round_delta1 = getattr(d, 'delta_s1_rounded', raw_delta1)
            doc.append(Math(data=[NoEscape(fr"V_{{c}} = 2 \cdot \left(\frac{{{getattr(d, 'BIL1', 95)}}}{{{ceil_nc_b1}}}\right) \cdot 0.75 = {formatear_numero(Vc1 if Vc1 is not None else 0.0,2)}\;\mathrm{{kV}}")], escape=False))
            doc.append(Math(data=[NoEscape(fr"\delta_{{e}} = 5.0 \cdot \left(\frac{{{formatear_numero(Vc1 if Vc1 is not None else 0.0,2)}}}{{{formatear_numero(getattr(d, 'rigidez_papel_presspan', 40.0),1)}}}\right) = {formatear_numero(raw_delta1,2)}\;\mathrm{{mm}}\; (redondeado:\; {formatear_numero(round_delta1,1)}\;\mathrm{{mm}})")], escape=False))

        # Sub-sección: Aislamiento (resumen de márgenes)
        with doc.create(Subsection('Aislamiento entre capas (impulso)', numbering=False)):
            doc.append(Math(data=[NoEscape(fr"margen_{{BT}} = {formatear_numero(getattr(d, 'margen_total_bt', 0.0))} \;\mathrm{{mm}}, \; margen_{{MT}} = {formatear_numero(getattr(d, 'margen_total_mt', 0.0))} \;\mathrm{{mm}}")], escape=False))
        doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.4pt']))
        doc.append(Command('newline'))

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
            doc.append(Command('newline'))
            
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
            doc.append(Command('newline'))
            
        # CORREGIDO: Mostrar peso total del cobre calculado considerando el número de fases
        factor_fases = 3 if getattr(d, 'fases', 1) == 3 else 1
        Qc_por_bobinado = getattr(d, 'Qc_por_bobinado', 0.0)
        Qc_total = getattr(d, 'Qc_total', 0.0)
        
        if factor_fases == 3:
            # Para trifásico: mostrar cálculo por fase y luego el total
            doc.append(NoEscape(fr"\textbf{{Peso del Cobre (por fase)}}: $Q_{{c,fase}} = Q_{{b1}} + Q_{{b2}} = {formatear_numero(getattr(d, 'Qb1', 0.0))} + {formatear_numero(getattr(d, 'Qb2', 0.0))} = {formatear_numero(Qc_por_bobinado)}$ kg"))
            doc.append(Command('newline'))
            doc.append(NoEscape(fr"\textbf{{Peso Total del Cobre (3 fases)}}: $Q_c = Q_{{c,fase}} \times 3 = {formatear_numero(Qc_por_bobinado)} \times 3 = \mathbf{{{formatear_numero(Qc_total)}}}$ kg"))
        else:
            # Para monofásico: mostrar directamente el total
            doc.append(NoEscape(fr"\textbf{{Peso Total del Cobre}}: $Q_c = Q_{{b1}} + Q_{{b2}} = {formatear_numero(getattr(d, 'Qb1', 0.0))} + {formatear_numero(getattr(d, 'Qb2', 0.0))} = \mathbf{{{formatear_numero(Qc_total)}}}$ kg"))
        
    doc.append(Command('vspace', '0.3em'))
    # Añadir salto de línea extra para separar el título/resultados del bloque de comparación
    # Usar salto de párrafo en lugar de \newline para evitar 'There's no line here to end'.
    doc.append(Command('par'))
    doc.append(Command('vspace', '0.2em'))

    # Comparación con la fórmula propuesta: Q_c = 0.021 * Kc * b * c * (2*D + c)
    try:
        Kc_val = getattr(d, 'Kc', 0.0)
        b_val = getattr(d, 'b', 0.0)
        c_val = getattr(d, 'c', 0.0)
        D_val = getattr(d, 'D', 0.0)

        # CORREGIDO: La fórmula empírica ya está definida para transformador trifásico
        factor_fases = 3 if getattr(d, 'fases', 1) == 3 else 1

        Qc_formula = 0.021 * Kc_val * b_val * c_val * (2 * D_val + c_val)
        # Para monofásico, dividir la fórmula entre 3 para comparar apropiadamente
        if factor_fases == 1:
            Qc_formula_comparacion = Qc_formula / 3
            formula_text = r"0.021 \cdot K_c \cdot b \cdot c \cdot (2D + c) / 3"
        else:
            Qc_formula_comparacion = Qc_formula
            formula_text = r"0.021 \cdot K_c \cdot b \cdot c \cdot (2D + c)"
        
        Qc_formula_str = formatear_numero(Qc_formula_comparacion)

        # CORREGIDO: Usar Qc_total que ya tiene el factor de fases aplicado correctamente
        Qc_calc_total = getattr(d, 'Qc_total', 0.0)

        diff_abs = Qc_calc_total - Qc_formula_comparacion
        diff_pct = (diff_abs / Qc_formula_comparacion * 100.0) if Qc_formula_comparacion != 0 else 0.0
        diff_pct_str = formatear_numero(diff_pct)

        # Construir paso a paso la sustitución numérica para mayor trazabilidad
        Kc_s = formatear_numero(Kc_val)
        b_s = formatear_numero(b_val)
        c_s = formatear_numero(c_val)
        D_s = formatear_numero(D_val)
        paren_val = formatear_numero(2 * D_val + c_val)

        doc.append(NoEscape(r"\textbf{Comparación con fórmula estimada}:"))
        doc.append(Command('newline'))
        doc.append(Command('vspace', '0.2em'))
        # Mostrar la fórmula simbólica
        doc.append(NoEscape(fr"$Q_c^{{fórmula}} = 0.021 \cdot K_c \cdot b \cdot c \cdot (2D + c)$"))
        doc.append(Command('newline'))
        doc.append(Command('vspace', '0.3em'))
        # Sustitución de valores
        doc.append(NoEscape(fr"$= 0.021 \cdot {Kc_s} \cdot {b_s} \cdot {c_s} \cdot (2 \cdot {D_s} + {c_s})$"))
        doc.append(Command('newline'))
        doc.append(Command('vspace', '0.3em'))
        # Evaluar paréntesis y mostrar producto final
        doc.append(NoEscape(fr"$= 0.021 \cdot {Kc_s} \cdot {b_s} \cdot {c_s} \cdot ({paren_val})$"))
        doc.append(Command('newline'))
        doc.append(Command('vspace', '0.3em'))
        doc.append(NoEscape(fr"$= \mathbf{{{Qc_formula_str}}}\;\mathrm{{kg}}$"))
        doc.append(Command('newline'))
        doc.append(Command('vspace', '0.2em'))
        # Mostrar comparación con resultado calculado
        doc.append(NoEscape(fr"(Resultado calculado por el motor: $Q_c = \mathbf{{{formatear_numero(Qc_calc_total)}}}\;\mathrm{{kg}}$; Diferencia = {diff_pct_str}\%)"))
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