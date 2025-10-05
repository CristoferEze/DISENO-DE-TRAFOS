# src/design_phases/windings_and_taps/calculation.py
# -*- coding: utf-8 -*-

import math
from core import utils

def run(d):
    """Realiza los cálculos de devanados, corrientes, TAPs y peso del cobre por bobinado."""
    
    # Función auxiliar para redondear según configuración
    def aplicar_redondeo(valor):
        if getattr(d, 'redondear_2_decimales', False):
            return round(valor, 2)
        return valor
    
    # Espiras del secundario (usar correctamente E2_fase)
    N2_calculado = (d.E2_fase * 1e8) / (4.44 * d.f * d.flujo)
    d.N2_fase = round(N2_calculado)

    # Preparar datos de TAPs (incluye las tomas negativas, 0 y positivas)
    all_pct = sorted(list(set([-p for p in d.taps_pct] + [0] + d.taps_pct)))
    d.tap_data = {}
    for pct in all_pct:
        E1_l_tap = d.E1_linea * (1 + pct / 100.0)
        # Corregir el cálculo de tensión de fase para TAPs considerando la conexión correcta
        E1_f_tap = E1_l_tap if (d.fases == 3 and 'D' in (d.conn1 or '')) else E1_l_tap / math.sqrt(3)
        # Calcular N1 correctamente usando la relación de tensiones de fase
        N1_f_tap = round(d.N2_fase * (E1_f_tap / d.E2_fase))
        d.tap_data[pct] = {
            'Vlinea': aplicar_redondeo(E1_l_tap),
            'Vfase': aplicar_redondeo(E1_f_tap),
            'N_espiras': N1_f_tap
        }

    # Corrientes y secciones nominales
    S_dev_VA = (d.S * 1000) / d.fases
    d.I1_fase_nom = aplicar_redondeo(S_dev_VA / d.E1_fase)
    d.I2_fase = aplicar_redondeo(S_dev_VA / d.E2_fase)
    d.s1 = aplicar_redondeo(d.I1_fase_nom / d.J)
    d.s2 = aplicar_redondeo(d.I2_fase / d.J)

    # --- NUEVO: Cálculo de corrientes y distribución de espiras para TAPs ---
    d.tap_currents = {}
    d.tap_distribution = {}

    if d.taps_pct:
        # Corriente de fase en cada toma
        for pct, data in d.tap_data.items():
            # Evitar división por cero
            if data['Vfase'] and data['Vfase'] != 0:
                I_fase_tap = aplicar_redondeo(S_dev_VA / data['Vfase'])
            else:
                I_fase_tap = float('inf')
            d.tap_currents[pct] = I_fase_tap

        # Distribución de espiras entre tomas (orden descendente de porcentaje)
        sorted_keys = sorted(d.tap_data.keys(), reverse=True)
        if len(sorted_keys) > 1:
            diffs = []
            for i in range(len(sorted_keys)-1):
                n_hi = d.tap_data[sorted_keys[i]]['N_espiras']
                n_lo = d.tap_data[sorted_keys[i+1]]['N_espiras']
                diffs.append(int(round(n_hi - n_lo)))

            N_max = d.tap_data[sorted_keys[0]]['N_espiras']
            N_taps_centrales = sum(diffs)
            # Determinar espiras de la bobina principal (mitad restante)
            N_bobina_principal = int(((N_max - N_taps_centrales) / 2.0) + 0.5)

            d.tap_distribution['principal_start'] = N_bobina_principal
            d.tap_distribution['taps'] = []
            for i in range(len(diffs)):
                d.tap_distribution['taps'].append({
                    'from': sorted_keys[i],
                    'to': sorted_keys[i+1],
                    'turns': diffs[i]
                })
            d.tap_distribution['principal_end'] = N_bobina_principal
            d.tap_distribution['total_check'] = N_bobina_principal * 2 + N_taps_centrales
            d.tap_distribution['N_max'] = N_max

    # --- NUEVO: Cálculo del peso del cobre por bobinado ---
    # 1. Radio medio y longitud media de espira
    # Se asume d.D y d.c en cm; r_m en cm, l_m en metros
    try:
        d.rm = aplicar_redondeo(d.D / 2.0 + d.c / 4.0)
    except Exception:
        d.rm = 0.0
    d.lm = aplicar_redondeo(2.0 * math.pi * d.rm / 100.0)  # metros

    # 2. Selección automática del conductor AWG y peso específico (kg/m)
    # MEJORADO: Múltiples métodos de cálculo de peso
    
    # Método 1: Selección por base de datos AWG
    d.awg1, conductor1_props = utils.find_awg_conductor_for_section(getattr(d, 's1', None))
    d.awg2, conductor2_props = utils.find_awg_conductor_for_section(getattr(d, 's2', None))

    # Método 2: Cálculo teórico como alternativa/verificación
    # Usar densidad opcional del cobre si está disponible
    if d.usar_valores_opcionales and d.rho_cobre_opcional:
        rho_cobre_kg_mm3 = d.rho_cobre_opcional / 1000  # Convertir de kg/cm³ a kg/mm³
    else:
        rho_cobre_kg_mm3 = 8.96e-6  # Densidad del cobre en kg/mm³
    
    if conductor1_props:
        # Usar datos de la base de datos AWG
        d.peso_conductor_primario_kg_m = conductor1_props.get('peso_g_m', 0) / 1000.0
        d.metodo_peso_primario = "Base de datos AWG"
    else:
        # Usar cálculo teórico: peso = sección × longitud × densidad
        d.awg1 = "Cálculo teórico"
        d.peso_conductor_primario_kg_m = aplicar_redondeo(getattr(d, 's1', 0.0) * rho_cobre_kg_mm3 * 1000)  # kg/m
        d.metodo_peso_primario = "Cálculo teórico"
        print(f"Usando cálculo teórico para conductor primario. Sección: {getattr(d, 's1', 0.0):.2f} mm²")

    if conductor2_props:
        # Usar datos de la base de datos AWG
        d.peso_conductor_secundario_kg_m = conductor2_props.get('peso_g_m', 0) / 1000.0
        d.metodo_peso_secundario = "Base de datos AWG"
    else:
        # Usar cálculo teórico: peso = sección × longitud × densidad
        d.awg2 = "Cálculo teórico"
        d.peso_conductor_secundario_kg_m = aplicar_redondeo(getattr(d, 's2', 0.0) * rho_cobre_kg_mm3 * 1000)  # kg/m
        d.metodo_peso_secundario = "Cálculo teórico"
        print(f"Usando cálculo teórico para conductor secundario. Sección: {getattr(d, 's2', 0.0):.2f} mm²")

    # 3. Bobinado primario (usamos el número máximo de espiras de TAPs)
    if d.tap_data:
        try:
            N1_max = d.tap_data[max(d.tap_data.keys())]['N_espiras']
        except Exception:
            N1_max = 0
    else:
        N1_max = 0

    d.Lb1 = aplicar_redondeo(d.lm * N1_max)
    d.Qb1 = aplicar_redondeo(d.Lb1 * d.peso_conductor_primario_kg_m)
    
    # 4. Bobinado secundario
    d.Lb2 = aplicar_redondeo(d.lm * d.N2_fase)
    d.Qb2 = aplicar_redondeo(d.Lb2 * d.peso_conductor_secundario_kg_m)
    
    # 5. Peso total del Cobre (por bobinado, verificación)
    d.Qc_por_bobinado = aplicar_redondeo(d.Qb1 + d.Qb2)
    
    # 6. Ajuste por número de fases (trifásico)
    # En el cálculo físico paso a paso faltaba multiplicar por 3 para un transformador trifásico.
    try:
        factor_fases = 3 if getattr(d, 'fases', 1) == 3 else 1
    except Exception:
        factor_fases = 1
    d.Qc_total = aplicar_redondeo(d.Qc_por_bobinado * factor_fases)