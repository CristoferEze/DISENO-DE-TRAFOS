# src/design_phases/nucleus_and_window/lamination_plotters/monofasico_recto.py
import matplotlib.pyplot as plt
import os

def draw(d, output_dir, step_index=0):
    """Placeholder para el plotter de núcleo monofásico recto.
    Ahora acepta step_index y devuelve la ruta absoluta del archivo generado.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, f'lamination_plot_step_{step_index + 1}.png')
    
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.text(0.5, 0.5, f"Diagrama de Núcleo Monofásico (Recto)\nEscalón {step_index + 1}",
            ha='center', va='center', fontsize=14, color='gray')
    ax.axis('off')
    
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return os.path.abspath(output_path)