import os
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def draw(d, output_dir='temp', step_index=0):
    """
    Dibuja el ensamble y las piezas de un núcleo trifásico diagonal con geometrías específicas
    y calcula el área de cada pieza. El ensamble muestra yugos superior e inferior como piezas únicas.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'lamination_trifasico_45deg_step_{step_index + 1}.png')

    fig = plt.figure(figsize=(12, 14))
    gs = fig.add_gridspec(4, 1, height_ratios=[4, 2, 2, 2])
    ax_main = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[1, 0])
    ax2 = fig.add_subplot(gs[2, 0])
    ax3 = fig.add_subplot(gs[3, 0])

    # --- INICIO DE LA MODIFICACIÓN: USAR DIMENSIONES PRE-CALCULADAS POR ESCALÓN ---
    # Usar las dimensiones actualizadas ya calculadas en nucleus_and_window/calculation.py
    if hasattr(d, 'b_por_escalon') and hasattr(d, 'c_prima_por_escalon'):
        # Usar dimensiones pre-calculadas por escalón
        b_mm = (d.b_por_escalon[step_index] if step_index < len(d.b_por_escalon) else d.b) * 10.0
        c_prima_mm = (d.c_prima_por_escalon[step_index] if step_index < len(d.c_prima_por_escalon) else getattr(d, 'c_prima', d.c)) * 10.0
    else:
        # Fallback: usar dimensiones base y aplicar regla acumulativa manualmente
        b_mm = getattr(d, 'b', 0.0) * 10.0
        c_prima_mm = getattr(d, 'c_prima', getattr(d, 'c', 0.0)) * 10.0
        
        anchos_cm = getattr(d, 'anchos', [])
        espesores_cm = getattr(d, 'espesores', [])
        
        if step_index > 0:
            cumulative_e_mm = sum(espesores_cm[1:step_index + 1]) * 10.0 * 2.0
            b_mm += cumulative_e_mm
            c_prima_mm += cumulative_e_mm

    anchos_cm = getattr(d, 'anchos', [])
    a = anchos_cm[step_index] * 10.0 if len(anchos_cm) > step_index else 0.0
    
    # Calcular las bases usando las dimensiones ya actualizadas
    base_menor_1 = b_mm
    base_menor_2 = 2 * c_prima_mm + (anchos_cm[0] * 10.0 if anchos_cm else 0.0)
    largo_rect_3 = b_mm
    # --- FIN DE LA MODIFICACIÓN ---

    # --- 1.b. Detectar overrides provenientes de calculation.py (_detalles_para_plot)
    override = getattr(d, '_detalles_para_plot', None)
    mapping = {}
    if override:
        for det in override:
            name = det.get('nombre', '')
            m = re.search(r'(\d+)', str(name))
            if m:
                try:
                    val = det.get('largo_cm', None)
                    if val is not None:
                        mapping[m.group(1)] = float(val) * 10.0  # mm
                except Exception:
                    # ignorar valores no numéricos
                    pass

    # --- 2. DIBUJO DEL ENSAMBLE REALISTA Y CORREGIDO ---
    # Columnas (Piezas 1 y 3)
    col_left = [[-a, -a], [0, 0], [0, b_mm], [-a, b_mm + a]]
    x_offset_col_center = c_prima_mm
    col_center = [[x + x_offset_col_center, y] for x, y in [[0, 0], [a/2, -a/2], [a, 0], [a, b_mm], [a/2, b_mm+a/2], [0, b_mm]]]
    x_offset_col_right = c_prima_mm + a + c_prima_mm
    col_right = [[x + x_offset_col_right, y] for x, y in [[0, 0], [a, -a], [a, b_mm+a], [0, b_mm]]]
    
    # Yugos superior e inferior como PIEZAS ÚNICAS (Pieza 2)
    yoke_bottom = [
        [-a, -a],                                       # Esquina inf-izq exterior
        [x_offset_col_right + a, -a],                   # Esquina inf-der exterior
        [x_offset_col_right, 0],                        # Esquina inf-der interior
        [x_offset_col_center + a, 0],                   # Lado derecho de la muesca
        [x_offset_col_center + a/2, -a/2],              # Punta de la muesca (encaja con col_center)
        [x_offset_col_center, 0],                       # Lado izquierdo de la muesca
        [0, 0],                                         # Esquina inf-izq interior
    ]
    yoke_top = [
        [-a, b_mm + a],                                 # Esquina sup-izq exterior
        [x_offset_col_right + a, b_mm + a],             # Esquina sup-der exterior
        [x_offset_col_right, b_mm],                     # Esquina sup-der interior
        [x_offset_col_center + a, b_mm],                # Lado derecho de la muesca
        [x_offset_col_center + a/2, b_mm + a/2],        # Punta de la muesca (encaja con col_center)
        [x_offset_col_center, b_mm],                    # Lado izquierdo de la muesca
        [0, b_mm],                                      # Esquina sup-izq interior
    ]

    # Añadir polígonos al ensamble
    ax_main.add_patch(patches.Polygon(col_left, closed=True, fc='#FFDDC1', ec='k'))
    ax_main.add_patch(patches.Polygon(col_right, closed=True, fc='#FFDDC1', ec='k'))
    ax_main.add_patch(patches.Polygon(col_center, closed=True, fc='#C1FFD7', ec='k'))
    ax_main.add_patch(patches.Polygon(yoke_bottom, closed=True, fc='#D7E3FF', ec='k'))
    ax_main.add_patch(patches.Polygon(yoke_top, closed=True, fc='#D7E3FF', ec='k'))
    
    # Etiquetas del ensamble corregidas
    ax_main.text(-a/2, b_mm/2, '1', ha='center', va='center', fontsize=16, weight='bold')
    ax_main.text(x_offset_col_right, b_mm/2, '1', ha='center', va='center', fontsize=16, weight='bold')
    ax_main.text(c_prima_mm + a/2, b_mm/2, '3', ha='center', va='center', fontsize=16, weight='bold')
    ax_main.text(c_prima_mm + a/2, -a*0.8, '2', ha='center', va='center', fontsize=16, weight='bold')
    ax_main.text(c_prima_mm + a/2, b_mm + a*0.8, '2', ha='center', va='center', fontsize=16, weight='bold')
    ax_main.set_title(f"Ensamble Trifásico 45° - Escalón {step_index + 1}\nAncho de Lámina (a): {a:.1f} mm")

    # --- INICIO: AÑADIR COTAS AL ENSAMBLE ---
    dim_offset = a * 1.5 if a != 0 else 10.0
    # Altura (b)
    ax_main.annotate('', xy=(-a - dim_offset, 0), xytext=(-a - dim_offset, b_mm), arrowprops=dict(arrowstyle='<->', ec='red'))
    ax_main.text(-a - dim_offset * 1.2, b_mm / 2, f'Altura (b):\n{b_mm:.1f} mm', ha='right', va='center', color='red', fontsize=10, rotation=90)
    # Ancho (c')
    ax_main.annotate('', xy=(0, -a - dim_offset), xytext=(c_prima_mm, -a - dim_offset), arrowprops=dict(arrowstyle='<->', ec='blue'))
    ax_main.text(c_prima_mm / 2, -a - dim_offset * 1.2, f'Ancho (c\\\'): {c_prima_mm:.1f} mm', ha='center', va='top', color='blue', fontsize=10)
    # Grosor (a_n)
    ax_main.annotate('', xy=(-a, b_mm + a + dim_offset), xytext=(0, b_mm + a + dim_offset), arrowprops=dict(arrowstyle='<->', ec='green'))
    ax_main.text(-a / 2, b_mm + a + dim_offset * 1.2, f'Grosor (a{step_index}): {a:.1f} mm', ha='center', va='bottom', color='green', fontsize=10)
    # --- FIN: AÑADIR COTAS ---

    # --- 3. CÁLCULO DE ÁREAS Y DIBUJO DE PIEZAS INDIVIDUALES (Sin cambios) ---
    offset = a * 0.6

    # --- Pieza 1: Trapecio ---
    # Dimensiones del trapecio 1 (usar base_menor_1 calculada previamente)
    altura_1 = a
    base_mayor_1 = base_menor_1 + 2 * a
    
    # Dibujo de la pieza 1 y sus dimensiones
    p1_shape = [[0, 0], [base_mayor_1, 0], [base_menor_1 + a, altura_1], [a, altura_1]]
    ax1.add_patch(patches.Polygon(p1_shape, closed=True, fc='#FFDDC1', ec='k'))
    ax1.text(base_mayor_1/2, altura_1/2, '1', ha='center', va='center', fontsize=14)
    # Cotas mejoradas con flechas para Pieza 1
    ax1.annotate('', xy=(0, -offset), xytext=(base_mayor_1, -offset), arrowprops=dict(arrowstyle='<->', ec='blue'))
    ax1.text(base_mayor_1/2, -offset*1.5, f'Base Mayor: {base_mayor_1:.1f} mm', ha='center', va='top', color='blue', fontsize=9)
    ax1.annotate('', xy=(a, altura_1 + offset), xytext=(base_menor_1 + a, altura_1 + offset), arrowprops=dict(arrowstyle='<->', ec='red'))
    ax1.text(base_mayor_1/2, altura_1 + offset*1.5, f'Base Menor: {base_menor_1:.1f} mm', ha='center', va='bottom', color='red', fontsize=9)
    ax1.annotate('', xy=(-offset*2, 0), xytext=(-offset*2, altura_1), arrowprops=dict(arrowstyle='<->', ec='green'))
    ax1.text(-offset*2.5, altura_1/2, f'Altura:\n{altura_1:.1f} mm', ha='right', va='center', color='green', fontsize=9)
    # Mostrar largo calculado (override) cuando exista, si no usar la base mayor como referencia
    l1_mm = mapping.get('1', base_mayor_1)
    ax1.set_title(f"Pieza 1 (Trapecio) — Largo mostrado: {l1_mm:.1f} mm")
    
    # --- Pieza 2: Trapecio con corte ---
    # Dimensiones del trapecio 2 (usar base_menor_2 calculada previamente)
    altura_2 = a
    base_mayor_2 = base_menor_2 + 2 * a
    
    # Dibujo de la pieza 2 y sus dimensiones
    p2_shape = [[0, 0], [base_mayor_2, 0], [base_menor_2 + a, altura_2], [a, altura_2]]
    ax2.add_patch(patches.Polygon(p2_shape, closed=True, fc='#D7E3FF', ec='k'))
    corte_centro_x = base_mayor_2 / 2
    corte_shape = [[corte_centro_x - a/2, altura_2], [corte_centro_x + a/2, altura_2], [corte_centro_x, altura_2 - a/2]]
    ax2.add_patch(patches.Polygon(corte_shape, closed=True, fc='white', ec='red'))
    ax2.text(base_mayor_2/2, altura_2/3, '2', ha='center', va='center', fontsize=14)
    # Cotas mejoradas con flechas para Pieza 2
    ax2.annotate('', xy=(0, -offset), xytext=(base_mayor_2, -offset), arrowprops=dict(arrowstyle='<->', ec='blue'))
    ax2.text(base_mayor_2/2, -offset*1.5, f'Base Mayor: {base_mayor_2:.1f} mm', ha='center', va='top', color='blue', fontsize=9)
    ax2.annotate('', xy=(a, altura_2 + offset), xytext=(base_menor_2 + a, altura_2 + offset), arrowprops=dict(arrowstyle='<->', ec='red'))
    ax2.text(base_mayor_2/2, altura_2 + offset*1.5, f'Base Menor: {base_menor_2:.1f} mm', ha='center', va='bottom', color='red', fontsize=9)
    ax2.annotate('', xy=(-offset*2, 0), xytext=(-offset*2, altura_2), arrowprops=dict(arrowstyle='<->', ec='green'))
    ax2.text(-offset*2.5, altura_2/2, f'Altura:\n{altura_2:.1f} mm', ha='right', va='center', color='green', fontsize=9)
    # Mostrar largo calculado (override) cuando exista, si no usar la base mayor como referencia
    l2_mm = mapping.get('2', base_mayor_2)
    ax2.set_title(f"Pieza 2 (Yugo - con corte) — Largo mostrado: {l2_mm:.1f} mm")

    # --- Pieza 3: Rectángulo + 2 Triángulos ---
    rect_ancho_3, rect_largo_3 = a, largo_rect_3
    tri_base_3, tri_altura_3 = a, a / 2.0
    # Dibujar rectángulo en horizontal (volteado): ancho visual = rect_largo_3, alto visual = rect_ancho_3
    p3_shape = [[0, 0], [rect_largo_3, 0], [rect_largo_3, rect_ancho_3], [0, rect_ancho_3]]
    ax3.add_patch(patches.Polygon(p3_shape, closed=True, fc='#C1FFD7', ec='k'))
    # Triángulos a los lados (izquierda y derecha) para mantener la geometría original pero rotada
    tri_right = [[rect_largo_3, 0], [rect_largo_3, rect_ancho_3], [rect_largo_3 + tri_altura_3, rect_ancho_3/2]]
    tri_left = [[0, 0], [0, rect_ancho_3], [-tri_altura_3, rect_ancho_3/2]]
    ax3.add_patch(patches.Polygon(tri_right, closed=True, fc='#C1FFD7', ec='k'))
    ax3.add_patch(patches.Polygon(tri_left, closed=True, fc='#C1FFD7', ec='k'))
    ax3.text(rect_largo_3/2, rect_ancho_3/2, '3', ha='center', va='center', fontsize=14)
    # Cotas mejoradas con flechas para Pieza 3
    ax3.annotate('', xy=(0, rect_ancho_3 + offset), xytext=(rect_largo_3, rect_ancho_3 + offset), arrowprops=dict(arrowstyle='<->', ec='blue'))
    ax3.text(rect_largo_3/2, rect_ancho_3 + offset*1.5, f'Largo Rect.: {rect_largo_3:.1f} mm', ha='center', va='bottom', color='blue', fontsize=9)
    ax3.annotate('', xy=(-tri_altura_3 - offset, 0), xytext=(-tri_altura_3 - offset, rect_ancho_3), arrowprops=dict(arrowstyle='<->', ec='red'))
    ax3.text(-tri_altura_3 - offset*1.5, rect_ancho_3/2, f'Ancho:\n{rect_ancho_3:.1f} mm', ha='right', va='center', color='red', fontsize=9)
    # Mostrar largo calculado (override) cuando exista, si no usar el largo del rectángulo como referencia
    l3_mm = mapping.get('3', rect_largo_3)
    ax3.set_title(f"Pieza 3 (Rectángulo+Triángulos) — Largo mostrado: {l3_mm:.1f} mm")

    # --- AJUSTES FINALES Y ESCALA ---
    for ax in [ax_main, ax1, ax2, ax3]: ax.axis('equal'); ax.axis('off')
    plt.tight_layout(pad=2.0, h_pad=3.0)
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    return os.path.abspath(output_path)

# --- INICIO: Ejemplo de uso y Mock de datos ---
if __name__ == '__main__':
    class MockDimensions:
        def __init__(self):
            self.b = 30.0
            self.c_prima = 15.0
            self.anchos = [6.0]
            self.g = 6.0
            self._detalles_para_plot = None

    d_simulado = MockDimensions()
    output_directory = 'output_test'
    ruta_imagen = draw(d_simulado, output_dir=output_directory, step_index=0)
    print(f"Imagen de prueba para 'trifasico_45deg' guardada en: {ruta_imagen}")
# --- FIN: Ejemplo de uso y Mock de datos ---