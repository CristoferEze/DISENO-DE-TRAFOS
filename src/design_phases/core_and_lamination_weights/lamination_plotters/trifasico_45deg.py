import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw(d, output_dir='temp', step_index=0):
    """
    Dibuja el ensamble y las piezas de un núcleo trifásico con corte a 45 grados.
    Las geometrías se definen mediante polígonos y se colocan de forma que el
    núcleo cierre correctamente. Devuelve la ruta absoluta del PNG generado.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'lamination_trifasico_45deg_step_{step_index + 1}.png')

    fig = plt.figure(figsize=(10, 8))
    gs = fig.add_gridspec(4, 1, height_ratios=[4, 1, 1, 1])
    ax_main = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[1, 0])
    ax2 = fig.add_subplot(gs[2, 0])
    ax3 = fig.add_subplot(gs[3, 0])

    # --- 1. CÁLCULO DE DIMENSIONES ---
    b_mm = getattr(d, 'b', 0.0) * 10.0
    c_mm = getattr(d, 'c', 0.0) * 10.0
    current_a_mm = (d.anchos[step_index] if getattr(d, 'anchos', None) and len(d.anchos) > step_index else 0.0) * 10.0
    w = current_a_mm if current_a_mm > 0 else getattr(d, 'g', 0.0) * 10.0

    # --- 2. DEFINICIÓN DE FORMAS (vértices) ---
    # Pieza 1 (Columnas laterales): trapecio para encaje a 45°
    h_col = b_mm + w
    piece1_shape = [[0, 0], [w, w], [w, h_col], [0, h_col - w]]

    # Pieza 3 (Columna central): paralelogramo desplazado
    h_center_col = b_mm + 2 * w
    piece3_shape = [[w, 0], [0, w], [0, h_center_col - w], [w, h_center_col]]

    # Pieza 2 (Yugo): perfil con ranuras formadas por triángulos/paralelogramos
    yoke_len = 2 * c_mm + 3 * w
    notch1_x = c_mm + w
    notch2_x = 2 * c_mm + 2 * w
    piece2_shape = [
        [0, w], [notch1_x, w], [notch1_x + w, 0], [notch2_x, 0],
        [notch2_x + w, w], [yoke_len, w], [yoke_len, 0], [0, 0]
    ]

    # --- 3. DIBUJO DEL ENSAMBLE (posición final) ---
    # Yugo inferior: usar piece2_shape invertida en Y para ajustarla debajo de las columnas
    yoke_bottom = [[x, y - w] for x, y in piece2_shape]  # desplazar hacia abajo
    ax_main.add_patch(patches.Polygon(yoke_bottom, closed=True, fc='w', ec='k'))

    # Columna izquierda (Pieza 1) posicionada sobre el yugo inferior
    col_left = [[x, y] for x, y in piece1_shape]
    col_left = [[x, y + w] for x, y in col_left]
    ax_main.add_patch(patches.Polygon(col_left, closed=True, fc='w', ec='k'))

    # Columna central (Pieza 3) desplazada en X por c_mm + w
    x_center = c_mm + w
    col_center = [[x + x_center, y] for x, y in piece3_shape]
    ax_main.add_patch(patches.Polygon(col_center, closed=True, fc='w', ec='k'))

    # Columna derecha (Pieza 1 reflejada) desplazada en X por 2*(c_mm + w)
    x_right = 2 * (c_mm + w)
    col_right_reflected = [[w - x, y] for x, y in piece1_shape]  # reflejar horizontalmente
    col_right = [[x + x_right, y + w] for x, y in col_right_reflected]
    ax_main.add_patch(patches.Polygon(col_right, closed=True, fc='w', ec='k'))

    # Yugo superior: usar piece2_shape elevado por la altura total de las columnas
    y_top = b_mm + 2 * w
    yoke_top = [[x, y + y_top] for x, y in piece2_shape]
    ax_main.add_patch(patches.Polygon(yoke_top, closed=True, fc='w', ec='k'))

    # Etiquetas y título
    ax_main.set_title(f"Trifásico 45° - Escalón {step_index + 1}\nAncho de Lámina: {w:.1f} mm")
    ax_main.text((yoke_len) / 2, (b_mm + w) / 2 + w, "Ventanas y columnas (vista ensamblada)", ha='center', va='center', fontsize=10, alpha=0.6)

    # --- 4. DIBUJO DE PIEZAS INDIVIDUALES ---
    ax1.set_title("Pieza 1 (Columna Lateral)")
    ax1.add_patch(patches.Polygon(piece1_shape, closed=True, fc='w', ec='k'))
 
    ax2.set_title("Pieza 2 (Yugo)")
    ax2.add_patch(patches.Polygon(piece2_shape, closed=True, fc='w', ec='k'))
 
    ax3.set_title("Pieza 3 (Columna Central)")
    ax3.add_patch(patches.Polygon(piece3_shape, closed=True, fc='w', ec='k'))
 
    # --- INICIO DE LA CORRECCIÓN ---
    # Aplicar configuraciones comunes a TODOS los subplots
    for ax in [ax_main, ax1, ax2, ax3]:
        ax.axis('equal')
        ax.axis('off')
    # --- FIN DE LA CORRECCIÓN ---

    plt.tight_layout(pad=1.5)
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    return os.path.abspath(output_path)