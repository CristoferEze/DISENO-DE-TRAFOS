# src/diagrams/generator.py
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import os
from . import single_phase_drawer
from . import three_phase_drawer

def generate_connection_diagram(d, output_dir='temp'):
    """
    Genera un diagrama de conexionado.
    Decide qué tipo de diagrama dibujar basado en el número de fases.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'connection_diagram.png')
    
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')

    conn_str = getattr(d, 'conn', 'Dyn5').upper()
    title = f'Diagrama de Conexionado - {conn_str}' if getattr(d, 'fases', 3) == 3 else 'Diagrama de Conexionado - Monofásico'
    ax.set_title(title, fontsize=16, fontweight='bold', y=1.02)
    
    if getattr(d, 'fases', 3) == 3:
        three_phase_drawer.draw(ax, d)
    else:
        single_phase_drawer.draw(ax, d)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    
    return output_path