import os
import matplotlib.pyplot as plt

def draw(d, output_dir='temp'):
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, 'lam_monofasico_45deg.png')
    fig, ax = plt.subplots(figsize=(5,4))
    ax.set_title('Monofásico 45° - placeholder')

    esp = getattr(d, 'espesores', [])
    anchos = getattr(d, 'anchos', [])
    y = 0
    for i, espesor in enumerate(esp):
        ancho = anchos[i] if i < len(anchos) else 1.0
        rect = plt.Rectangle((0, y), ancho, espesor, fill=None, edgecolor='black')
        ax.add_patch(rect)
        ax.text(ancho/2, y + espesor/2, f'E{i+1}', ha='center', va='center', fontsize=8)
        y += espesor + 0.08

    ax.set_xlim(0, max(anchos) if anchos else 1.0)
    ax.set_ylim(0, y if y > 0 else 1.0)
    ax.axis('equal')

    fig.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return filename