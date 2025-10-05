# src/design_phases/nucleus_and_window/calculation.py
# -*- coding: utf-8 -*-

import math
from core import database as db, utils
from decimal import Decimal, ROUND_HALF_UP

def _find_steel_data(steel_key):
    """
    Función auxiliar para encontrar los datos del acero de forma robusta.
    Busca por la clave principal (ej: 'M-5') y por la designación antigua (ej: '30M5').
    """
    # 1. Intenta una búsqueda directa con la clave principal (ej: 'M-5')
    if steel_key in db.acero_electrico_db:
        return db.acero_electrico_db[steel_key]
    
    # 2. Si falla, itera y busca en la 'designacion_antigua' (ej: '30M5')
    for data in db.acero_electrico_db.values():
        if data.get('designacion_antigua') == steel_key:
            return data
            
    # 3. Si no se encuentra de ninguna forma, lanza un error claro.
    raise KeyError(f"No se encontraron datos para el tipo de acero '{steel_key}' en la base de datos.")

def run(d):
    """Realiza los cálculos del núcleo y la ventana."""
    # Lógica de _calcular_parametros_base (ahora considera valores opcionales)
    if d.usar_valores_opcionales and d.B_opcional:
        d.B_kgauss = d.B_opcional
    else:
        d.B_kgauss = d.B_man if d.B_man else utils.get_promedio(db.densidad_flujo_db[utils.sel_clave(db.densidad_flujo_db, d.S)])
    
    d.B_tesla = d.B_kgauss / 10.0
    
    if d.usar_valores_opcionales and d.J_opcional:
        d.J = d.J_opcional
    else:
        d.J = utils.get_promedio(db.densidad_corriente_db[d.refrig]['Cobre'])
    
    # --- INICIO DE LA CORRECCIÓN ---
    # En lugar de acceder directamente al diccionario, usamos la función auxiliar
    # para encontrar los datos del acero de manera segura.
    try:
        steel_data = _find_steel_data(d.acero)
        # Usar valor opcional de fa si está disponible
        # Usar valor opcional de fa si está disponible.
        # Guardar siempre el valor original sin redondear en d.fa_original y usar d.fa = float(d.fa_original)
        if d.usar_valores_opcionales and d.fa_opcional is not None:
            d.fa_original = d.fa_opcional
        else:
            d.fa_original = steel_data.get('fa', 0.975)
        # CORREGIDO: No redondear NUNCA el factor de apilamiento, independientemente del modo de redondeo
        d.fa = float(d.fa_original)
        d.merma_id = steel_data['merma']
    except KeyError as e:
        # Propagamos el error con un mensaje más descriptivo si la función falla.
        raise ValueError(f"El tipo de acero '{d.acero}' no es válido o no se encuentra en la base de datos.") from e
    # --- FIN DE LA CORRECCIÓN ---
    
    tipo_nucleo_key = f"{d.tipo}_columnas"
    if d.usar_valores_opcionales and d.C_opcional:
        d.C = d.C_opcional
    else:
        d.C = d.C_man if d.C_man else utils.get_promedio(db.constante_flujo_db[tipo_nucleo_key])
    
    # Lógica de _calcular_tensiones_fase (robusta frente a entradas inválidas)
    if d.fases == 3:
        conn_str = (d.conn or '').upper()
        
        # Parsear conexiones del tipo "Dyn5", "D-Yn", etc.
        if conn_str and len(conn_str) >= 3:
            # Para conexiones tipo "Dyn5", "Ynd11", etc.
            if conn_str[0] in ['D', 'Y'] and len(conn_str) > 2:
                d.conn1 = conn_str[0]  # Primera letra (D o Y)
                # Buscar la segunda conexión (después de la primera letra)
                resto = conn_str[1:]
                if resto.startswith('yn') or resto.startswith('YN'):
                    d.conn2 = 'YN'
                    # Extraer índice horario después de 'yn'
                    indice_str = resto[2:] if len(resto) > 2 else '0'
                elif resto.startswith('y') or resto.startswith('Y'):
                    d.conn2 = 'Y'
                    # Extraer índice horario después de 'y'
                    indice_str = resto[1:] if len(resto) > 1 else '0'
                elif resto.startswith('d') or resto.startswith('D'):
                    d.conn2 = 'D'
                    # Extraer índice horario después de 'd'
                    indice_str = resto[1:] if len(resto) > 1 else '0'
                else:
                    d.conn2 = 'YN'  # Default
                    indice_str = '0'
                
                # Convertir índice horario a entero
                try:
                    d.clock_index = int(indice_str)
                except ValueError:
                    d.clock_index = 0
                    
            elif '-' in conn_str:
                parts = conn_str.split('-', 1)
                d.conn1, d.conn2 = parts[0], parts[1]
                d.clock_index = 0  # Default para formato con guión
            else:
                d.conn1 = d.conn2 = conn_str
                d.clock_index = 0
        else:
            d.conn1, d.conn2 = 'D', 'YN'
            d.clock_index = 0
            
        # Calcular tensiones de fase correctamente
        d.E1_fase = d.E1_linea if 'D' in d.conn1 else d.E1_linea / math.sqrt(3)
        d.E2_fase = d.E2_linea if 'D' in d.conn2 else d.E2_linea / math.sqrt(3)
    else:
        d.conn1 = d.conn2 = "Monofasico"
        d.E1_fase = d.E1_linea
        d.E2_fase = d.E2_linea

    # Lógica de _calcular_kc (ahora considera valores opcionales y redondeo)
    if d.usar_valores_opcionales and d.Kc_opcional:
        d.Kc_original = d.Kc_opcional
    elif d.Kc_man:
        d.Kc_original = d.Kc_man
    else:
        E1_kv = d.E1_fase / 1000.0
        kc_n = 8 if d.S <= 10 else (10 if 10 < d.S <= 250 else 12)
        d.Kc_original = (kc_n / (30 + E1_kv)) * 1.15
    
    # Redondear Kc según configuración (usar ROUND_HALF_UP para evitar 'bankers rounding')
    if getattr(d, 'redondear_2_decimales', False):
        d.Kc = float(Decimal(str(d.Kc_original)).quantize(Decimal('1e-2'), rounding=ROUND_HALF_UP))
    else:
        d.Kc = float(Decimal(str(d.Kc_original)).quantize(Decimal('1e-4'), rounding=ROUND_HALF_UP))

    # Lógica de _calcular_nucleo
    d.flujo_original = d.C * math.sqrt(d.S / d.f) * 1e6
    # Convertir a kilolineas y redondear
    d.flujo_kilolineas = d.flujo_original / 1000
    if getattr(d, 'redondear_2_decimales', False):
        d.flujo_kilolineas = round(d.flujo_kilolineas, 2)
        d.flujo = d.flujo_kilolineas * 1000  # Usar valor redondeado para cálculos
    else:
        d.flujo_kilolineas = round(d.flujo_kilolineas, 1)
        d.flujo = d.flujo_original  # Usar valor original para más precisión
    
    d.An = d.flujo / (d.B_kgauss * 1000)
    # CORREGIDO: Usar fa_original para cálculos, no el valor redondeado
    d.Ab = d.An / d.fa_original
    d.num_escalones = d._num_esc(d.Ab)
    
    # Usar valor opcional de Kr si está disponible
    if d.usar_valores_opcionales and d.Kr_opcional:
        d.Kr_original = d.Kr_opcional
    else:
        db_kr_acero = db.coeficiente_kr_db.get(d.merma_id, {})
        db_kr_esc = db_kr_acero.get(d.num_escalones, {})
        d.Kr_original = db_kr_esc[utils.sel_clave(db_kr_esc, d.S)]
    
    # Redondear Kr según configuración (usar ROUND_HALF_UP para evitar 'bankers rounding')
    if getattr(d, 'redondear_2_decimales', False):
        d.Kr = float(Decimal(str(d.Kr_original)).quantize(Decimal('1e-2'), rounding=ROUND_HALF_UP))
    else:
        d.Kr = float(Decimal(str(d.Kr_original)).quantize(Decimal('1e-3'), rounding=ROUND_HALF_UP))
    
    # Calcular diámetro circunscrito D usando valores redondeados
    d.D = 2 * math.sqrt(d.An / (math.pi * d.Kr))
    d.anchos = [factor * d.D for factor in db.dimensiones_escalones_db.get(d.num_escalones, [])]
    d.espesores = []
    suma_e_previos = 0
    for a_i in d.anchos:
        e_i = (math.sqrt(d.D**2 - a_i**2) - suma_e_previos) / 2.0
        d.espesores.append(e_i)
        suma_e_previos += 2 * e_i
    # CORREGIDO: Usar fa_original para cálculos, no el valor redondeado
    d.An_verificacion = 2 * d.fa_original * sum([d.anchos[i] * d.espesores[i] for i in range(len(d.anchos))])

    # Lógica de _calcular_ventana
    S_VA = d.S * 1000; J_A_m2 = d.J * 1e6; An_m2 = d.An * 1e-4
    Aw_m2 = (S_VA) / (3.33 * d.f * d.B_tesla * J_A_m2 * d.Kc * An_m2)
    d.Aw = Aw_m2 * 1e4
    d.b = math.sqrt(d.rel_rw * d.Aw)
    d.M = (d.Aw / d.b) + d.D
    d.c_prima = d.M - d.anchos[0] if d.anchos else None
    d.c = d.M - d.D

    # --- NUEVO: Cálculo de las dimensiones del yugo y columnas ---
    # Estas variables son necesarias para los cálculos de peso precisos y para el plotter.
    a1 = d.anchos[0] if d.anchos else d.D  # Ancho del escalón más grande (o D como fallback)
    
    # Altura del yugo (g), Fórmula (1.54)
    # El ancho del yugo 'a' es igual al ancho del escalón más grande 'a1'
    d.g = d.An / a1 if a1 > 0 else 0
    
    # Longitud del yugo (L) para monofásico, Fórmula (1.55)
    d.L_monofasico = d.c + d.D + a1
    
    # Longitud del yugo (L) para trifásico, Fórmula (1.58)
    d.L_trifasico = 2 * d.c + 2 * d.D + a1
    
    # Generación de imágenes MOVIDA a la capa de UI (app_view.py).
    # El objeto 'diseno' no debe encargarse de crear gráficos en la fase de cálculo.
    d.core_plot_paths = []
    d.core_plot_path = None