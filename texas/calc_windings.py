# Modulo: calc_windings
# Realiza los calculos de devanados, corrientes y TAPs.

import math
import utils
import database as db

def run(d):
    def aplicar_redondeo(valor):
        return round(valor, 2) if getattr(d, 'redondear_2_decimales', False) else valor

    N2_calculado = (d.E2_fase * 1e8) / (4.44 * d.f * d.flujo)
    d.N2_fase = round(N2_calculado)

    S_dev_VA = d.S * 1000
    if getattr(d, 'fases', 3) == 3:
        S_dev_VA = (d.S * 1000) / 3
        
    d.I2_fase = aplicar_redondeo(S_dev_VA / d.E2_fase)

    all_pct = sorted(list(set([-p for p in getattr(d, 'taps_pct', [])] + [0] + getattr(d, 'taps_pct', []))), reverse=True)
    d.tap_data = {}
    max_I1 = 0
    for pct in all_pct:
        E1_l_tap = d.E1_linea * (1 + pct / 100.0)
        if getattr(d, 'fases', 3) == 1:
            E1_f_tap = E1_l_tap
        else:
            conn1 = getattr(d, 'conn1', 'D')
            E1_f_tap = E1_l_tap if conn1 == 'D' else E1_l_tap / math.sqrt(3)
            
        N1_f_tap = round(d.N2_fase * (E1_f_tap / d.E2_fase))
        I1_f_tap = S_dev_VA / E1_f_tap
        if I1_f_tap > max_I1: max_I1 = I1_f_tap
        d.tap_data[pct] = {'Vlinea': E1_l_tap, 'Vfase': E1_f_tap, 'N_espiras': N1_f_tap, 'I1': I1_f_tap}

    if getattr(d, 'fases', 3) == 1:
        d.E1_fase = d.E1_linea
        d.E2_fase = d.E2_linea

    d.I1_fase_nom = aplicar_redondeo(S_dev_VA / d.E1_fase)
    d.I1_max = aplicar_redondeo(max_I1)
    
    d.s1 = aplicar_redondeo(d.I1_max / d.J)
    d.s2 = aplicar_redondeo(d.I2_fase / d.J)

    d.rm = aplicar_redondeo((d.D / 2.0) + (d.c / 4.0))
    d.lm = aplicar_redondeo(2.0 * math.pi * d.rm / 100.0)

    d.awg1, conductor1_props = utils.find_awg_conductor_for_section(getattr(d, 's1', None))
    # Para s2 calcular pletina si es relativamente grande (umbral configurable: 5.0 mm2)
    if d.s2 >= 5.0:
        s_req = d.s2
        w_candidates = sorted(db.pletina_w_std)
        t_list = sorted(db.pletina_t_std)

        best = None
        # Para cada ancho estándar, proponemos un espesor objetivo ~ w/3 y luego
        # encontrar el espesor estándar que cumpla el área por exceso si es posible.
        for w in w_candidates:
            # espesor objetivo aproximadamente 1/3 del ancho
            t_obj = w / 3.0
            # Espesor inicial: el más cercano al objetivo
            t_near = min(t_list, key=lambda x: abs(x - t_obj))
            area_near = w * t_near
            if area_near >= s_req:
                # cumple por exceso
                candidate = (w, t_near, area_near)
            else:
                # buscar el primer espesor estándar que haga area >= s_req
                t_ge = next((t for t in t_list if t * w >= s_req), None)
                if t_ge is not None:
                    candidate = (w, t_ge, w * t_ge)
                else:
                    # este ancho no puede cubrir el requerimiento con ningun espesor estandar
                    candidate = None

            if candidate:
                # elegir el candidato con menor área que cumpla >= s_req
                if best is None or (candidate[2] < best[2]):
                    best = candidate

        if best is None:
            # Si no hay combinación que cumpla por exceso, elegir la mayor área disponible
            w_max = max(w_candidates)
            t_max = max(t_list)
            best = (w_max, t_max, w_max * t_max)

        w_std, t_std, area_std = best
        d.pletina2_w = w_std
        d.pletina2_t = t_std
        d.s2_real = aplicar_redondeo(area_std)
        # Para que los cálculos posteriores usen la sección real seleccionada
        d.s2 = aplicar_redondeo(d.s2_real)
        d.awg2 = 'Pletina'
        conductor2_props = {'ancho_mm': w_std + 0.1, 'espesor_mm': t_std, 'peso_g_m': d.s2_real * 8.96}
    else:
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

    def get_iso_props_completos(V_kV):
        # Buscar en la bd la tensión igual o inmediatamente superior
        for v_limite in sorted(db.clase_aislamiento_db.keys()):
            if V_kV <= v_limite:
                props = db.clase_aislamiento_db[v_limite]
                return props['BIL'], props['d_c'], props['e_y']
        # Si sobrepasa, retornar la máxima
        props = db.clase_aislamiento_db[max(db.clase_aislamiento_db.keys())]
        return props['BIL'], props['d_c'], props['e_y']

    V1_kV = d.E1_linea / 1000.0
    V2_kV = d.E2_linea / 1000.0

    BIL1, d_c_mt, e_y_mt = get_iso_props_completos(V1_kV)
    BIL2, d_c_bt, e_y_bt = get_iso_props_completos(V2_kV)
    
    margen_total_bt = d_c_bt + e_y_bt
    margen_total_mt = d_c_mt + e_y_mt

    d.d_c_bt = d_c_bt
    d.e_y_bt = e_y_bt
    d.margen_total_bt = margen_total_bt

    d.d_c_mt = d_c_mt
    d.e_y_mt = e_y_mt
    d.margen_total_mt = margen_total_mt

    # --- CALCULOS DE BOBINAS Y AISLAMIENTO ---
    # Convertir b a mm (de cm)
    b_mm = getattr(d, 'b', 0) * 10
    
    d.Hb2 = aplicar_redondeo(b_mm - 2 * margen_total_bt)
    d.Hb1 = aplicar_redondeo(b_mm - 2 * margen_total_mt)

    # Espira por capa
    diametro_c1 = conductor1_props.get('diametro_mm', 0.63) if conductor1_props else 0.63
    d.diam_c1_usado = diametro_c1
    
    # Para secundario, si es pletina, se usa ancho equivalente (ej. 5.8 mm)
    ancho_c2 = conductor2_props.get('ancho_mm', 5.8) if conductor2_props else 5.8
    d.ancho_c2_usado = ancho_c2

    d.Ne_cb2 = int(math.floor(d.Hb2 / ancho_c2)) if ancho_c2 > 0 else 0
    d.Ne_cb1 = int(math.floor(d.Hb1 / diametro_c1)) if diametro_c1 > 0 else 0

    d.Nc_b2 = (d.N2_fase / d.Ne_cb2) if d.Ne_cb2 > 0 else 0
    d.Nc_b1 = (d.N1_fase / d.Ne_cb1) if d.Ne_cb1 > 0 else 0

    # Aislamiento entre capas (Impulso) - Aproximando valores típicos
    k_i2 = 0.25
    k_s2 = 3.5
    d.BIL2 = BIL2
    d.Vc2 = 2 * (BIL2 / math.ceil(d.Nc_b2)) * k_i2 if math.ceil(d.Nc_b2) > 0 else 0
    Rigidez_diel = 40.0 # kV/mm promedio
    d.delta_s2 = k_s2 * (d.Vc2 / Rigidez_diel)

    k_i1 = 0.75
    k_s1 = 5.0
    d.BIL1 = BIL1
    d.Vc1 = 2 * (BIL1 / math.ceil(d.Nc_b1)) * k_i1 if math.ceil(d.Nc_b1) > 0 else 0
    d.delta_s1 = k_s1 * (d.Vc1 / Rigidez_diel)

    d.Lb1 = aplicar_redondeo(d.lm * N1_max)
    d.Qb1 = aplicar_redondeo(d.Lb1 * d.peso_conductor_primario_kg_m)
    d.Lb2 = aplicar_redondeo(d.lm * d.N2_fase)
    d.Qb2 = aplicar_redondeo(d.Lb2 * d.peso_conductor_secundario_kg_m)
    d.Qc_por_bobinado = aplicar_redondeo(d.Qb1 + d.Qb2)

    factor_fases = 3 if getattr(d, 'fases', 1) == 3 else 1
    d.Qc_total = aplicar_redondeo(d.Qc_por_bobinado * factor_fases)