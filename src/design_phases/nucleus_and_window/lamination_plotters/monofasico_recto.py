# src/design_phases/nucleus_and_window/lamination_plotters/monofasico_recto.py
import matplotlib.pyplot as plt
import os

def draw(d, output_dir):
    """Placeholder para el plotter de núcleo monofásico recto."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, 'lamination_plot.png')
    
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.text(0.5, 0.5, "Diagrama de Núcleo Monofásico (Recto)\n(Placeholder)", 
            ha='center', va='center', fontsize=14, color='gray')
    ax.axis('off')
    
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path