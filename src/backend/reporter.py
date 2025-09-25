# src/backend/reporter.py

# -*- coding: utf-8 -*-
from pylatex import Document, Section, Subsection, Command, Package, Math
from pylatex.utils import NoEscape, bold

class LatexReportGenerator:
    """
    Usa PyLaTeX de forma idiomática para construir un objeto de documento
    a partir de un objeto DisenoTransformador.
    """
    def __init__(self, diseno):
        self.d = diseno

    def _add_calculation_step(self, doc, titulo, formula, valores, resultado, unidad):
        """
        Añade un bloque de cálculo estandarizado al documento, utilizando
        los objetos Math de PyLaTeX.
        """
        unidad_safe = unidad if unidad is not None else ""
        unidad_latex = f"\\mathrm{{{unidad_safe.replace('^2', '^{{2}}')}}}" if unidad_safe else ""
        
        # Asegurar que el título sea tratado como LaTeX sin escapado si es una cadena
        if isinstance(titulo, str):
            titulo_latex = NoEscape(titulo)
        else:
            titulo_latex = titulo

        with doc.create(Subsection(titulo_latex, numbering=False)):
            doc.append(Math(data=[NoEscape(formula)], escape=False))
            doc.append(Math(data=[NoEscape(valores)], escape=False))
            doc.append(Math(data=[NoEscape(f"{resultado} \\; {unidad_latex}")], escape=False))
        
        doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.4pt']))

    def create_latex_document(self):
        """Crea y devuelve un objeto Documento de PyLaTeX."""
        d = self.d
        
        geometry_options = {
            "tmargin": "1in", "lmargin": "1in",
            "paperheight": "40in", "paperwidth": "8.5in"
        }
        
        doc = Document(geometry_options=geometry_options,
                       fontenc='T1',
                       inputenc='utf8')

        # --- Título y Encabezado ---
        doc.append(NoEscape(r"{\Large \bfseries Reporte de Diseño de Transformador}"))
        doc.append(Command('newline'))
        doc.append(NoEscape(r"{\large Calculadora Automática}"))
        doc.append(Command('vspace', '1em'))
        # --- CORRECCIÓN APLICADA AQUÍ ---
        doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.8pt']))

        # --- Sección de Datos de Entrada ---
        with doc.create(Section('Datos de Entrada y Parámetros Base', numbering=False)):
            doc.append(bold("Potencia (S): "))
            doc.append(f"{d.S} kVA, ")
            doc.append(bold("Tensión Primaria (E1): "))
            doc.append(f"{d.E1_linea} V")
            doc.append(Command('newline'))
            
            doc.append(bold("Tensión Secundario (E2): "))
            doc.append(f"{d.E2_linea} V, ")
            doc.append(bold("Frecuencia (f): "))
            doc.append(f"{d.f} Hz")
            doc.append(Command('newline'))

            doc.append(bold("Conexión: "))
            doc.append(d.conn.replace('_', r'\_') + ", ")
            doc.append(bold("Tipo de Acero: "))
            doc.append(d.acero.replace('_', r'\_'))
            doc.append(Command('vspace', '0.5em'))
            doc.append(Command('newline'))
            
            doc.append("Parámetros seleccionados de tablas:")
            doc.append(Command('newline'))
            
            parametros_base = (
                f"B = {d.B_kgauss*1000:.0f} \\, \\mathrm{{gauss}}, "
                f"J = {d.J:.2f} \\, \\mathrm{{A/mm^2}}, "
                f"C = {d.C:.2f}, f_a = {d.fa:.3f}, K_r = {d.Kr:.3f}"
            )
            doc.append(Math(data=[NoEscape(parametros_base)], escape=False))

        # --- CORRECCIÓN APLICADA AQUÍ ---
        doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.8pt']))

        # --- Sección de Procedimiento de Cálculo ---
        with doc.create(Section('Procedimiento de Cálculo', numbering=False)):
            if d.fases == 3 and 'D' not in d.conn1:
                self._add_calculation_step(doc, r"Tensión Fase Primaria ($E_{1,fase}$)", r"E_{1,fase} = \frac{E_{1,linea}}{\sqrt{3}}", f"E_{{1,fase}} = \\frac{{{d.E1_linea:.0f}}}{{\\sqrt{{3}}}}", f"E_{{1,fase}} = {d.E1_fase:.2f}", "V")
            else:
                with doc.create(Subsection(NoEscape(r"Tensión de Fase Primaria ($E_{1,fase}$)"), numbering=False)):
                    doc.append(Math(data=[NoEscape(f"E_{{1,fase}} = E_{{1,linea}} = {d.E1_fase:.2f} \\; \\mathrm{{V}}")], escape=False))
                doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.4pt']))

            E1_kv = d.E1_fase / 1000.0
            kc_n = 8 if d.S <= 10 else (10 if 10 < d.S <= 250 else 12)
            self._add_calculation_step(doc, "Coef. Plenitud Cobre ($K_c$)", r"K_c = \left( \frac{k_{c,n}}{30 + E_{1,kV}} \right) \times 1.15", f"K_c = \\left( \\frac{{{kc_n}}}{{30 + {E1_kv:.2f}}} \\right) \\times 1.15", f"K_c = {d.Kc:.4f}", "")
            self._add_calculation_step(doc, r"Flujo Magnético ($\Phi$)", r"\Phi = C \cdot \sqrt{\frac{S}{f}} \cdot 10^6", f"\\Phi = {d.C:.2f} \\cdot \\sqrt{{\\frac{{{d.S}}}{{{d.f}}}}} \\cdot 10^6", f"\\Phi = {d.flujo:,.0f}", "lineas")
            self._add_calculation_step(doc, "Área Neta ($A_n$)", r"A_n = \frac{\Phi}{B}", f"A_n = \\frac{{{d.flujo:,.0f}}}{{{d.B_kgauss*1000:.0f}}}", f"A_n = {d.An:.2f}", "cm^2")
            self._add_calculation_step(doc, "Área Bruta ($A_b$)", r"A_b = \frac{A_n}{f_a}", f"A_b = \\frac{{{d.An:.2f}}}{{{d.fa:.3f}}}", f"A_b = {d.Ab:.2f}", "cm^2")
            self._add_calculation_step(doc, "Diámetro Núcleo (D)", r"D = 2 \cdot \sqrt{\frac{A_n}{\pi \cdot K_r}}", f"D = 2 \\cdot \\sqrt{{\\frac{{{d.An:.2f}}}{{\\pi \\cdot {d.Kr:.3f}}}}}", f"D = {d.D:.2f}", "cm")
            self._add_calculation_step(doc, "Área Ventana ($A_w$)", r"A_w = \frac{S_{VA}}{3.33 \cdot f \cdot B_T \cdot J \cdot K_c \cdot A_n}", f"A_w = \\frac{{{d.S*1000:.0f}}}{{3.33 \\cdot {d.f} \\cdot {d.B_tesla:.2f} \\cdot {d.J*1e6:,.0f} \\cdot {d.Kc:.4f} \\cdot {d.An*1e-4:.6f}}}", f"A_w = {d.Aw:.2f}", "cm^2")
            self._add_calculation_step(doc, "Distancia entre Centros (M)", r"M = \frac{A_w}{b} + D", f"M = \\frac{{{d.Aw:.2f}}}{{{d.b:.2f}}} + {d.D:.2f}", f"M = {d.M:.2f}", "cm")
            self._add_calculation_step(doc, "Ancho de Ventana (c)", r"c = M - D", f"c = {d.M:.2f} - {d.D:.2f}", f"c = {d.c:.2f}", "cm")

        # --- Sección de Devanados y Corrientes ---
        with doc.create(Section('Devanados y Corrientes', numbering=False)):
            self._add_calculation_step(doc, "Espiras Secundario ($N_2$)", r"N_2 = \frac{E_{2,fase} \cdot 10^8}{4.44 \cdot f \cdot \Phi}", f"N_2 = \\frac{{{d.E2_fase:.2f} \\cdot 10^8}}{{4.44 \\cdot {d.f} \\cdot {d.flujo:,.0f}}}", f"N_2 = {d.N2_fase:.0f}", "espiras")
            S_dev_VA = (d.S * 1000) / d.fases
            self._add_calculation_step(doc, "Corriente Primaria de Fase ($I_{1,fase}$)", r"I_{1,fase} = \frac{S_{devanado}}{E_{1,fase}}", f"I_{{1,fase}} = \\frac{{{S_dev_VA:,.0f}}}{{{d.E1_fase:.2f}}}", f"I_{{1,fase}} = {d.I1_fase_nom:.2f}", "A")
            self._add_calculation_step(doc, "Corriente Secundaria de Fase ($I_{2,fase}$)", r"I_{2,fase} = \frac{S_{devanado}}{E_{2,fase}}", f"I_{{2,fase}} = \\frac{{{S_dev_VA:,.0f}}}{{{d.E2_fase:.2f}}}", f"I_{{2,fase}} = {d.I2_fase:.2f}", "A")
            self._add_calculation_step(doc, "Sección Conductor Primario ($s_1$)", r"s_1 = \frac{I_{1,fase}}{J}", f"s_1 = \\frac{{{d.I1_fase_nom:.2f}}}{{{d.J:.2f}}}", f"s_1 = {d.s1:.2f}", "mm^2")
            self._add_calculation_step(doc, "Sección Conductor Secundario ($s_2$)", r"s_2 = \frac{I_{2,fase}}{J}", f"s_2 = \\frac{{{d.I2_fase:.2f}}}{{{d.J:.2f}}}", f"s_2 = {d.s2:.2f}", "mm^2")

        # --- Sección de TAPs ---
        with doc.create(Section('Resultados por Toma (TAPs)', numbering=False)):
            for pct, data in sorted(d.tap_data.items(), reverse=True):
                linea_tap = f"\\textbullet\\ Toma ({pct:+.1f}\\%) : V\\_linea = {data['Vlinea']:.0f} V, N\\_espiras = {data['N_espiras']}"
                doc.append(NoEscape(linea_tap))
                doc.append(Command('newline'))

        return doc