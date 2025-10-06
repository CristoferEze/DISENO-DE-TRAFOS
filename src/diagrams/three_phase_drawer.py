# src/diagrams/three_phase_drawer.py
# -*- coding: utf-8 -*-

import re
import matplotlib.pyplot as plt
from .utils import draw_winding_rect

# -----------------------------------------------------------------------------
# FUNCIONES DE DIBUJO MODULARES
# -----------------------------------------------------------------------------

def _draw_star_below(ax, terminals, has_neutral, phases):
    """Dibuja una conexión en Estrella con el neutro DEBAJO de las bobinas."""
    p1_start, p1_end = terminals[f'{phases[0]}1'], terminals[f'{phases[0]}2']
    p2_start, p2_end = terminals[f'{phases[1]}1'], terminals[f'{phases[1]}2']
    p3_start, p3_end = terminals[f'{phases[2]}1'], terminals[f'{phases[2]}2']
    
    neutral_y = p1_end[1] - 0.4  # Nivel de la barra de neutro
    
    # Barra de neutro horizontal (usar coordenadas de los terminales finales)
    ax.plot([p1_end[0], p3_end[0]], [neutral_y, neutral_y], color='black', lw=1.5)

    # Conexiones verticales desde los terminales inferiores (fin) a la barra
    ax.plot([p1_end[0], p1_end[0]], [p1_end[1], neutral_y], color='black', lw=1.5)
    ax.plot([p2_end[0], p2_end[0]], [p2_end[1], neutral_y], color='black', lw=1.5)
    ax.plot([p3_end[0], p3_end[0]], [p3_end[1], neutral_y], color='black', lw=1.5)
    
    if has_neutral:
        neutral_x_out = p2_end[0] # Centro
        ax.plot([neutral_x_out, neutral_x_out], [neutral_y, neutral_y - 0.5], color='black', lw=1.5)
        ax.text(neutral_x_out, neutral_y - 0.7, 'N', ha='center', va='top', fontsize=12, fontweight='bold')

def _draw_star_above(ax, terminals, has_neutral, phases):
    """Dibuja una conexión en Estrella con el neutro ENCIMA de las bobinas."""
    p1_start, p1_end = terminals[f'{phases[0]}1'], terminals[f'{phases[0]}2']
    p2_start, p2_end = terminals[f'{phases[1]}1'], terminals[f'{phases[1]}2']
    p3_start, p3_end = terminals[f'{phases[2]}1'], terminals[f'{phases[2]}2']
    
    neutral_y = p1_start[1] + 0.4 # Nivel de la barra de neutro
    
    # Barra de neutro horizontal
    ax.plot([p1_start[0], p3_start[0]], [neutral_y, neutral_y], color='black', lw=1.5)

    # Conexiones verticales desde los terminales superiores (inicio) a la barra
    ax.plot([p1_start[0], p1_start[0]], [p1_start[1], neutral_y], color='black', lw=1.5)
    ax.plot([p2_start[0], p2_start[0]], [p2_start[1], neutral_y], color='black', lw=1.5)
    ax.plot([p3_start[0], p3_start[0]], [p3_start[1], neutral_y], color='black', lw=1.5)
    
    if has_neutral:
        neutral_x_out = p2_start[0] # Centro
        ax.plot([neutral_x_out, neutral_x_out], [neutral_y, neutral_y + 0.5], color='black', lw=1.5)
        ax.text(neutral_x_out, neutral_y + 0.7, 'N', ha='center', va='bottom', fontsize=12, fontweight='bold')

def _draw_delta_right(ax, terminals, phases):
    """Dibuja una conexión Delta con secuencia hacia la derecha (U'->V)."""
    p1_start, p1_end = terminals[f'{phases[0]}1'], terminals[f'{phases[0]}2']
    p2_start, p2_end = terminals[f'{phases[1]}1'], terminals[f'{phases[1]}2']
    p3_start, p3_end = terminals[f'{phases[2]}1'], terminals[f'{phases[2]}2']
    jog_len = 0.4

    # Conexión U' -> V
    x_path1 = [p1_end[0], p1_end[0] + jog_len, p2_start[0] - jog_len, p2_start[0]]
    y_path1 = [p1_end[1], p1_end[1], p2_start[1], p2_start[1]]
    ax.plot(x_path1, y_path1, color='black', lw=1.5)

    # Conexión V' -> W
    x_path2 = [p2_end[0], p2_end[0] + jog_len, p3_start[0] - jog_len, p3_start[0]]
    y_path2 = [p2_end[1], p2_end[1], p3_start[1], p3_start[1]]
    ax.plot(x_path2, y_path2, color='black', lw=1.5)

    # Conexión de retorno W' -> U (por fuera a la izquierda)
    y_level = p3_end[1] - 0.4
    x_outside = p1_start[0] - 0.6
    x_path3 = [p3_end[0], p3_end[0], x_outside, x_outside, p1_start[0]]
    y_path3 = [p3_end[1], y_level, y_level, p1_start[1], p1_start[1]]
    ax.plot(x_path3, y_path3, color='black', lw=1.5)

