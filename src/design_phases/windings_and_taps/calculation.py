# src/design_phases/windings_and_taps/calculation.py
# -*- coding: utf-8 -*-

import math

def run(d):
    """Realiza los cálculos de devanados, corrientes y TAPs."""
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