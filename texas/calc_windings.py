# Modulo: calc_windings
# Realiza los calculos de devanados, corrientes y TAPs.

import math
import utils

def run(d):
    def aplicar_redondeo(valor):
        return round(valor, 2) if getattr(d, 'redondear_2_decimales', False) else valor

    N2_calculado = (d.E2_fase * 1e8) / (4.44 * d.f * d.flujo)
    d.N2_fase = round(N2_calculado)

    all_pct = sorted(list(set([-p for p in getattr(d, 'taps_pct', [])] + [0] + getattr(d, 'taps_pct', []))))
    d.tap_data = {}
    for pct in all_pct:
        E1_l_tap = d.E1_linea * (1 + pct / 100.0)
        conn1 = getattr(d, 'conn1', 'D')
        E1_f_tap = E1_l_tap if (getattr(d, 'fases', 3) == 3 and conn1 == 'D') else E1_l_tap / math.sqrt(3)
        N1_f_tap = round(d.N2_fase * (E1_f_tap / d.E2_fase))
        d.tap_data[pct] = {'Vlinea': E1_l_tap, 'Vfase': E1_f_tap, 'N_espiras': N1_f_tap}

    S_dev_VA = (d.S * 1000) / getattr(d, 'fases', 3)
    d.I1_fase_nom = aplicar_redondeo(S_dev_VA / d.E1_fase)
    d.I2_fase = aplicar_redondeo(S_dev_VA / d.E2_fase)
    d.s1 = aplicar_redondeo(d.I1_fase_nom / d.J)
    d.s2 = aplicar_redondeo(d.I2_fase / d.J)

    d.rm = aplicar_redondeo((d.D / 2.0) + (d.c / 4.0))
    d.lm = aplicar_redondeo(2.0 * math.pi * d.rm / 100.0)

    d.awg1, conductor1_props = utils.find_awg_conductor_for_section(getattr(d, 's1', None))
    d.awg2, conductor2_props = utils.find_awg_conductor_for_section(getattr(d, 's2', None))

    rho_cobre_kg_mm3 = 8.96e-6
    if conductor1_props:
        d.peso_conductor_primario_kg_m = conductor1_props.get('peso_g_m', 0) / 1000.0
    else:
        d.peso_conductor_primario_kg_m = aplicar_redondeo(getattr(d, 's1', 0.0) * rho_cobre_kg_mm3 * 1000)

    if conductor2_props:
        d.peso_conductor_secundario_kg_m = conductor2_props.get('peso_g_m', 0) / 1000.0
    else:
        d.peso_conductor_secundario_kg_m = aplicar_redondeo(getattr(d, 's2', 0.0) * rho_cobre_kg_mm3 * 1000)

    N1_max = 0
    if d.tap_data:
        N1_max = d.tap_data[max(d.tap_data.keys())]['N_espiras']
    elif getattr(d, 'E2_fase', 0) != 0:
        N1_max = int(round(d.N2_fase * (d.E1_fase / d.E2_fase)))
    d.N1_fase = N1_max
    
    d.Lb1 = aplicar_redondeo(d.lm * N1_max)
    d.Qb1 = aplicar_redondeo(d.Lb1 * d.peso_conductor_primario_kg_m)
    d.Lb2 = aplicar_redondeo(d.lm * d.N2_fase)
    d.Qb2 = aplicar_redondeo(d.Lb2 * d.peso_conductor_secundario_kg_m)
    d.Qc_por_bobinado = aplicar_redondeo(d.Qb1 + d.Qb2)

    factor_fases = 3 if getattr(d, 'fases', 1) == 3 else 1
    d.Qc_total = aplicar_redondeo(d.Qc_por_bobinado * factor_fases)