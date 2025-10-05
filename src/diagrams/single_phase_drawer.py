# src/diagrams/single_phase_drawer.py
# -*- coding: utf-8 -*-

import matplotlib.patches as patches
from .utils import draw_coil

def draw(ax, d):
    """
    Dibuja un diagrama de conexión monofásico.
    """
    # Títulos
    ax.text(2.5, 7, 'PRIMARIO', ha='center', fontsize=14, fontweight='bold')
    ax.text(7.5, 7, 'SECUNDARIO', ha='center', fontsize=14, fontweight='bold')

    # Bobinas
    n1_text = f"N₁ = {getattr(d, 'N1_fase', 0):.0f}"
    n2_text = f"N₂ = {getattr(d, 'N2_fase', 0):.0f}"
    
    p_start, p_end = draw_coil(ax, 2.5, 4.5, text=n1_text)
    s_start, s_end = draw_coil(ax, 7.5, 4.5, text=n2_text)

    # Núcleo
    core = patches.Rectangle((4.25, 3.5), 1.5, 2, linewidth=2, edgecolor='gray', facecolor='none', ls='--')
    ax.add_patch(core)
    
    # Terminales
    ax.plot([p_start[0], p_start[0] - 0.5], [p_start[1], p_start[1]], 'k-')
    ax.text(p_start[0] - 0.7, p_start[1], 'H1', ha='right', va='center', fontsize=12)
    
    ax.plot([p_end[0], p_end[0] - 0.5], [p_end[1], p_end[1]], 'k-')
    ax.text(p_end[0] - 0.7, p_end[1], 'H2', ha='right', va='center', fontsize=12)

    ax.plot([s_start[0] - 0.2, s_start[0] - 0.7], [s_start[1], s_start[1]], 'k-')
    ax.text(s_start[0] - 0.9, s_start[1], 'X1', ha='right', va='center', fontsize=12)

    ax.plot([s_end[0] - 0.2, s_end[0] - 0.7], [s_end[1], s_end[1]], 'k-')
    ax.text(s_end[0] - 0.9, s_end[1], 'X2', ha='right', va='center', fontsize=12)