import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def draw(d, output_dir, step_index=0):
    """
    Dibuja el ensamble y las piezas de un núcleo monofásico con corte recto.
    CORREGIDO: Implementa un modelo de ensamble con esquinas superpuestas,
    según las especificaciones del usuario.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'lamination_plot_step_{step_index + 1}.png')

    fig = plt.figure(figsize=(9, 9)) # Aumentado para mejor visualización de cotas
    gs = fig.add_gridspec(3, 1, height_ratios=[4, 1, 1])

    ax_main = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[1, 0])
    ax2 = fig.add_subplot(gs[2, 0])

    # --- INICIO DE LA CORRECCIÓN: LÓGICA DE ENSAMBLE SUPERPUESTO ---
    b_mm = getattr(d, 'b', 0.0) * 10.0
    # Usamos c_prima para el ancho de la ventana
    c_prima_mm = getattr(d, 'c_prima', getattr(d, 'c', 0.0)) * 10.0

    anchos_cm = getattr(d, 'anchos', [])
    grosor_mm = anchos_cm[step_index] * 10.0 if len(anchos_cm) > step_index else 0.0

    # 1. Dimensiones de las piezas (según la definición del usuario)
    piece_dims = {
        '1': { # Pieza 1 (Vertical)
            'width': grosor_mm,
            'height': b_mm + grosor_mm
        },
        '2': { # Pieza 2 (Horizontal)
            'width': c_prima_mm + grosor_mm,
            'height': grosor_mm
        }
    }

    # --- 2. DIBUJO DEL ENSAMBLE CON SUPERPOSICIÓN EN ESQUINAS ---
    ax_main.set_title(f"Monofásico Recto (Superpuesto) - Escalón {step_index + 1}")

    # Pieza 2 (Yugo Inferior) - Base en (0,0)
    p2_bottom = patches.Rectangle((grosor_mm, 0), piece_dims['2']['width'], piece_dims['2']['height'], fc='lightblue', ec='k', alpha=0.8)
    ax_main.add_patch(p2_bottom)
    ax_main.text(piece_dims['2']['width'] / 2, piece_dims['2']['height'] / 2, '2', ha='center', va='center', fontsize=18)

    # Pieza 1 (Columna Izquierda) - Encima de la base en (0,0)
    p1_left = patches.Rectangle((0, 0), piece_dims['1']['width'], piece_dims['1']['height'], fc='lightcoral', ec='k', alpha=0.8)
    ax_main.add_patch(p1_left)
    ax_main.text(piece_dims['1']['width'] / 2, piece_dims['1']['height'] / 2, '1', ha='center', va='center', fontsize=18)

    # Pieza 1 (Columna Derecha) - Posición específica: (c'+grosor, grosor)
    x_col_der = c_prima_mm + grosor_mm
    y_col_der = grosor_mm
    p1_right = patches.Rectangle((x_col_der, y_col_der), piece_dims['1']['width'], piece_dims['1']['height'], fc='lightcoral', ec='k', alpha=0.8)
    ax_main.add_patch(p1_right)
    ax_main.text(x_col_der + piece_dims['1']['width'] / 2, y_col_der + piece_dims['1']['height'] / 2, '1', ha='center', va='center', fontsize=18)

    # Pieza 2 (Yugo Superior) - Encima de la columna izquierda
    x_yugo_sup = 0
    y_yugo_sup = b_mm + grosor_mm
    p2_top = patches.Rectangle((x_yugo_sup, y_yugo_sup), piece_dims['2']['width'], piece_dims['2']['height'], fc='lightblue', ec='k', alpha=0.8)
    ax_main.add_patch(p2_top)
    ax_main.text(x_yugo_sup + piece_dims['2']['width'] / 2, y_yugo_sup + piece_dims['2']['height'] / 2, '2', ha='center', va='center', fontsize=18)


    # --- 3. AÑADIR COTAS AL ENSAMBLE SUPERPUESTO ---
    dim_offset = grosor_mm * 2.0 if grosor_mm != 0 else 10.0
    # Altura interna de la ventana (b)
    y_start_b = grosor_mm
    y_end_b = b_mm + grosor_mm
    ax_main.annotate('', xy=(-dim_offset, y_start_b), xytext=(-dim_offset, y_end_b), arrowprops=dict(arrowstyle='<->', ec='red'))
    ax_main.text(-dim_offset * 1.2, y_start_b + b_mm / 2, f'Altura (b):\n{b_mm:.1f} mm', ha='right', va='center', color='red', fontsize=10, rotation=90)
    # Ancho interno de la ventana (c')
    x_start_c = grosor_mm
    x_end_c = c_prima_mm + grosor_mm
    ax_main.annotate('', xy=(x_start_c, -dim_offset), xytext=(x_end_c, -dim_offset), arrowprops=dict(arrowstyle='<->', ec='blue'))
    ax_main.text(x_start_c + c_prima_mm / 2, -dim_offset * 1.2, f'Ancho (c\'): {c_prima_mm:.1f} mm', ha='center', va='top', color='blue', fontsize=10)
    # Grosor (a_n)
    y_top = y_yugo_sup + grosor_mm
    ax_main.annotate('', xy=(0, y_top + dim_offset), xytext=(grosor_mm, y_top + dim_offset), arrowprops=dict(arrowstyle='<->', ec='green'))
    ax_main.text(grosor_mm / 2, y_top + dim_offset * 0.8, f'Grosor (a{step_index}): {grosor_mm:.1f} mm', ha='center', va='bottom', color='green', fontsize=10)
    # --- FIN DE LA CORRECCIÓN ---

    # --- DIBUJO DE PIEZAS INDIVIDUALES ---
    ax1.set_title("Pieza 1 (Vertical)")
    ax1.add_patch(patches.Rectangle((0, 0), piece_dims['1']['height'], piece_dims['1']['width'], fc='lightcoral', ec='k'))
    ax1.text(piece_dims['1']['height'] / 2, piece_dims['1']['width'] / 2, '1', ha='center', va='center', fontsize=12)
    ax1.text(piece_dims['1']['height'] / 2, -piece_dims['1']['width'] * 0.5, f"Largo (b + grosor): {piece_dims['1']['height']:.1f} mm", ha='center', va='top', fontsize=10)
    ax1.text(-5, piece_dims['1']['width'] / 2, f"Ancho\n(grosor):\n{piece_dims['1']['width']:.1f} mm", ha='right', va='center', fontsize=9)

    ax2.set_title("Pieza 2 (Horizontal)")
    ax2.add_patch(patches.Rectangle((0, 0), piece_dims['2']['width'], piece_dims['2']['height'], fc='lightblue', ec='k'))
    ax2.text(piece_dims['2']['width'] / 2, piece_dims['2']['height'] / 2, '2', ha='center', va='center', fontsize=12)
    ax2.text(piece_dims['2']['width'] / 2, -piece_dims['2']['height'] * 0.5, f"Largo (c' + grosor): {piece_dims['2']['width']:.1f} mm", ha='center', va='top', fontsize=10)
    ax2.text(-5, piece_dims['2']['height'] / 2, f"Ancho\n(grosor):\n{piece_dims['2']['height']:.1f} mm", ha='right', va='center', fontsize=9)

    for ax in [ax_main, ax1, ax2]:
        ax.axis('equal')
        ax.axis('off')

    plt.tight_layout(pad=2.0)
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    return os.path.abspath(output_path)

# --- INICIO: Ejemplo de uso y Mock de datos ---
if __name__ == '__main__':
    class MockDimensions:
        def __init__(self):
            self.b = 20.0       # cm (Altura interna de la ventana)
            self.c_prima = 15.0 # cm (Ancho interno de la ventana)
            self.anchos = [4.0] # cm (Grosor de la laminación para este escalón)
            # --- Variables no usadas en este dibujo pero se incluyen por completitud ---
            self.c = 15.0
            self.espesores = []
            self.g = 4.0
            self._detalles_para_plot = None

    d_simulado = MockDimensions()
    output_directory = 'output_test_superpuesto'
    ruta_imagen = draw(d_simulado, output_dir=output_directory, step_index=0)
    print(f"Imagen de prueba corregida para ensamble 'superpuesto' guardada en: {ruta_imagen}")
# --- FIN: Ejemplo de uso y Mock de datos ---