# src/diagrams/utils.py
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Rectangle, Circle
import numpy as np

def draw_winding_rect(ax, center_x, center_y, width=0.5, height=2.0, text=""):
    """
    Dibuja una representación esquemática de una bobina como un rectángulo
    con un punto de polaridad en el terminal de inicio.

    Devuelve las coordenadas de los terminales (inicio, fin).
    """
    terminal_len = 0.5
    
    # Coordenadas del rectángulo
    rect_x = center_x - width / 2
    rect_y = center_y - height / 2
    
    # Dibujar el rectángulo de la bobina
    rect = Rectangle((rect_x, rect_y), width, height, facecolor='black', edgecolor='black')
    ax.add_patch(rect)
    
    # Coordenadas de los terminales
    start_terminal_y = rect_y + height + terminal_len
    end_terminal_y = rect_y - terminal_len
    
    # Dibujar líneas de terminales
    ax.plot([center_x, center_x], [rect_y + height, start_terminal_y], color='black', lw=1.5)
    ax.plot([center_x, center_x], [rect_y, end_terminal_y], color='black', lw=1.5)

    # Dibujar punto de polaridad (círculo blanco con borde negro)
    dot_y = rect_y + height + 0.1
    dot = Circle((center_x, dot_y), radius=0.06, facecolor='white', edgecolor='black', lw=1.5, zorder=5)
    ax.add_patch(dot)
    
    # Añadir texto a la IZQUIERDA de la bobina
    if text:
        ax.text(center_x - width / 2 - 0.2, center_y, text,
                ha='right', va='center', fontsize=11, fontweight='bold')
    
    return (center_x, start_terminal_y), (center_x, end_terminal_y)


def draw_coil(ax, center_x, center_y, width=1.0, height=1.8, num_loops=5, text=""):
    """
    (Función sin cambios, para el diagrama monofásico)
    Dibuja una representación de una bobina con espiras.
    """
    # ... (código de esta función sin cambios) ...
    loop_height = height / max(1, num_loops)
    path_data = []

    terminal_x_start = center_x - width / 2 - 0.4
    terminal_y_start = center_y + height / 2
    terminal_x_end = center_x - width / 2 - 0.4
    terminal_y_end = center_y - height / 2

    path_data.append((Path.MOVETO, (terminal_x_start, terminal_y_start)))
    path_data.append((Path.LINETO, (center_x - width / 2, terminal_y_start)))
    
    for i in range(num_loops):
        y_top = center_y + height / 2 - i * loop_height
        y_bottom = center_y + height / 2 - (i + 1) * loop_height
        path_data.append((Path.LINETO, (center_x - width / 2, y_bottom)))
        path_data.append((Path.MOVETO, (center_x + width / 2, y_top)))
        path_data.append((Path.LINETO, (center_x + width / 2, y_bottom)))

    path_data.append((Path.MOVETO, (center_x - width / 2, terminal_y_start)))
    path_data.append((Path.LINETO, (center_x - width / 2, terminal_y_end)))

    path_data.append((Path.MOVETO, (center_x - width / 2, terminal_y_end)))
    path_data.append((Path.LINETO, (terminal_x_end, terminal_y_end)))
    
    codes, verts = zip(*path_data)
    path = Path(verts, codes)
    patch = PathPatch(path, facecolor='none', edgecolor='black', lw=1.5)
    ax.add_patch(patch)

    if text:
        ax.text(center_x - width / 2 - 0.1, center_y, text, 
                ha='right', va='center', fontsize=11, fontweight='bold')
    
    return (terminal_x_start, terminal_y_start), (terminal_x_end, terminal_y_end)