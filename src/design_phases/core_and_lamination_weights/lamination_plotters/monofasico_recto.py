import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def draw(d, output_dir, step_index=0):
    """
    Dibuja el ensamble y las piezas de un núcleo monofásico con corte recto.
    Usa las dimensiones específicas del escalón: d.anchos[step_index] (ancho 'a')
    y d.espesores[step_index] (espesor del paquete) cuando estén disponibles.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'lamination_plot_step_{step_index + 1}.png')

    fig = plt.figure(figsize=(8, 8))
    gs = fig.add_gridspec(3, 1, height_ratios=[4, 1, 1])
    
    ax_main = fig.add_subplot(gs[0, 0]) # Ensamble principal
    ax1 = fig.add_subplot(gs[1, 0])     # Pieza 1 (Columna)
    ax2 = fig.add_subplot(gs[2, 0])     # Pieza 2 (Yugo)
    
    # --- 1. CÁLCULO CENTRALIZADO DE DIMENSIONES (usar valores por escalón) ---
    b_mm = getattr(d, 'b', 0.0) * 10.0  # Alto de la ventana en mm
    c_mm = getattr(d, 'c', 0.0) * 10.0  # Ancho de la ventana en mm

    # Ancho de lamina (a) y espesor del paquete (e) para el escalón actual (valores en cm en d)
    ancho_cm = (d.anchos[step_index] if getattr(d, 'anchos', None) and len(d.anchos) > step_index else 0.0)
    espesor_cm = (d.espesores[step_index] if getattr(d, 'espesores', None) and len(d.espesores) > step_index else 0.0)

    current_a_mm = ancho_cm * 10.0
    espesor_mm = espesor_cm * 10.0

    lamination_width_mm = current_a_mm if current_a_mm > 0 else getattr(d, 'g', 0.0) * 10.0
    # Usar espesor del paquete como altura del yugo cuando esté disponible
    yoke_height_mm = espesor_mm if espesor_mm > 0 else lamination_width_mm

    piece_dims = {
        '1': { # Pieza 1 (Columna)
            'width': lamination_width_mm,
            'height': b_mm
        },
        '2': { # Pieza 2 (Yugo)
            'width': c_mm + 2 * lamination_width_mm,
            'height': yoke_height_mm
        }
    }

    # --- 2. DIBUJO DEL ENSAMBLE ---
    # Yugo inferior
    ax_main.add_patch(patches.Rectangle((0, 0), piece_dims['2']['width'], piece_dims['2']['height'], fc='w', ec='k'))
    ax_main.text(piece_dims['2']['width']/2, piece_dims['2']['height']/2, '2', ha='center', va='center', fontsize=18)
    
    # Columna izquierda
    ax_main.add_patch(patches.Rectangle((0, piece_dims['2']['height']), piece_dims['1']['width'], piece_dims['1']['height'], fc='w', ec='k'))
    ax_main.text(piece_dims['1']['width']/2, piece_dims['2']['height'] + piece_dims['1']['height']/2, '1', ha='center', va='center', fontsize=18)
    
    # Columna derecha
    x_col_der = piece_dims['2']['width'] - piece_dims['1']['width']
    ax_main.add_patch(patches.Rectangle((x_col_der, piece_dims['2']['height']), piece_dims['1']['width'], piece_dims['1']['height'], fc='w', ec='k'))
    ax_main.text(x_col_der + piece_dims['1']['width']/2, piece_dims['2']['height'] + piece_dims['1']['height']/2, '1', ha='center', va='center', fontsize=18)
    
    # Yugo superior
    y_yugo_sup = piece_dims['2']['height'] + piece_dims['1']['height']
    ax_main.add_patch(patches.Rectangle((0, y_yugo_sup), piece_dims['2']['width'], piece_dims['2']['height'], fc='w', ec='k'))
    ax_main.text(piece_dims['2']['width']/2, y_yugo_sup + piece_dims['2']['height']/2, '2', ha='center', va='center', fontsize=18)

    ax_main.set_title(f"Monofásico Recto - Escalón {step_index + 1}\nAncho (a): {lamination_width_mm:.1f} mm  Espesor paquete: {espesor_mm:.1f} mm")

    # --- 3. DIBUJO DE PIEZAS INDIVIDUALES ---
    ax1.set_title("Pieza 1 (Columna)")
    # Mostrar pieza 1 en vista horizontal (largo x ancho)
    ax1.add_patch(patches.Rectangle((0, 0), piece_dims['1']['height'], piece_dims['1']['width'], fc='w', ec='k'))
    ax1.text(piece_dims['1']['height']/2, piece_dims['1']['width']/2, '1', ha='center', va='center', fontsize=12)

    ax2.set_title("Pieza 2 (Yugo)")
    ax2.add_patch(patches.Rectangle((0, 0), piece_dims['2']['width'], piece_dims['2']['height'], fc='w', ec='k'))
    ax2.text(piece_dims['2']['width']/2, piece_dims['2']['height']/2, '2', ha='center', va='center', fontsize=12)

    # --- INICIO DE LA CORRECCIÓN ---
    # Aplicar configuraciones comunes a TODOS los subplots
    for ax in [ax_main, ax1, ax2]:
        ax.axis('equal')
        ax.axis('off')
    # --- FIN DE LA CORRECCIÓN ---
    
    plt.tight_layout(pad=1.5)
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    return os.path.abspath(output_path)