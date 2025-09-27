# src/design_phases/nucleus_and_window/lamination_plotters/trifasico_recto.py
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def draw(d, output_dir, step_index=0):
    """
    Dibuja el ensamble y las piezas de un núcleo trifásico con corte recto
    para un escalón específico (step_index). Devuelve la RUTA ABSOLUTA
    del archivo generado.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, f'lamination_plot_step_{step_index + 1}.png')

    # Crear una figura con un layout específico: un subplot grande arriba y tres más pequeños abajo
    fig = plt.figure(figsize=(8, 10))
    gs = fig.add_gridspec(4, 2, height_ratios=[4, 1, 1, 1], width_ratios=[1,1])
    
    ax_main = fig.add_subplot(gs[0, :]) # Ensamble principal ocupa toda la primera fila
    ax1 = fig.add_subplot(gs[1, :])     # Pieza 1
    ax2 = fig.add_subplot(gs[2, :])     # Pieza 2
    ax3 = fig.add_subplot(gs[3, :])     # Pieza 3
    
    # --- Dimensiones Clave en mm ---
    b_mm = getattr(d, 'b', 0.0) * 10.0
    g_mm = getattr(d, 'g', 0.0) * 10.0
    a1_mm = (d.anchos[0] if getattr(d, 'anchos', None) else 0.0) * 10.0
    current_a_mm = (d.anchos[step_index] if getattr(d, 'anchos', None) and len(d.anchos) > step_index else 0.0) * 10.0

    # Longitudes de las piezas según el diagrama de referencia
    l1_mm = b_mm + g_mm
    l2_mm = getattr(d, 'c', 0.0) * 10.0 + g_mm
    l3_mm = getattr(d, 'c', 0.0) * 10.0 + a1_mm + g_mm

    # --- 1. DIBUJO DEL ENSAMBLE (ax_main) ---
    # Columna central
    ax_main.add_patch(patches.Rectangle((g_mm, 0), a1_mm, b_mm, fc='w', ec='k'))
    ax_main.text(g_mm + a1_mm/2, b_mm/2, '1', ha='center', va='center', fontsize=20)
    # Columnas laterales
    ax_main.add_patch(patches.Rectangle((0, 0), g_mm, b_mm, fc='w', ec='k'))
    ax_main.text(g_mm/2, b_mm/2, '1', ha='center', va='center', fontsize=20)
    ax_main.add_patch(patches.Rectangle((g_mm + a1_mm, 0), g_mm, b_mm, fc='w', ec='k'))
    ax_main.text(g_mm + a1_mm + g_mm/2, b_mm/2, '1', ha='center', va='center', fontsize=20)
    # Yugo inferior
    ax_main.add_patch(patches.Rectangle((0, -g_mm), g_mm + a1_mm + g_mm, g_mm, fc='w', ec='k'))
    ax_main.text((g_mm*2+a1_mm)/2, -g_mm/2, '3', ha='center', va='center', fontsize=20)
    # Yugo superior
    ax_main.add_patch(patches.Rectangle((0, b_mm), g_mm + a1_mm + g_mm, g_mm, fc='w', ec='k'))
    ax_main.text((g_mm*2+a1_mm)/2, b_mm + g_mm/2, '2', ha='center', va='center', fontsize=20)

    # Cotas del ensamble
    total_width = 2*g_mm + a1_mm
    ax_main.text(0, -g_mm*1.5, f'{g_mm:.1f} mm', ha='center', va='top')
    ax_main.text(g_mm + a1_mm/2, -g_mm*1.5, f'{a1_mm:.1f} mm', ha='center', va='top')
    ax_main.plot([0, g_mm], [-g_mm*1.2, -g_mm*1.2], 'k')
    ax_main.plot([g_mm, g_mm+a1_mm], [-g_mm*1.2, -g_mm*1.2], 'k')
    ax_main.text(-total_width*0.1, b_mm/2, f'{b_mm:.1f} mm', ha='right', va='center', rotation=90)
    
    ax_main.set_title(f"Dimensionado de Laminación\nEscalón {step_index + 1} (Ancho: {current_a_mm:.1f} mm)")

    # --- 2. DIBUJO DE PIEZAS INDIVIDUALES ---
    for ax in [ax1, ax2, ax3]:
        ax.axis('off')
    # Pieza 1
    ax1.add_patch(patches.Rectangle((0, 0), l1_mm, g_mm, fc='w', ec='k'))
    ax1.text(l1_mm/2, g_mm/2, '1', ha='center', va='center', fontsize=12)
    ax1.text(l1_mm/2, -g_mm*0.4, f'{l1_mm:.1f} mm', ha='center', va='top')
    ax1.text(-l1_mm*0.02, g_mm/2, f'{g_mm:.1f} mm', ha='right', va='center')
    # Pieza 2
    ax2.add_patch(patches.Rectangle((0, 0), l2_mm, g_mm, fc='w', ec='k'))
    ax2.text(l2_mm/2, g_mm/2, '2', ha='center', va='center', fontsize=12)
    ax2.text(l2_mm/2, -g_mm*0.4, f'{l2_mm:.1f} mm', ha='center', va='top')
    ax2.text(-l2_mm*0.02, g_mm/2, f'{g_mm:.1f} mm', ha='right', va='center')
    # Pieza 3
    ax3.add_patch(patches.Rectangle((0, 0), l3_mm, g_mm, fc='w', ec='k'))
    ax3.text(l3_mm/2, g_mm/2, '3', ha='center', va='center', fontsize=12)
    ax3.text(l3_mm/2, -g_mm*0.4, f'{l3_mm:.1f} mm', ha='center', va='top')
    ax3.text(-l3_mm*0.02, g_mm/2, f'{g_mm:.1f} mm', ha='right', va='center')

    for ax in [ax_main, ax1, ax2, ax3]:
        ax.axis('equal')
        ax.axis('off')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    return os.path.abspath(output_path)