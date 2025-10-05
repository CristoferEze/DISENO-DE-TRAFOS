# src/diagrams/utils.py
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import numpy as np

def draw_coil(ax, center_x, center_y, width=1.5, height=1.0, num_loops=4, text=""):
    """
    Dibuja una representación de una bobina con espiras y un texto en su interior.

    Devuelve las coordenadas de los terminales (inicio, fin).
    """
    loop_height = height / max(1, num_loops)
    path_data = []

    # Terminal de entrada
    path_data.append((Path.MOVETO, (center_x - width / 2 - 0.3, center_y + height / 2)))
    path_data.append((Path.LINETO, (center_x - width / 2, center_y + height / 2)))
    
    # Espiras
    for i in range(num_loops):
        y = center_y + height / 2 - i * loop_height
        path_data.append((Path.LINETO, (center_x - width / 2, y)))
        path_data.append((Path.LINETO, (center_x + width / 2, y)))

    # Terminal de salida
    path_data.append((Path.LINETO, (center_x - width / 2, center_y - height / 2)))
    path_data.append((Path.LINETO, (center_x - width / 2 - 0.3, center_y - height / 2)))
    
    codes, verts = zip(*path_data)
    path = Path(verts, codes)
    patch = PathPatch(path, facecolor='none', edgecolor='black', lw=2)
    ax.add_patch(patch)

    # Añadir texto en el centro de la bobina
    if text:
        ax.text(center_x, center_y, text, ha='center', va='center', fontsize=12, fontweight='bold')
    
    # Coordenadas de los terminales
    start_terminal = (center_x - width / 2 - 0.3, center_y + height / 2)
    end_terminal = (center_x - width / 2 - 0.3, center_y - height / 2)
    
    return start_terminal, end_terminal