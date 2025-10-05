# src/diagrams/three_phase_drawer.py
# -*- coding: utf-8 -*-

from .utils import draw_coil
import matplotlib.pyplot as plt

def draw(ax, d):
    """Dibuja un diagrama de conexión trifásico."""
    terminals = {'primary': {}, 'secondary': {}}
    
    # --- DIBUJAR BOBINAS ---
    phases = ['U', 'V', 'W']
    x_coords = [2.5, 5.0, 7.5]
    n1_text = f"N₁ = {max([data['N_espiras'] for data in d.tap_data.values()]):.0f}" if getattr(d, 'tap_data', None) else "N₁ = 0"
    n2_text = f"N₂ = {getattr(d, 'N2_fase', 0):.0f}"
    
    # Bobinas primarias (arriba)
    ax.text(5, 7.5, 'PRIMARIO', ha='center', fontsize=14, fontweight='bold')
    for i, phase in enumerate(phases):
        text = n1_text if i == 0 else ""
        start, end = draw_coil(ax, x_coords[i], 6.0, text=text)
        # Guardar terminales con claves homogéneas (mayúsculas para primario)
        terminals['primary'][f'{phase}1'] = start
        terminals['primary'][f'{phase}2'] = end
        ax.text(x_coords[i], 6.6, phase, ha='center', va='center', fontsize=12, color='red')

    # Bobinas secundarias (abajo)
    ax.text(5, 3.5, 'SECUNDARIO', ha='center', fontsize=14, fontweight='bold')
    for i, phase in enumerate(phases):
        text = n2_text if i == 0 else ""
        start, end = draw_coil(ax, x_coords[i], 2.0, text=text)
        # Guardar terminales con claves minúsculas para secundario (u,v,w)
        terminals['secondary'][f'{phase.lower()}1'] = start
        terminals['secondary'][f'{phase.lower()}2'] = end
        ax.text(x_coords[i], 2.6, phase.lower(), ha='center', va='center', fontsize=12, color='blue')

    # --- DIBUJAR CONEXIONES SEGÚN TIPO ---
    conn1 = getattr(d, 'conn1', 'D').upper()
    conn2 = getattr(d, 'conn2', 'YN').upper()

    _draw_wiring(ax, conn1, terminals['primary'], 'primary')
    _draw_wiring(ax, conn2, terminals['secondary'], 'secondary')


def _draw_wiring(ax, conn_type, terminals, side):
    """Dibuja las conexiones entre las bobinas (Delta, Estrella)."""
    line_color = 'red' if side == 'primary' else 'blue'

    # Helper to safely access keys (some keys may be missing)
    def t(key):
        return terminals.get(key, (0,0))

    if 'D' in conn_type:  # Conexión Delta
        # Usar puntos U1,U2,V1,V2,W1,W2 para dibujar triángulo
        U1 = t('U1'); U2 = t('U2')
        V1 = t('V1'); V2 = t('V2')
        W1 = t('W1'); W2 = t('W2')
        # Triángulo entre salidas de bobinas (U2->V1, V2->W1, W2->U1)
        ax.plot([U2[0], V1[0]], [U2[1], V1[1]], color=line_color, lw=1.5)
        ax.plot([V2[0], W1[0]], [V2[1], W1[1]], color=line_color, lw=1.5)
        ax.plot([W2[0], U1[0]], [W2[1], U1[1]], color=line_color, lw=1.5)

        # Marcar terminales de línea en la conexión
        if side == 'primary':
            ax.text(U1[0] - 0.5, U1[1], 'L1', ha='right', va='center', fontsize=12)
            ax.text(V1[0] - 0.5, V1[1], 'L2', ha='right', va='center', fontsize=12)
            ax.text(W1[0] - 0.5, W1[1], 'L3', ha='right', va='center', fontsize=12)
        else:
            ax.text(t('u1')[0] - 0.5, t('u1')[1], 'L1', ha='right', va='center', fontsize=12)
            ax.text(t('v1')[0] - 0.5, t('v1')[1], 'L2', ha='right', va='center', fontsize=12)
            ax.text(t('w1')[0] - 0.5, t('w1')[1], 'L3', ha='right', va='center', fontsize=12)

    elif 'Y' in conn_type:  # Conexión Estrella
        # Crear punto neutro en el centro x promedio
        ux = t('U2')[0]; uy = t('U2')[1]
        vx = t('V2')[0]; vy = t('V2')[1]
        wx = t('W2')[0]; wy = t('W2')[1]
        center_x = (ux + vx + wx) / 3.0 if (ux+vx+wx) != 0 else 5.0
        neutral_pt = (center_x, min(uy, vy, wy) - 0.5)

        # Conectar cada bobina al neutro
        ax.plot([t('U2')[0], neutral_pt[0]], [t('U2')[1], neutral_pt[1]], color=line_color, lw=1.5)
        ax.plot([t('V2')[0], neutral_pt[0]], [t('V2')[1], neutral_pt[1]], color=line_color, lw=1.5)
        ax.plot([t('W2')[0], neutral_pt[0]], [t('W2')[1], neutral_pt[1]], color=line_color, lw=1.5)

        # Terminales de línea
        if side == 'primary':
            ax.text(t('U1')[0] - 0.5, t('U1')[1], 'L1', ha='right', va='center', fontsize=12)
            ax.text(t('V1')[0] - 0.5, t('V1')[1], 'L2', ha='right', va='center', fontsize=12)
            ax.text(t('W1')[0] - 0.5, t('W1')[1], 'L3', ha='right', va='center', fontsize=12)
        else:
            ax.text(t('u1')[0] - 0.5, t('u1')[1], 'L1', ha='right', va='center', fontsize=12)
            ax.text(t('v1')[0] - 0.5, t('v1')[1], 'L2', ha='right', va='center', fontsize=12)
            ax.text(t('w1')[0] - 0.5, t('w1')[1], 'L3', ha='right', va='center', fontsize=12)

        if 'N' in conn_type:
            # Dibujar neutro vertical y marcar N
            ax.plot([neutral_pt[0], neutral_pt[0]], [neutral_pt[1], neutral_pt[1] - 0.5], color=line_color, lw=1.5)
            ax.text(neutral_pt[0] + 0.2, neutral_pt[1] - 0.5, 'N', ha='left', va='center', fontsize=12)