def _draw_delta_left(ax, terminals, phases):
    """Dibuja una conexión Delta con secuencia hacia la izquierda (U'->W)."""
    p1_start, p1_end = terminals[f'{phases[0]}1'], terminals[f'{phases[0]}2']
    p2_start, p2_end = terminals[f'{phases[1]}1'], terminals[f'{phases[1]}2']
    p3_start, p3_end = terminals[f'{phases[2]}1'], terminals[f'{phases[2]}2']
    jog_len = 0.4

    # Conexión U' -> W
    x_path1 = [p1_end[0], p1_end[0] - jog_len, p3_start[0] + jog_len, p3_start[0]]
    y_path1 = [p1_end[1], p1_end[1], p3_start[1], p3_start[1]]
    ax.plot(x_path1, y_path1, color='black', lw=1.5)

    # Conexión W' -> V
    x_path2 = [p3_end[0], p3_end[0] - jog_len, p2_start[0] + jog_len, p2_start[0]]
    y_path2 = [p3_end[1], p3_end[1], p2_start[1], p2_start[1]]
    ax.plot(x_path2, y_path2, color='black', lw=1.5)

    # Conexión de retorno V' -> U (por fuera a la derecha)
    y_level = p2_end[1] - 0.4
    x_outside = p1_start[0] + 0.6
    x_path3 = [p2_end[0], p2_end[0], x_outside, x_outside, p1_start[0]]
    y_path3 = [p2_end[1], y_level, y_level, p1_start[1], p1_start[1]]
    ax.plot(x_path3, y_path3, color='black', lw=1.5)

# -----------------------------------------------------------------------------
# LÓGICA PRINCIPAL Y DESPACHADOR
# -----------------------------------------------------------------------------

def _dispatch_wiring(ax, conn_type, terminals, side, phase_index):
    """
    Decide qué función de dibujo modular llamar basado en la conexión y el índice.
    """
    phases = ['U', 'V', 'W'] if side == 'primary' else ['u', 'v', 'w']
    has_neutral = 'N' in conn_type


    if 'D' in conn_type:
        # Los índices 2, 4, 8, 10 suelen tener secuencia de fase inversa
        if phase_index in [2, 4, 8, 10]:
            _draw_delta_left(ax, terminals, phases)
        else:
            _draw_delta_right(ax, terminals, phases)
            
    elif 'Y' in conn_type:
        # CORRECCIÓN: La inversión de polaridad se da en impares, pero el grupo 11
        # es una excepción común que se considera conexión "directa" o no invertida.
        is_inverted = (phase_index % 2 != 0 and phase_index != 11)
        
        # Para el primario, nunca se invierte. Para el secundario, depende del índice.
        if side == 'secondary' and is_inverted:
            _draw_star_above(ax, terminals, has_neutral, phases)
        else:
            _draw_star_below(ax, terminals, has_neutral, phases)

def draw(ax, d):
    """Función principal que prepara y despacha el dibujo del diagrama."""
    terminals = {'primary': {}, 'secondary': {}}
    
    # --- DIBUJAR BOBINAS ---
    phases_upper = ['U', 'V', 'W']
    x_coords = [2.5, 5.0, 7.5]
    
    n1_text = f"N₁ = {getattr(d, 'N1_fase', 0):.0f}"
    n2_text = f"N₂ = {getattr(d, 'N2_fase', 0):.0f}"
    
    ax.text(5, 7.95, 'PRIMARIO', ha='center', fontsize=14, fontweight='bold')
    for i, phase in enumerate(phases_upper):
        text = n1_text if i == 0 else ""
        start, end = draw_winding_rect(ax, x_coords[i], 6.0, text=text)
        terminals['primary'][f'{phase}1'] = start
        terminals['primary'][f'{phase}2'] = end
        ax.text(x_coords[i], start[1] + 0.2, f'{phase}', ha='center', va='bottom', fontsize=12, color='black')
        ax.text(x_coords[i], end[1] - 0.2, f"{phase}'", ha='center', va='top', fontsize=12, color='black')

    ax.text(5, 3.05, 'SECUNDARIO', ha='center', fontsize=14, fontweight='bold')
    for i, phase in enumerate(phases_upper):
        text = n2_text if i == 0 else ""
        start, end = draw_winding_rect(ax, x_coords[i], 1.0, text=text)
        terminals['secondary'][f'{phase.lower()}1'] = start
        terminals['secondary'][f'{phase.lower()}2'] = end
        ax.text(x_coords[i], start[1] + 0.2, f'{phase.lower()}', ha='center', va='bottom', fontsize=12, color='black')
        ax.text(x_coords[i], end[1] - 0.2, f"{phase.lower()}'", ha='center', va='top', fontsize=12, color='black')

    # --- ANALIZAR GRUPO DE CONEXIÓN Y DESPACHAR DIBUJO ---
    conn_str = getattr(d, 'conn', 'Dyn5').upper()
    match = re.search(r'([A-Z])([A-Z]N?|N?[A-Z])(\d+)', conn_str)
    if match:
        conn1 = match.group(1)
        conn2 = match.group(2)
        phase_index = int(match.group(3))
    else: # Fallback
        conn1, conn2, phase_index = 'D', 'YN', 5


    _dispatch_wiring(ax, conn1, terminals['primary'], 'primary', phase_index)
    _dispatch_wiring(ax, conn2, terminals['secondary'], 'secondary', phase_index)