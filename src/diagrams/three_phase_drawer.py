# src/diagrams/three_phase_drawer.py
# -*- coding: utf-8 -*-

from .utils import draw_winding_rect
import matplotlib.pyplot as plt
import re

def draw(ax, d):
    """Dibuja un diagrama de conexión trifásico usando rectángulos."""
    terminals = {'primary': {}, 'secondary': {}}
    
    # --- DIBUJAR BOBINAS ---
    phases_upper = ['U', 'V', 'W']
    x_coords = [2.5, 5.0, 7.5]
    
    # Manejar el caso donde no hay taps
    if getattr(d, 'tap_data', None) and d.tap_data:
        n1_val = max(data['N_espiras'] for data in d.tap_data.values())
        n1_text = f"N₁ = {n1_val:.0f}"
    else:
        n1_text = f"N₁ = {getattr(d, 'N1_fase', 0):.0f}"
        
    n2_text = f"N₂ = {getattr(d, 'N2_fase', 0):.0f}"
    
    # Bobinas primarias (arriba)
    ax.text(5, 7.95, 'PRIMARIO', ha='center', fontsize=14, fontweight='bold')
    for i, phase in enumerate(phases_upper):
        text = n1_text if i == 0 else ""
        start, end = draw_winding_rect(ax, x_coords[i], 6.0, text=text)
        terminals['primary'][f'{phase}1'] = start
        terminals['primary'][f'{phase}2'] = end
        # Etiquetado: separar más la notación de entrada y salida de la bobina
        label_in_pos = (x_coords[i], start[1] + 0.5)
        label_out_pos = (x_coords[i], end[1] - 0.5)
        ax.text(label_in_pos[0], label_in_pos[1], f'{phase}', ha='center', va='bottom', fontsize=12, color='black')
        ax.text(label_out_pos[0], label_out_pos[1], f"{phase}'", ha='center', va='top', fontsize=12, color='black')

    # Bobinas secundarias (abajo)
    ax.text(5, 3.05, 'SECUNDARIO', ha='center', fontsize=14, fontweight='bold')
    for i, phase in enumerate(phases_upper):
        text = n2_text if i == 0 else ""
        start, end = draw_winding_rect(ax, x_coords[i], 1.0, text=text)
        terminals['secondary'][f'{phase.lower()}1'] = start
        terminals['secondary'][f'{phase.lower()}2'] = end
        # Etiquetado secundario: separar más la notación de entrada y salida de la bobina
        label_in_pos = (x_coords[i], start[1] + 0.5)
        label_out_pos = (x_coords[i], end[1] - 0.5)
        ax.text(label_in_pos[0], label_in_pos[1], f'{phase.lower()}', ha='center', va='bottom', fontsize=12, color='black')
        ax.text(label_out_pos[0], label_out_pos[1], f"{phase.lower()}'", ha='center', va='top', fontsize=12, color='black')

    # --- DIBUJAR CONEXIONES SEGÚN TIPO ---
    # Intentar leer un campo compacto 'conn' (p.ej. "Dyn5") o usar conn1/conn2 por separado.
    conn_str = getattr(d, 'conn', None)
    if conn_str:
        conn_str = conn_str.upper()
        match = re.search(r'([A-Z])([A-Z]N?|N?[A-Z])(\d+)', conn_str)
        if match:
            conn1 = match.group(1)
            conn2 = match.group(2)
            phase_index = int(match.group(3))
        else:
            conn1 = getattr(d, 'conn1', 'D').upper()
            conn2 = getattr(d, 'conn2', 'YN').upper()
            phase_index = 5
    else:
        conn1 = getattr(d, 'conn1', 'D').upper()
        conn2 = getattr(d, 'conn2', 'YN').upper()
        phase_index = 5

    # La polaridad del secundario se invierte para TODOS los índices horarios IMPARES.
    invert_secondary = (phase_index % 2 != 0)

    _draw_wiring(ax, conn1, terminals['primary'], 'primary')
    _draw_wiring(ax, conn2, terminals['secondary'], 'secondary', invert_polarity=invert_secondary)


