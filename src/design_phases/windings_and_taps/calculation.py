# src/design_phases/windings_and_taps/calculation.py
# -*- coding: utf-8 -*-

import math
from core import utils

def run(d):
    """Realiza los cálculos de devanados, corrientes, TAPs y peso del cobre por bobinado."""
    # Espiras del secundario
    d.N2_fase = round((d.E2_fase * 1e8) / (4.44 * d.f * d.flujo))

    # Preparar datos de TAPs (incluye las tomas negativas, 0 y positivas)
    all_pct = sorted(list(set([-p for p in d.taps_pct] + [0] + d.taps_pct)))
    d.tap_data = {}
    for pct in all_pct:
        E1_l_tap = d.E1_linea * (1 + pct / 100.0)
        E1_f_tap = E1_l_tap if (d.fases == 3 and 'D' in (d.conn1 or '')) else E1_l_tap / math.sqrt(3)
        N1_f_tap = round(d.N2_fase * (E1_f_tap / d.E2_fase))
        d.tap_data[pct] = {'Vlinea': E1_l_tap, 'Vfase': E1_f_tap, 'N_espiras': N1_f_tap}

    # Corrientes y secciones nominales
    S_dev_VA = (d.S * 1000) / d.fases
    d.I1_fase_nom = S_dev_VA / d.E1_fase
    d.I2_fase = S_dev_VA / d.E2_fase
    d.s1 = d.I1_fase_nom / d.J
    d.s2 = d.I2_fase / d.J

    # --- NUEVO: Cálculo de corrientes y distribución de espiras para TAPs ---
    d.tap_currents = {}
    d.tap_distribution = {}

    if d.taps_pct:
        # Corriente de fase en cada toma
        for pct, data in d.tap_data.items():
            # Evitar división por cero
            if data['Vfase'] and data['Vfase'] != 0:
                I_fase_tap = S_dev_VA / data['Vfase']
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
        d.rm = d.D / 2.0 + d.c / 4.0
    except Exception:
        d.rm = 0.0
    d.lm = 2.0 * math.pi * d.rm / 100.0  # metros

    # 2. Selección automática del conductor AWG y peso específico (kg/m)
    # Usamos la función utilitaria para elegir el menor AWG cuya sección >= s requerida.
    d.awg1, conductor1_props = utils.find_awg_conductor_for_section(getattr(d, 's1', None))
    d.awg2, conductor2_props = utils.find_awg_conductor_for_section(getattr(d, 's2', None))

    if conductor1_props:
        # La base de datos almacena peso en g/m -> convertir a kg/m
        d.peso_conductor_primario_kg_m = conductor1_props.get('peso_g_m', 0) / 1000.0
    else:
        d.awg1 = "No encontrado"
        d.peso_conductor_primario_kg_m = 0.0
        print(f"Advertencia: No se encontró conductor para sección primaria de {getattr(d, 's1', 0.0):.2f} mm^2")

    if conductor2_props:
        d.peso_conductor_secundario_kg_m = conductor2_props.get('peso_g_m', 0) / 1000.0
    else:
        d.awg2 = "No encontrado"
        d.peso_conductor_secundario_kg_m = 0.0
        print(f"Advertencia: No se encontró conductor para sección secundaria de {getattr(d, 's2', 0.0):.2f} mm^2")

    # 3. Bobinado primario (usamos el número máximo de espiras de TAPs)
    if d.tap_data:
        try:
            N1_max = d.tap_data[max(d.tap_data.keys())]['N_espiras']
        except Exception:
            N1_max = 0
    else:
        N1_max = 0

    d.Lb1 = d.lm * N1_max
    d.Qb1 = d.Lb1 * d.peso_conductor_primario_kg_m

    # 4. Bobinado secundario
    d.Lb2 = d.lm * d.N2_fase
    d.Qb2 = d.Lb2 * d.peso_conductor_secundario_kg_m

    # 5. Peso total del Cobre (por bobinado, verificación)
    d.Qc_por_bobinado = d.Qb1 + d.Qb2