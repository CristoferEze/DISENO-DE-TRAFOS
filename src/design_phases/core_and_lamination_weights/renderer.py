# src/design_phases/core_and_lamination_weights/renderer.py
# -*- coding: utf-8 -*-

from pylatex import Section, Subsection, Command, Figure
from pylatex.utils import NoEscape
import os

# Aceptamos add_step para mantener API consistente con otros renderers
def run(doc, d, add_step):
    """Renderiza el detalle de peso del núcleo y las laminaciones."""
    with doc.create(Section('Peso del Núcleo por Laminaciones', numbering=False)):
        # Resumen general
        if hasattr(d, 'Qr'):
            doc.append(NoEscape(rf"\textbf{{Peso del Núcleo (Qr)}}: \textbf{{{d.Qr:.2f}}} kg"))
            doc.append(Command('newline'))
        else:
            doc.append(NoEscape(r"\textbf{Peso del Núcleo (Qr)}: No disponible"))
            doc.append(Command('newline'))

        doc.append(Command('vspace', '0.5em'))

        # Detalle por escalón si está disponible
        if getattr(d, 'peso_por_escalon', None):
            for escalon in d.peso_por_escalon:
                escn = escalon.get('escalon', '?')
                peso_total = escalon.get('peso_total_escalon', 0.0)
                with doc.create(Subsection(NoEscape(f"Escalón {escn}"), numbering=False)):
                    doc.append(NoEscape(fr"\textbf{{Peso total escalón {escn}}}: {peso_total:.2f} kg"))
                    doc.append(Command('newline'))
                    doc.append(Command('vspace', '0.3em'))

                    # Listar piezas y pesos
                    detalles = escalon.get('detalles', [])
                    for det in detalles:
                        nombre = det.get('nombre', 'pieza')
                        num = det.get('num_piezas', 0)
                        pk = det.get('peso_kg', 0.0)
                        linea = rf"\textbullet\ {nombre}: {num} piezas, {pk:.3f} kg"
                        doc.append(NoEscape(linea))
                        doc.append(Command('newline'))
                    doc.append(Command('vspace', '0.5em'))
        else:
            doc.append(NoEscape(r"No se dispone del detalle por escalón de las laminaciones."))
            doc.append(Command('newline'))

        # Incluir gráficos si existen rutas provistas por otras fases (nucleus/laminations)
        core_plot = getattr(d, 'core_plot_path', None)
        lam_plots = getattr(d, 'lamination_plot_paths', None)
    
        try:
            if core_plot:
                core_basename = os.path.basename(core_plot)
                with doc.create(Figure(position='h!')) as fig:
                    fig.add_image(core_basename, width=NoEscape(r'0.9\linewidth'))
                    fig.add_caption('Sección transversal del núcleo.')
    
            if lam_plots:
                for p in lam_plots:
                    lam_basename = os.path.basename(p)
                    with doc.create(Figure(position='h!')) as fig:
                        fig.add_image(lam_basename, width=NoEscape(r'0.9\linewidth'))
                        fig.add_caption('Laminación por escalón')
        except Exception as e:
            doc.append(NoEscape(fr"\textit{{Error al incluir gráficos: {e}}}"))