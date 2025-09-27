# src/design_phases/nucleus_and_window/core_plotter.py
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def generate_core_plot(d, output_dir='temp'):
    """
    Genera una visualización de la sección transversal del núcleo cruciforme
    y la guarda como una imagen.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, 'core_plot.png')

    fig, ax = plt.subplots(figsize=(6, 6))

    # Dibuja el círculo circunscrito
    circulo = patches.Circle((0, 0), radius=d.D / 2, color='red', fill=False, linestyle='--', label='Diámetro Circunscrito (D)')
    ax.add_patch(circulo)

    # Dibuja los escalones del núcleo
    y_offset = 0
    for i in range(len(d.anchos)):
        ancho = d.anchos[i]
        espesor = d.espesores[i]
        
        # Escalón superior
        rect_sup = patches.Rectangle((-ancho / 2, y_offset), ancho, espesor, edgecolor='black', facecolor='lightblue')
        ax.add_patch(rect_sup)
        
        # Escalón inferior (simétrico)
        rect_inf = patches.Rectangle((-ancho / 2, -y_offset - espesor), ancho, espesor, edgecolor='black', facecolor='lightblue')
        ax.add_patch(rect_inf)

        y_offset += espesor

    # Configuración del gráfico
    ax.set_aspect('equal', adjustable='box')
    lim = d.D / 2 * 1.1
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_xlabel("Ancho (cm)")
    ax.set_ylabel("Espesor (cm)")
    ax.set_title("Sección Transversal del Núcleo Cruciforme")
    ax.grid(True)
    ax.legend()

    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    
    return output_path