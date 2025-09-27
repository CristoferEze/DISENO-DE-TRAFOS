import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw(d, output_dir, step_index=0):
    """
    Dibuja el ensamble y las piezas de un núcleo monofásico con corte a 45 grados.
    Usa las dimensiones específicas del escalón: d.anchos[step_index] (ancho 'a')
    y d.espesores[step_index] (espesor del paquete) cuando estén disponibles.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'lamination_monofasico_45deg_step_{step_index + 1}.png')

    fig = plt.figure(figsize=(8, 8))
    gs = fig.add_gridspec(3, 1, height_ratios=[4, 1, 1])
    
    ax_main = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[1, 0])
    ax2 = fig.add_subplot(gs[2, 0])
    
    # --- 1. CÁLCULO DE DIMENSIONES (usar valores por escalón) ---
    b_mm = getattr(d, 'b', 0.0) * 10.0
    c_mm = getattr(d, 'c', 0.0) * 10.0

    ancho_cm = (d.anchos[step_index] if getattr(d, 'anchos', None) and len(d.anchos) > step_index else 0.0)
    espesor_cm = (d.espesores[step_index] if getattr(d, 'espesores', None) and len(d.espesores) > step_index else 0.0)

    a_mm = ancho_cm * 10.0
    e_mm = espesor_cm * 10.0

    w = a_mm if a_mm > 0 else getattr(d, 'g', 0.0) * 10.0  # ancho de lámina en mm
    yoke_h = e_mm if e_mm > 0 else w  # usar espesor del paquete para alto de yugo si está disponible

    # --- 2. DIBUJO DEL ENSAMBLE ---
    # Coordenadas adaptadas a 45° con desplazamientos según 'w' y 'yoke_h'
    yoke_bottom = [[w, 0], [c_mm + w, 0], [c_mm + 2*w, yoke_h], [0, yoke_h]]
    col_left = [[0, yoke_h], [w, yoke_h], [w, b_mm + yoke_h], [0, b_mm + 2*yoke_h - w]]
    col_right = [[c_mm + w, yoke_h], [c_mm + 2*w, yoke_h], [c_mm + 2*w, b_mm + yoke_h], [c_mm + w, b_mm + 2*yoke_h - w]]
    yoke_top = [[w, b_mm + 2*yoke_h - w], [c_mm + w, b_mm + 2*yoke_h - w], [c_mm + 2*w, b_mm + yoke_h], [0, b_mm + yoke_h]]

    ax_main.add_patch(patches.Polygon(yoke_bottom, closed=True, fc='w', ec='k'))
    ax_main.add_patch(patches.Polygon(col_left, closed=True, fc='w', ec='k'))
    ax_main.add_patch(patches.Polygon(col_right, closed=True, fc='w', ec='k'))
    ax_main.add_patch(patches.Polygon(yoke_top, closed=True, fc='w', ec='k'))

    # Etiquetas
    ax_main.text(c_mm/2 + w, (b_mm/2) + yoke_h, "Ventana", ha='center', va='center', fontsize=12, alpha=0.6)
    ax_main.set_title(f"Monofásico 45° - Escalón {step_index + 1}\nAncho a: {a_mm:.1f} mm  Espesor paquete: {e_mm:.1f} mm")

    # --- 3. DIBUJO DE PIEZAS INDIVIDUALES ---
    # Pieza 1 (Columna) - trapecio vertical según 'w' y 'yoke_h'
    h_col = b_mm + yoke_h
    col_shape = [[0, 0], [w, yoke_h], [w, h_col], [0, h_col - yoke_h]]
    ax1.add_patch(patches.Polygon(col_shape, closed=True, fc='w', ec='k'))
    ax1.set_title("Pieza 1 (Columna)")
 
    # Pieza 2 (Yugo) - trapecio horizontal según 'c_mm' y 'w'
    l_yoke = c_mm + w
    yoke_shape = [[0, 0], [l_yoke, 0], [l_yoke + w, yoke_h], [-w, yoke_h]]
    ax2.add_patch(patches.Polygon(yoke_shape, closed=True, fc='w', ec='k'))
    ax2.set_title("Pieza 2 (Yugo)")
 
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