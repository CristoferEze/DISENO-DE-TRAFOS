# src/design_phases/nucleus_and_window/lamination_plotters/trifasico_recto_ajustado.py
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def draw(d, output_dir, step_index=0):
    """
    Dibuja el ensamble y las piezas de un núcleo trifásico.
    Utiliza un diccionario centralizado para las dimensiones de las piezas,
    asegurando consistencia entre el ensamble y las vistas individuales.
    Las dimensiones se ajustan para el escalón específico (step_index).
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, f'lamination_plot_step_{step_index + 1}_ajustado.png')

    fig = plt.figure(figsize=(8, 10))
    gs = fig.add_gridspec(4, 2, height_ratios=[4, 1, 1, 1], width_ratios=[1,1])
    
    ax_main = fig.add_subplot(gs[0, :]) # Ensamble principal
    ax1 = fig.add_subplot(gs[1, :])     # Pieza 1
    ax2 = fig.add_subplot(gs[2, :])     # Pieza 2
    ax3 = fig.add_subplot(gs[3, :])     # Pieza 3
    
    # --- 1. CÁLCULO CENTRALIZADO DE DIMENSIONES (MODIFICADO: REGLA CUMULATIVA) ---
    # Dimensiones base en mm
    b_mm = getattr(d, 'b', 0.0) * 10.0  # Alto de la ventana
    c_mm = getattr(d, 'c', 0.0) * 10.0  # Ancho de la ventana

    # Listas por escalón (valores en cm)
    anchos_cm = getattr(d, 'anchos', [])
    espesores_cm = getattr(d, 'espesores', [])

    # Ancho/grosor de la laminación para el escalón actual (mm)
    lamination_width_mm = anchos_cm[step_index] * 10.0 if len(anchos_cm) > step_index else (getattr(d, 'g', 0.0) * 10.0)

    # Detectar overrides provenientes de calculation.py (_detalles_para_plot)
    override = getattr(d, '_detalles_para_plot', None)
    mapping = {}
    if override:
        for det in override:
            name = det.get('nombre', '')
            m = re.search(r'(\d+)', str(name))
            if m:
                mapping[m.group(1)] = det.get('largo_cm', None)

    # Calcular largos según regla acumulativa
    largo_1, largo_2, largo_3 = 0.0, 0.0, 0.0
    if step_index == 0:
        # Escalón 1: usa su propio ancho 'a0'
        a0_mm = lamination_width_mm
        largo_1 = b_mm + a0_mm
        largo_2 = c_mm + a0_mm
        largo_3 = (2 * c_mm) + a0_mm
    else:
        # Escalones > 1: sumar 2 * e (en mm) para todos los escalones interiores desde el 2° hasta el actual
        cumulative_e_mm = sum(espesores_cm[1:step_index + 1]) * 10.0 * 2.0
        largo_1 = b_mm + cumulative_e_mm
        largo_2 = c_mm + cumulative_e_mm
        largo_3 = (2 * c_mm) + cumulative_e_mm

    # Construir dictionary de dimensiones usando los largos calculados o los overrides
    piece_dims = {
        '1': {
            'width': lamination_width_mm,
            'height': (float(mapping.get('1')) * 10.0) if mapping.get('1') is not None else largo_1
        },
        '2': {
            'width': (float(mapping.get('2')) * 10.0) if mapping.get('2') is not None else largo_2,
            'height': lamination_width_mm
        },
        '3': {
            'width': (float(mapping.get('3')) * 10.0) if mapping.get('3') is not None else largo_3,
            'height': lamination_width_mm
        }
    }

    # --- ENFOQUE ACTUALIZADO: Usar valores calculados o valores por defecto ---
    # Solo sobreescribir el diccionario si no se definió arriba con overrides
    if not mapping:
        piece_dims = {
            '1': {
                # Pieza 1 (Columna): Su ancho es el de la lámina, su alto es la ventana + yugo.
                'width': lamination_width_mm,
                'height': b_mm + lamination_width_mm
            },
            '2': {
                # Pieza 2 (Yugo Corto): Su alto es el de la lámina, su largo es la ventana + columna.
                'width': c_mm + lamination_width_mm,
                'height': lamination_width_mm
            },
            '3': {
                # Pieza 3 (Yugo Largo): Su alto es el de la lámina, su largo es 2 ventanas + columna.
                'width': (2 * c_mm) + lamination_width_mm,
                'height': lamination_width_mm
            }
        }

    # --- 2. DIBUJO DEL ENSAMBLE (usando el diccionario 'piece_dims') ---
    
    # Pieza 2 (yugo inferior izquierdo)
    ax_main.add_patch(patches.Rectangle((0, 0), piece_dims['2']['width'], piece_dims['2']['height'], fc='w', ec='k'))
    ax_main.text(piece_dims['2']['width']/2, piece_dims['2']['height']/2, '2', ha='center', va='center', fontsize=20)
    
    # Columna izquierda (Pieza 1) - usar las dimensiones completas de piece_dims['1']
    # Base en y = altura del yugo inferior (piece_dims['2']['height'])
    ax_main.add_patch(patches.Rectangle((0, piece_dims['2']['height']), piece_dims['1']['width'], piece_dims['1']['height'], fc='w', ec='k'))
    ax_main.text(piece_dims['1']['width']/2, piece_dims['2']['height'] + piece_dims['1']['height']/2, '1', ha='center', va='center', fontsize=20)
    
    # Columna central (Pieza 1) - usar mismas dimensiones y base en y = altura del yugo inferior
    x_col_central = piece_dims['2']['width']
    ax_main.add_patch(patches.Rectangle((x_col_central, 0), piece_dims['1']['width'], piece_dims['1']['height'], fc='w', ec='k'))
    ax_main.text(x_col_central + piece_dims['1']['width']/2, piece_dims['2']['height'] + piece_dims['1']['height']/2, '1', ha='center', va='center', fontsize=20)
    
    # Pieza 2 (yugo inferior derecho)
    x_yugo_der = x_col_central + piece_dims['1']['width']
    ax_main.add_patch(patches.Rectangle((x_yugo_der, 0), piece_dims['2']['width'], piece_dims['2']['height'], fc='w', ec='k'))
    ax_main.text(x_yugo_der + piece_dims['2']['width']/2, piece_dims['2']['height']/2, '2', ha='center', va='center', fontsize=20)
 
    # Columna derecha (Pieza 1) - posicionada en x = 2 * largo de la pieza 2 (2 * l2)
    x_col_der = 2 * piece_dims['2']['width']
    ax_main.add_patch(patches.Rectangle((x_col_der, piece_dims['2']['height']), piece_dims['1']['width'], piece_dims['1']['height'], fc='w', ec='k'))
    ax_main.text(x_col_der + piece_dims['1']['width']/2, piece_dims['2']['height'] + piece_dims['1']['height']/2, '1', ha='center', va='center', fontsize=20)

    # Pieza 3 (yugo superior) - colocar sobre la parte superior de las columnas (altura base + altura columna)
    x_yugo_sup = piece_dims['1']['width']
    y_yugo_sup = piece_dims['2']['height'] + piece_dims['1']['height']
    ax_main.add_patch(patches.Rectangle((x_yugo_sup, y_yugo_sup-piece_dims['3']['height']), piece_dims['3']['width'], piece_dims['3']['height'], fc='w', ec='k'))
    ax_main.text(x_yugo_sup + piece_dims['3']['width']/2, y_yugo_sup- piece_dims['3']['height']/2, '3', ha='center', va='center', fontsize=20)

    ax_main.set_title(f"Dimensionado de Laminación - Escalón {step_index + 1}\nAncho de Lámina: {lamination_width_mm:.1f} mm")

    # --- INICIO: AÑADIR COTAS AL ENSAMBLE ---
    dim_offset = lamination_width_mm * 1.5 if lamination_width_mm != 0 else 10.0
    # Altura (b)
    y_start = piece_dims['2']['height']
    ax_main.annotate('', xy=(-dim_offset, y_start), xytext=(-dim_offset, y_start + b_mm), arrowprops=dict(arrowstyle='<->', ec='red'))
    ax_main.text(-dim_offset * 1.2, y_start + b_mm / 2, f'Altura (b):\n{b_mm:.1f} mm', ha='right', va='center', color='red', fontsize=10, rotation=90)
    # Ancho (c)
    x_start = piece_dims['1']['width']
    ax_main.annotate('', xy=(x_start, -dim_offset), xytext=(x_start + c_mm, -dim_offset), arrowprops=dict(arrowstyle='<->', ec='blue'))
    ax_main.text(x_start + c_mm / 2, -dim_offset * 1.2, f'Ancho (c): {c_mm:.1f} mm', ha='center', va='top', color='blue', fontsize=10)
    # Grosor (a_n)
    y_top = y_yugo_sup
    ax_main.annotate('', xy=(0, y_top + dim_offset), xytext=(lamination_width_mm, y_top + dim_offset), arrowprops=dict(arrowstyle='<->', ec='green'))
    ax_main.text(lamination_width_mm / 2, y_top + dim_offset * 1.2, f'Grosor (a{step_index}): {lamination_width_mm:.1f} mm', ha='center', va='bottom', color='green', fontsize=10)
    # --- FIN: AÑADIR COTAS ---

    # --- 3. DIBUJO DE PIEZAS INDIVIDUALES (usando el mismo diccionario 'piece_dims') ---
    for ax in [ax1, ax2, ax3]:
        ax.axis('off')
        
    # Pieza 1: Se muestra la pieza más alta para referencia. Se dibuja en horizontal.
    ax1.set_title("Pieza 1 (Columna)")
    ax1.add_patch(patches.Rectangle((0, 0), piece_dims['1']['height'], piece_dims['1']['width'], fc='w', ec='k'))
    ax1.text(piece_dims['1']['height']/2, piece_dims['1']['width']/2, '1', ha='center', va='center', fontsize=12)
    ax1.text(piece_dims['1']['height']/2, -piece_dims['1']['width']*0.4, f"{piece_dims['1']['height']:.1f} mm", ha='center', va='top')
    ax1.text(-5, piece_dims['1']['width']/2, f"{piece_dims['1']['width']:.1f} mm", ha='right', va='center')

    # Pieza 2
    ax2.set_title("Pieza 2 (Yugo Corto)")
    ax2.add_patch(patches.Rectangle((0, 0), piece_dims['2']['width'], piece_dims['2']['height'], fc='w', ec='k'))
    ax2.text(piece_dims['2']['width']/2, piece_dims['2']['height']/2, '2', ha='center', va='center', fontsize=12)
    ax2.text(piece_dims['2']['width']/2, -piece_dims['2']['height']*0.4, f"{piece_dims['2']['width']:.1f} mm", ha='center', va='top')
    ax2.text(-5, piece_dims['2']['height']/2, f"{piece_dims['2']['height']:.1f} mm", ha='right', va='center')

    # Pieza 3
    ax3.set_title("Pieza 3 (Yugo Largo)")
    ax3.add_patch(patches.Rectangle((0, 0), piece_dims['3']['width'], piece_dims['3']['height'], fc='w', ec='k'))
    ax3.text(piece_dims['3']['width']/2, piece_dims['3']['height']/2, '3', ha='center', va='center', fontsize=12)
    ax3.text(piece_dims['3']['width']/2, -piece_dims['3']['height']*0.4, f"{piece_dims['3']['width']:.1f} mm", ha='center', va='top')
    ax3.text(-5, piece_dims['3']['height']/2, f"{piece_dims['3']['height']:.1f} mm", ha='right', va='center')

    for ax in [ax_main, ax1, ax2, ax3]:
        ax.axis('equal')
        ax.axis('off')
    
    plt.tight_layout(pad=1.5)
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    return os.path.abspath(output_path)
    
    
# --- INICIO: Ejemplo de uso y Mock de datos para 'trifasico_recto' ---
if __name__ == '__main__':
    class MockDimensions:
        def __init__(self):
            # Dimensiones de la ventana en cm
            self.b = 30.0
            self.c = 15.0
            self.c_prima = 15.0
            # Anchos de lámina por escalón (cm)
            self.anchos = [6.0]
            # Espesores por escalón (cm) — usados por la regla acumulativa
            self.espesores = [0.5, 0.5]
            # Valor por defecto de grosor si no hay 'anchos' definido
            self.g = 6.0
            self._detalles_para_plot = None

    d_simulado = MockDimensions()
    output_directory = 'output_test'
    ruta_imagen = draw(d_simulado, output_dir=output_directory, step_index=0)
    print(f"Imagen de prueba para 'trifasico_recto' guardada en: {ruta_imagen}")
# --- FIN: Ejemplo de uso y Mock de datos ---