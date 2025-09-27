# src/design_phases/nucleus_and_window/lamination_plotter.py
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def generate_lamination_plot(d, output_dir='temp'):
    """
    Genera una visualización de las laminaciones del primer escalón del núcleo,
    inspirado en los diagramas del libro de diseño.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, 'lamination_plot.png')

    # Usar las dimensiones calculadas. a1 es el ancho del primer escalón.
    a1 = d.anchos[0] if d.anchos else 0
    b = d.b if getattr(d, 'b', None) is not None else 0 # Alto de la ventana (y del bobinado)
    c_prima = d.c_prima if getattr(d, 'c_prima', None) is not None else 0

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_aspect('equal', adjustable='box')
    
    # Dimensiones para el dibujo (no a escala real, pero proporcionales)
    L_total = a1 + c_prima
    H_total = b + 2 * a1
    
    # Dibujar el contorno del núcleo (las dos "T" juntas)
    # Pieza Larga (I)
    rect_I = patches.Rectangle((0, a1), L_total, b, edgecolor='black', facecolor='lightgray', linewidth=1.5)
    ax.add_patch(rect_I)
    # Yugo superior
    rect_yugo_sup = patches.Rectangle(((L_total - a1) / 2, b + a1), a1, a1, edgecolor='black', facecolor='lightgray', linewidth=1.5)
    ax.add_patch(rect_yugo_sup)
    # Yugo inferior
    rect_yugo_inf = patches.Rectangle(((L_total - a1) / 2, 0), a1, a1, edgecolor='black', facecolor='lightgray', linewidth=1.5)
    ax.add_patch(rect_yugo_inf)

    # Añadir cotas y medidas
    # Ancho a1
    ax.plot([ (L_total - a1) / 2, (L_total + a1) / 2 ], [b + a1 + a1*0.2, b + a1 + a1*0.2], 'k')
    ax.text(L_total / 2, b + a1 + a1*0.25, f'$a_1={a1:.2f}$ cm', ha='center', va='bottom')

    # Ancho c'
    ax.plot([a1, a1 + c_prima], [a1-a1*0.2, a1-a1*0.2], 'k')
    ax.text(a1 + c_prima/2, a1-a1*0.25, f"$c'={c_prima:.2f}$ cm", ha='center', va='top')
    
    # Alto b
    ax.plot([L_total + a1*0.2, L_total + a1*0.2], [a1, a1 + b], 'k')
    ax.text(L_total + a1*0.25, a1 + b/2, f'$b={b:.2f}$ cm', ha='left', va='center', rotation=90)

    # Limpieza del gráfico
    ax.set_xlim(-a1*0.5 if a1 else -1, L_total + a1*0.5 if L_total else 1)
    ax.set_ylim(-a1*0.5 if a1 else -1, H_total + a1*0.5 if H_total else 1)
    ax.axis('off')
    ax.set_title("Dimensiones de Laminación (Primer Escalón)")

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    return output_path