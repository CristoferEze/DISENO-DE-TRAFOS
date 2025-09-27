# src/design_phases/weights_and_losses/renderer.py
from pylatex import Section, Subsection, Command
from pylatex.utils import NoEscape

def run(doc, d):
    """Añade las secciones de pesos, pérdidas y rendimiento al documento."""
    
    # --- SECCIÓN DE PESOS (EXISTENTE) ---
    with doc.create(Section('Pesos y Cantidades', numbering=False)):
        doc.append(NoEscape(rf"\textbullet\ Peso del Cobre (Qc): \textbf{{{d.Qc:.2f}}} kg"))
        doc.append(Command('newline'))
        doc.append(NoEscape(rf"\textbullet\ Peso del Hierro (Qr): \textbf{{{d.Qr:.2f}}} kg"))
        doc.append(Command('newline'))
        doc.append(Command('vspace', '0.5em'))
        doc.append(NoEscape(rf"\textbf{{Peso Total Estimado}}: \textbf{{{d.Q_total:.2f}}} kg"))

    # --- NUEVA SECCIÓN: PÉRDIDAS Y RENDIMIENTO ---
    with doc.create(Section('Pérdidas y Rendimiento a Plena Carga', numbering=False)):
        
        # --- INICIO DE LA CORRECCIÓN ---

        # 1. Títulos de Subsection con NoEscape para formato correcto
        # 2. Se compacta el espaciado vertical
        
        with doc.create(Subsection(NoEscape(r'Pérdidas en el Cobre ($W_c$)'), numbering=False)):
            doc.append(NoEscape(r"\textbf{Pérdidas Específicas ($P_c$)}"))
            doc.append(NoEscape(r"$$ P_c = 2.44 \cdot J^2 $$"))
            doc.append(NoEscape(fr"$$ P_c = 2.44 \cdot ({d.J:.2f})^2 = {d.Pc:.2f} \; \mathrm{{W/kg}} $$"))
            
            doc.append(Command('vspace', '0.5em')) # Pequeño espacio
            
            doc.append(NoEscape(r"\textbf{Pérdidas Totales ($W_c$)}"))
            doc.append(NoEscape(r"$$ W_c = Q_c \cdot P_c $$"))
            doc.append(NoEscape(fr"$$ W_c = {d.Qc:.2f} \cdot {d.Pc:.2f} = {d.Wc:.2f} \; \mathrm{{W}} $$"))

        with doc.create(Subsection(NoEscape(r'Pérdidas en el Hierro ($W_f$)'), numbering=False)):
            doc.append(NoEscape(r"\textbf{Pérdidas Específicas ($P_f$)}"))
            doc.append(NoEscape(fr"Para acero \textbf{{{d.acero}}} a ${d.B_kgauss:.2f}$ kGauss, el valor de tabla es:"))
            doc.append(NoEscape(fr"$$ P_f = {d.Pf:.3f} \; \mathrm{{W/kg}} $$"))
            
            doc.append(Command('vspace', '0.5em'))
            
            doc.append(NoEscape(r"\textbf{Pérdidas Totales ($W_f$)}"))
            doc.append(NoEscape(r"$$ W_f = Q_r \cdot P_f $$"))
            doc.append(NoEscape(fr"$$ W_f = {d.Qr:.2f} \cdot {d.Pf:.3f} = {d.Wf:.2f} \; \mathrm{{W}} $$"))
            
        with doc.create(Subsection(NoEscape(r'Rendimiento ($\eta$)'), numbering=False)):
            P_salida_W = d.S * 1000
            P_entrada_W = P_salida_W + d.Wc + d.Wf
            doc.append(NoEscape(r"$$ \eta = \frac{P_{salida}}{P_{salida} + W_c + W_f} \times 100\% $$"))
            doc.append(NoEscape(fr"$$ \eta = \frac{{{P_salida_W:,.0f}}}{{{P_salida_W:,.0f} + {d.Wc:.2f} + {d.Wf:.2f}}} \times 100\% $$"))
            doc.append(NoEscape(fr"$$ \eta = \mathbf{{{d.rendimiento:.4f}\%}} $$"))

    # 3. La línea de separación se coloca una sola vez al final de toda la sección
    doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.8pt']))
    # --- FIN DE LA CORRECCIÓN ---