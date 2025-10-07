import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np # Necesario para los cálculos de límites

def draw(d, output_dir, step_index=0):
    """
    Dibuja el ensamble y las piezas de un núcleo monofásico con corte a 45 grados.
    Las piezas individuales se dibujan como trapecios isósceles, que es la forma correcta.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'lamination_monofasico_45deg_step_{step_index + 1}.png')

    fig = plt.figure(figsize=(10, 12))
    gs = fig.add_gridspec(3, 1, height_ratios=[4, 2, 2])
    
    ax_main = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[1, 0])
    ax2 = fig.add_subplot(gs[2, 0])
    
    # --- 1. CÁLCULO DE DIMENSIONES (MODIFICADO: REGLA CUMULATIVA) ---
    b_mm = getattr(d, 'b', 0.0) * 10.0  # Alto de la ventana en mm
    c_prima_mm = getattr(d, 'c_prima', getattr(d, 'c', 0.0)) * 10.0  # Ancho de ventana en mm
    
    # Listas por escalón (valores en cm)
    anchos_cm = getattr(d, 'anchos', [])
    espesores_cm = getattr(d, 'espesores', [])
    
    # Ancho de lámina del escalón actual (en mm)
    a_mm = anchos_cm[step_index] * 10.0 if len(anchos_cm) > step_index else 0.0

    # Inicializar bases menores que usarán la regla acumulativa
    base_menor_1, base_menor_2 = 0.0, 0.0

    if step_index == 0:
        # Escalón 1: usar dimensiones base
        base_menor_1 = b_mm
        base_menor_2 = c_prima_mm
    else:
        # Escalones > 1: sumar 2 * e (en mm) para todos los escalones interiores desde el 2do hasta el actual
        cumulative_e_mm = sum(espesores_cm[1:step_index + 1]) * 10.0 * 2.0
        base_menor_1 = b_mm + cumulative_e_mm
        base_menor_2 = c_prima_mm + cumulative_e_mm

    # Detectar overrides provenientes de calculation.py (_detalles_para_plot)
    override = getattr(d, '_detalles_para_plot', None)
    mapping = {}
    if override:
        for det in override:
            name = det.get('nombre', '')
            num = ''.join(ch for ch in str(name) if ch.isdigit())
            if num:
                mapping[num] = det.get('largo_cm', None)

    # --- 2. DIBUJO DEL ENSAMBLE (Formado por trapecios isósceles) ---
    yoke_bottom = [[0, 0], [c_prima_mm, 0], [c_prima_mm + a_mm, -a_mm], [-a_mm, -a_mm]]
    yoke_top    = [[0, b_mm], [-a_mm, b_mm + a_mm], [c_prima_mm + a_mm, b_mm + a_mm], [c_prima_mm, b_mm]]
    col_left    = [[0, 0], [-a_mm, -a_mm], [-a_mm, b_mm + a_mm], [0, b_mm]]
    col_right   = [[c_prima_mm, 0], [c_prima_mm, b_mm], [c_prima_mm + a_mm, b_mm + a_mm], [c_prima_mm + a_mm, -a_mm]]

    ax_main.add_patch(patches.Polygon(yoke_bottom, closed=True, fc='lightgrey', ec='k'))
    ax_main.add_patch(patches.Polygon(yoke_top, closed=True, fc='lightgrey', ec='k'))
    ax_main.add_patch(patches.Polygon(col_left, closed=True, fc='whitesmoke', ec='k'))
    ax_main.add_patch(patches.Polygon(col_right, closed=True, fc='whitesmoke', ec='k'))

    ax_main.text(-a_mm / 2, b_mm / 2, "1", ha='center', va='center', fontsize=20, weight='bold')
    ax_main.text(c_prima_mm + a_mm / 2, b_mm / 2, "1", ha='center', va='center', fontsize=20, weight='bold')
    ax_main.text(c_prima_mm / 2, b_mm + a_mm / 2, "2", ha='center', va='center', fontsize=20, weight='bold')
    ax_main.text(c_prima_mm / 2, -a_mm / 2, "2", ha='center', va='center', fontsize=20, weight='bold')
    
    ax_main.set_title(f"Ensamble Monofásico 45° - Escalón {step_index + 1}\nAncho lámina (a): {a_mm:.1f} mm")

    # --- INICIO: AÑADIR COTAS AL ENSAMBLE ---
    dim_offset = a_mm * 1.5 if a_mm != 0 else 10.0
    # Altura (b)
    ax_main.annotate('', xy=(-a_mm - dim_offset, 0), xytext=(-a_mm - dim_offset, b_mm), arrowprops=dict(arrowstyle='<->', ec='red'))
    ax_main.text(-a_mm - dim_offset * 1.2, b_mm / 2, f'Altura (b):\n{b_mm:.1f} mm', ha='right', va='center', color='red', fontsize=10, rotation=90)
    # Ancho (c')
    ax_main.annotate('', xy=(0, -a_mm - dim_offset), xytext=(c_prima_mm, -a_mm - dim_offset), arrowprops=dict(arrowstyle='<->', ec='blue'))
    ax_main.text(c_prima_mm / 2, -a_mm - dim_offset * 1.2, f'Ancho (c\\\'): {c_prima_mm:.1f} mm', ha='center', va='top', color='blue', fontsize=10)
    # Grosor (a_n)
    ax_main.annotate('', xy=(-a_mm, b_mm + a_mm + dim_offset), xytext=(0, b_mm + a_mm + dim_offset), arrowprops=dict(arrowstyle='<->', ec='green'))
    ax_main.text(-a_mm / 2, b_mm + a_mm + dim_offset * 1.2, f'Grosor (a{step_index}): {a_mm:.1f} mm', ha='center', va='bottom', color='green', fontsize=10)
    # --- FIN: AÑADIR COTAS ---

    ax_main.axis('equal')
    ax_main.axis('off')

    # --- 3. DIBUJO DE PIEZAS INDIVIDUALES COMO TRAPECIOS ISÓSCELES ---
    offset = a_mm * 0.6

    # --- Pieza 1 (Columna): Trapecio Isósceles ---
    # La altura del trapecio es el ancho de la lámina 'a'
    altura_1 = a_mm
    # La base menor es el alto de la ventana 'b'
    base_menor_1 = (float(mapping.get('1')) * 10.0) if mapping.get('1') is not None else b_mm
    # La base mayor de un trapecio isósceles con cortes a 45° es base_menor + 2*altura
    base_mayor_1 = base_menor_1 + 2 * altura_1
    
    # Vértices para dibujar el trapecio "acostado"
    col_shape = [[0, altura_1], [altura_1, 0], [altura_1 + base_menor_1, 0], [base_menor_1 + 2*altura_1, altura_1]]
    ax1.add_patch(patches.Polygon(col_shape, closed=True, fc='whitesmoke', ec='k'))
    ax1.set_title(f"Pieza 1 (Columna)")
    ax1.text((base_mayor_1 + base_menor_1)/2 / 2 + altura_1/2, altura_1/2, '1', ha='center', va='center', fontsize=14)
    
    # Dimensiones
    ax1.annotate('', xy=(altura_1, -offset), xytext=(altura_1 + base_menor_1, -offset), arrowprops=dict(arrowstyle='<->', ec='blue'))
    ax1.text(altura_1 + base_menor_1/2, -offset, f'Base Menor: {base_menor_1:.1f}', ha='center', va='top', color='blue', fontsize=9)
    ax1.annotate('', xy=(0, altura_1 + offset), xytext=(base_mayor_1, altura_1 + offset), arrowprops=dict(arrowstyle='<->', ec='red'))
    ax1.text(base_mayor_1/2, altura_1 + offset, f'Base Mayor: {base_mayor_1:.1f}', ha='center', va='bottom', color='red', fontsize=9)
    ax1.annotate('', xy=(-offset, 0), xytext=(-offset, altura_1), arrowprops=dict(arrowstyle='<->', ec='green'))
    ax1.text(-offset, altura_1/2, f'Altura:\n{altura_1:.1f}', ha='right', va='center', color='green', fontsize=9)
 
    # --- Pieza 2 (Yugo): Trapecio Isósceles ---
    altura_2 = a_mm
    base_menor_2 = (float(mapping.get('2')) * 10.0) if mapping.get('2') is not None else c_prima_mm
    base_mayor_2 = base_menor_2 + 2 * altura_2
    
    # Vértices para dibujar el trapecio
    yoke_shape = [[0, altura_2], [altura_2, 0], [altura_2 + base_menor_2, 0], [base_menor_2 + 2*altura_2, altura_2]]
    ax2.add_patch(patches.Polygon(yoke_shape, closed=True, fc='lightgrey', ec='k'))
    ax2.set_title("Pieza 2 (Yugo)")
    ax2.text((base_mayor_2 + base_menor_2)/2 / 2 + altura_2/2, altura_2/2, '2', ha='center', va='center', fontsize=14)

    # Dimensiones
    ax2.annotate('', xy=(altura_2, -offset), xytext=(altura_2 + base_menor_2, -offset), arrowprops=dict(arrowstyle='<->', ec='blue'))
    ax2.text(altura_2 + base_menor_2/2, -offset, f'Base Menor: {base_menor_2:.1f}', ha='center', va='top', color='blue', fontsize=9)
    ax2.annotate('', xy=(0, altura_2 + offset), xytext=(base_mayor_2, altura_2 + offset), arrowprops=dict(arrowstyle='<->', ec='red'))
    ax2.text(base_mayor_2/2, altura_2 + offset, f'Base Mayor: {base_mayor_2:.1f}', ha='center', va='bottom', color='red', fontsize=9)
    ax2.annotate('', xy=(-offset, 0), xytext=(-offset, altura_2), arrowprops=dict(arrowstyle='<->', ec='green'))
    ax2.text(-offset, altura_2/2, f'Altura:\n{altura_2:.1f}', ha='right', va='center', color='green', fontsize=9)

    # --- CORRECCIÓN DE ESCALA ---
    ax1.autoscale_view()
    ax2.autoscale_view()
    xlim1, ylim1 = ax1.get_xlim(), ax1.get_ylim()
    xlim2, ylim2 = ax2.get_xlim(), ax2.get_ylim()
    max_range = max(xlim1[1] - xlim1[0], ylim1[1] - ylim1[0], xlim2[1] - xlim2[0], ylim2[1] - ylim2[0])

    def set_equal_scale(ax, xlim, ylim, max_range):
        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2
        ax.set_xlim(x_center - max_range / 2, x_center + max_range / 2)
        ax.set_ylim(y_center - max_range / 2, y_center + max_range / 2)
        ax.axis('equal')
        ax.axis('off')

    set_equal_scale(ax1, xlim1, ylim1, max_range)
    set_equal_scale(ax2, xlim2, ylim2, max_range)
    
    plt.tight_layout(pad=2.0)
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    return os.path.abspath(output_path)

# --- INICIO: Ejemplo de uso y Mock de datos ---
if __name__ == '__main__':
    class MockDimensions:
        def __init__(self):
            # Dimensiones de la ventana en cm
            self.b = 24.4
            self.c_prima = 17.78
            # Ancho de la lámina en cm
            self.anchos = [5.0]
            self.g = 5.0 # Fallback en cm
            self._detalles_para_plot = None

    d_simulado = MockDimensions()
    output_directory = 'output_test'
    ruta_imagen = draw(d_simulado, output_dir=output_directory, step_index=0)
    print(f"Imagen de prueba para 'monofasico_45deg' guardada en: {ruta_imagen}")
# --- FIN: Ejemplo de uso y Mock de datos ---