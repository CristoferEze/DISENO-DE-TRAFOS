# src/design_phases/nucleus_and_window/lamination_plotter.py
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def _draw_trifasico_plot(axes, d):
    """Dibuja el ensamble y las piezas de un núcleo trifásico."""
    ax_main, ax1, ax2, ax3 = axes
    
    # Dimensiones en cm
    a1, g, b, L, c = d.anchos[0], d.g, d.b, d.L_trifasico, d.c
    
    # --- DIBUJO DEL ENSAMBLE (ax_main) ---
    x_col_izq = g
    x_col_cen = g + c
    x_col_der = g + c + a1 + c
    
    # Yugos
    ax_main.add_patch(patches.Rectangle((0, 0), L, g, fc='lightgray', ec='k'))
    ax_main.add_patch(patches.Rectangle((0, g + b), L, g, fc='lightgray', ec='k'))
    # Columnas
    ax_main.add_patch(patches.Rectangle((x_col_izq, g), g, b, fc='lightgray', ec='k'))
    ax_main.add_patch(patches.Rectangle((x_col_cen, g), a1, b, fc='lightgray', ec='k'))
    ax_main.add_patch(patches.Rectangle((x_col_der, g), g, b, fc='lightgray', ec='k'))
    
    # Cotas del ensamble
    ax_main.text(L / 2, -g * 0.5, f'{L*10:.1f} mm', ha='center', va='top', fontsize=9)
    ax_main.text(-L*0.05, (b+2*g)/2, f'{ (b+2*g)*10:.1f} mm', ha='right', va='center', fontsize=9, rotation=90)
    ax_main.set_title("Ensamble de Núcleo Trifásico")
    
    # --- DIBUJO DE PIEZAS INDIVIDUALES ---
    # Pieza 1 (Columna Central)
    ax1.add_patch(patches.Rectangle((0, 0), b, a1, fc='lightgray', ec='k'))
    ax1.text(b/2, a1/2, '1', ha='center', va='center', fontsize=16)
    ax1.text(b/2, -a1*0.4, f'{b*10:.1f} mm', ha='center', va='top', fontsize=9)
    ax1.text(-b*0.05, a1/2, f'{a1*10:.1f} mm', ha='right', va='center', fontsize=9, rotation=90)

    # Pieza 2 (Columnas Laterales)
    ax2.add_patch(patches.Rectangle((0, 0), b, g, fc='lightgray', ec='k'))
    ax2.text(b/2, g/2, '2', ha='center', va='center', fontsize=16)
    ax2.text(b/2, -g*0.4, f'{b*10:.1f} mm', ha='center', va='top', fontsize=9)
    ax2.text(-b*0.05, g/2, f'{g*10:.1f} mm', ha='right', va='center', fontsize=9, rotation=90)
    
    # Pieza 3 (Yugos)
    ax3.add_patch(patches.Rectangle((0, 0), L, g, fc='lightgray', ec='k'))
    ax3.text(L/2, g/2, '3', ha='center', va='center', fontsize=16)
    ax3.text(L/2, -g*0.4, f'{L*10:.1f} mm', ha='center', va='top', fontsize=9)
    ax3.text(-L*0.02, g/2, f'{g*10:.1f} mm', ha='right', va='center', fontsize=9, rotation=90)

def generate_lamination_plot(d, output_dir='temp'):
    """Genera una visualización del ensamble del núcleo y sus piezas únicas."""
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    output_path = os.path.join(output_dir, 'lamination_plot.png')

    # Crear subplots: uno grande para el ensamble, y varios pequeños para las piezas
    fig, axes = plt.subplots(4, 1, figsize=(8, 10), gridspec_kw={'height_ratios': [4, 1, 1, 1]})
    
    # Por ahora, nos centramos en el caso trifásico que es más complejo
    if d.fases == 3:
        _draw_trifasico_plot(axes, d)
    else:
        # Se podría implementar una función _draw_monofasico_plot similar aquí
        axes[0].text(0.5, 0.5, "Plot monofásico no implementado", ha='center')

    for ax in axes:
        ax.axis('equal')
        ax.axis('off')
        
    fig.suptitle("Peso del Núcleo por Laminaciones", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    
    return output_path