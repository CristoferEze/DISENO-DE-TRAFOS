# src/design_phases/daily_performance/renderer.py
from pylatex import Section, Subsection, Command, NoEscape

def run(doc, d):
    """Añade la sección de rendimiento diario al reporte."""
    if not getattr(d, 'detalles_ciclo', None):
        return

    with doc.create(Section('Análisis de Rendimiento Diario', numbering=False)):

        with doc.create(Subsection(NoEscape(r'Energía de Salida ($E_{salida}$)'), numbering=False)):
            for detalle in d.detalles_ciclo:
                carga_pct = detalle['carga_frac'] * 100
                doc.append(NoEscape(fr"$$ E_{{sal,{int(carga_pct)}\%}} = {d.S} \cdot {detalle['carga_frac']:.2f} \cdot {detalle['horas']}h = {detalle['energia_salida_kwh']:.2f} \; kWh $$"))
            doc.append(NoEscape(fr"$$ E_{{sal,total}} = \mathbf{{{d.energia_salida_total:.2f}}} \; kWh $$"))
            doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.4pt']))
            doc.append(Command('newline'))

        with doc.create(Subsection(NoEscape(r'Pérdidas de Energía en Cobre ($E_{p,cu}$)'), numbering=False)):
            for detalle in d.detalles_ciclo:
                carga_pct = detalle['carga_frac'] * 100
                doc.append(NoEscape(fr"$$ E_{{p,cu,{int(carga_pct)}\%}} = ({detalle['carga_frac']:.2f})^2 \cdot {d.Wc/1000:.2f} kW \cdot {detalle['horas']}h = {detalle['energia_perdida_cu_kwh']:.2f} \; kWh $$"))
            doc.append(NoEscape(fr"$$ E_{{p,cu,total}} = \mathbf{{{d.energia_perdida_cobre_total:.2f}}} \; kWh $$"))
            doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.4pt']))
            doc.append(Command('newline'))
            
        with doc.create(Subsection(NoEscape(r'Pérdidas de Energía en Hierro ($E_{p,fe}$)'), numbering=False)):
            doc.append(NoEscape(r"$$ E_{p,fe} = P_f \cdot 24h $$"))
            doc.append(NoEscape(fr"$$ E_{{p,fe}} = {d.Wf/1000:.3f} kW \cdot 24h = \mathbf{{{d.energia_perdida_hierro_total:.2f}}} \; kWh $$"))
            doc.append(Command('rule', arguments=[NoEscape(r'\linewidth'), '0.4pt']))
            doc.append(Command('newline'))

        with doc.create(Subsection(NoEscape(r'Rendimiento Diario ($\eta_{diario}$)'), numbering=False)):
            doc.append(NoEscape(r"$$ \eta_{diario} = \frac{E_{sal,total}}{E_{sal,total} + E_{p,cu,total} + E_{p,fe}} \times 100\% $$"))
            doc.append(NoEscape(fr"$$ \eta_{{diario}} = \frac{{{d.energia_salida_total:.2f}}}{{{d.energia_salida_total:.2f} + {d.energia_perdida_cobre_total:.2f} + {d.energia_perdida_hierro_total:.2f}}} \times 100\% $$"))
            doc.append(NoEscape(fr"$$ \eta_{{diario}} = \mathbf{{{d.rendimiento_diario:.4f}\%}} $$"))