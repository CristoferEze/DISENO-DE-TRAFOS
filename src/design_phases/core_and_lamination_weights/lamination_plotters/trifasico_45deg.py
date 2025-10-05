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

    # --- 2. DEFINICIÓN DE FORMAS CORREGIDAS (vértices) ---
    # Corrigiendo las dimensiones para que coincidan con los cálculos
    
    # Pieza 1 (Columnas laterales): altura corregida para trifásico
    h_col = b_mm + w  # Solo ventana + ancho de lámina
    piece1_shape = [[0, 0], [w, 0], [w, h_col], [0, h_col]]

    # Pieza 3 (Columna central): altura igual a las laterales
    piece3_shape = [[0, 0], [w, 0], [w, h_col], [0, h_col]]

    # Pieza 2 (Yugo): longitud corregida para trifásico
    # Longitud = c + ancho_lámina (yugo corto)
    yoke_len = c_mm + w
    piece2_shape = [[0, 0], [yoke_len, 0], [yoke_len, w], [0, w]]
    
    # Pieza 4 (Yugo largo): longitud = 2*c + ancho_lámina
    yoke_long_len = 2 * c_mm + w
    piece4_shape = [[0, 0], [yoke_long_len, 0], [yoke_long_len, w], [0, w]]

    # --- 3. DIBUJO DEL ENSAMBLE CORREGIDO (posición final) ---
    
    # Yugo inferior izquierdo (Pieza 2)
    ax_main.add_patch(patches.Polygon(piece2_shape, closed=True, fc='lightblue', ec='k'))
    ax_main.text(yoke_len/2, w/2, '2', ha='center', va='center', fontsize=12)

    # Columna izquierda (Pieza 1)
    col_left = [[x, y + w] for x, y in piece1_shape]
    ax_main.add_patch(patches.Polygon(col_left, closed=True, fc='lightcoral', ec='k'))
    ax_main.text(w/2, w + h_col/2, '1', ha='center', va='center', fontsize=12)

    # Columna central (Pieza 3) desplazada en X
    x_center = yoke_len
    col_center = [[x + x_center, y + w] for x, y in piece3_shape]
    ax_main.add_patch(patches.Polygon(col_center, closed=True, fc='lightgreen', ec='k'))
    ax_main.text(x_center + w/2, w + h_col/2, '3', ha='center', va='center', fontsize=12)

    # Yugo inferior derecho (Pieza 2)
    x_right_yoke = x_center + w
    yoke_right = [[x + x_right_yoke, y] for x, y in piece2_shape]
    ax_main.add_patch(patches.Polygon(yoke_right, closed=True, fc='lightblue', ec='k'))
    ax_main.text(x_right_yoke + yoke_len/2, w/2, '2', ha='center', va='center', fontsize=12)

    # Columna derecha (Pieza 1)
    x_col_right = x_right_yoke + yoke_len
    col_right = [[x + x_col_right, y + w] for x, y in piece1_shape]
    ax_main.add_patch(patches.Polygon(col_right, closed=True, fc='lightcoral', ec='k'))
    ax_main.text(x_col_right + w/2, w + h_col/2, '1', ha='center', va='center', fontsize=12)

    # Yugo superior (Pieza 4 - yugo largo)
    x_top_yoke = w
    y_top = w + h_col
    yoke_top = [[x + x_top_yoke, y + y_top] for x, y in piece4_shape]
    ax_main.add_patch(patches.Polygon(yoke_top, closed=True, fc='lightyellow', ec='k'))
    ax_main.text(x_top_yoke + yoke_long_len/2, y_top + w/2, '4', ha='center', va='center', fontsize=12)

    # Etiquetas y título
    ax_main.set_title(f"Trifásico Diagonal - Escalón {step_index + 1}\nAncho de Lámina: {w:.1f} mm")

    # --- 4. DIBUJO DE PIEZAS INDIVIDUALES CORREGIDAS ---
    ax1.set_title(f"Pieza 1 (Columna): {h_col:.1f} × {w:.1f} mm")
    ax1.add_patch(patches.Polygon(piece1_shape, closed=True, fc='lightcoral', ec='k'))
    ax1.text(w/2, h_col/2, '1', ha='center', va='center', fontsize=14)
 
    ax2.set_title(f"Pieza 2 (Yugo Corto): {yoke_len:.1f} × {w:.1f} mm")
    ax2.add_patch(patches.Polygon(piece2_shape, closed=True, fc='lightblue', ec='k'))
    ax2.text(yoke_len/2, w/2, '2', ha='center', va='center', fontsize=14)
 
    ax3.set_title(f"Pieza 3 (Yugo Largo): {yoke_long_len:.1f} × {w:.1f} mm")
    ax3.add_patch(patches.Polygon(piece4_shape, closed=True, fc='lightyellow', ec='k'))
    ax3.text(yoke_long_len/2, w/2, '3', ha='center', va='center', fontsize=14)
 
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