def _draw_wiring(ax, conn_type, terminals, side, invert_polarity=False):
    """Dibuja las conexiones con ruteado limpio para evitar colisiones.
    Si invert_polarity es True, se intercambian inicio/fin de cada bobina para
    representar la inversión de polaridad en el secundario.
    """
    line_color = 'black'
    
    if side == 'primary':
        p = ['U', 'V', 'W']
    else:
        p = ['u', 'v', 'w']

    # Puntos de inicio (1) y fin (2) de cada bobina
    p1_start, p1_end = terminals[f'{p[0]}1'], terminals[f'{p[0]}2']
    p2_start, p2_end = terminals[f'{p[1]}1'], terminals[f'{p[1]}2']
    p3_start, p3_end = terminals[f'{p[2]}1'], terminals[f'{p[2]}2']

    # --- INVERSIÓN DE POLARIDAD (cuando corresponde) ---
    if invert_polarity:
        p1_start, p1_end = p1_end, p1_start
        p2_start, p2_end = p2_end, p2_start
        p3_start, p3_end = p3_end, p3_start

    if 'D' in conn_type:
        # CONEXIÓN DELTA: Conecta la salida (X') a la entrada de la siguiente (Y).
        jog_len = 0.4  # Longitud de los segmentos horizontales en salida y entrada.

        # --- Conexión U' -> V (p1_end -> p2_start) ---
        # Lógica: Horizontal en salida -> Diagonal -> Horizontal en entrada
        x_path1 = [p1_end[0], p1_end[0] + jog_len, p2_start[0] - jog_len, p2_start[0]]
        y_path1 = [p1_end[1], p1_end[1],           p2_start[1],           p2_start[1]]
        ax.plot(x_path1, y_path1, color=line_color, lw=1.5)
        # Posicionar etiqueta en el centro de la diagonal
        mid_x1 = (p1_end[0] + p2_start[0]) / 2
        mid_y1 = (p1_end[1] + p2_start[1]) / 2
        ax.text(mid_x1, mid_y1, f"{p[0]}'→{p[1]}", ha='center', va='center', fontsize=10, backgroundcolor='white', bbox=dict(facecolor='white', edgecolor='none', pad=0.1))

        # --- Conexión V' -> W (p2_end -> p3_start) ---
        # Misma lógica: Horizontal -> Diagonal -> Horizontal
        x_path2 = [p2_end[0], p2_end[0] + jog_len, p3_start[0] - jog_len, p3_start[0]]
        y_path2 = [p2_end[1], p2_end[1],           p3_start[1],           p3_start[1]]
        ax.plot(x_path2, y_path2, color=line_color, lw=1.5)
        # Posicionar etiqueta en el centro de la diagonal
        mid_x2 = (p2_end[0] + p3_start[0]) / 2
        mid_y2 = (p2_end[1] + p3_start[1]) / 2
        ax.text(mid_x2, mid_y2, f"{p[1]}'→{p[2]}", ha='center', va='center', fontsize=10, backgroundcolor='white', bbox=dict(facecolor='white', edgecolor='none', pad=0.1))

        # --- Conexión W' -> U (p3_end -> p1_start) (retorno por fuera) ---
        # Lógica ortogonal de 5 segmentos para rodear la primera bobina.
        y_level = p3_end[1] - 0.4      # Nivel horizontal inferior
        x_outside = p1_start[0] - 0.6  # Coordenada X exterior
        
        # Ruta de 5 segmentos: Abajo -> Izquierda -> Arriba -> Derecha
        x_path3 = [p3_end[0], p3_end[0], x_outside,   x_outside,   p1_start[0]]
        y_path3 = [p3_end[1], y_level,   y_level,     p1_start[1], p1_start[1]]
        ax.plot(x_path3, y_path3, color=line_color, lw=1.5)
        ax.text((p3_end[0] + x_outside) / 2, y_level + 0.05, f"{p[2]}'→{p[0]}", ha='center', va='bottom', fontsize=10)

    elif 'Y' in conn_type:
        # CONEXIÓN ESTRELLA CON RUTEADO LIMPIO
        neutral_y = p1_end[1] - 0.4
        
        # Barra horizontal del neutro
        ax.plot([p1_end[0], p3_end[0]], [neutral_y, neutral_y], color=line_color, lw=1.5)

        # Conexiones verticales
        ax.plot([p1_end[0], p1_end[0]], [p1_end[1], neutral_y], color=line_color, lw=1.5)
        ax.plot([p2_end[0], p2_end[0]], [p2_end[1], neutral_y], color=line_color, lw=1.5)
        ax.plot([p3_end[0], p3_end[0]], [p3_end[1], neutral_y], color=line_color, lw=1.5)

        if 'N' in conn_type:
            # Salida del neutro
            neutral_x = p2_end[0] # Centro
            ax.plot([neutral_x, neutral_x], [neutral_y, neutral_y - 0.5], color=line_color, lw=1.5)
            ax.text(neutral_x, neutral_y - 0.7, 'N', ha='center', va='top', fontsize=12, fontweight='bold')