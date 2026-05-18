# core.py - contiene la función run para la fase de windings_and_taps
import math
from core import utils
from core import database
from .pletina import select_pletina

def run(d):
    # Función auxiliar para redondear según configuración
    def aplicar_redondeo(valor):
        if getattr(d, 'redondear_2_decimales', False):
            return round(valor, 2)
        return valor

    # Espiras del secundario (usar correctamente E2_fase)
    N2_calculado = (d.E2_fase * 1e8) / (4.44 * d.f * d.flujo)
    d.N2_fase = round(N2_calculado)

    # Preparar datos de TAPs y corrientes
    all_pct = sorted(list(set([-p for p in getattr(d, 'taps_pct', [])] + [0] + getattr(d, 'taps_pct', []))), reverse=True)
    d.tap_data = {}

    S_dev_VA = d.S * 1000
    if getattr(d, 'fases', 3) == 3:
        S_dev_VA = (d.S * 1000) / 3
    # Guardar para que el renderer solo presente (sin recalcular)
    d.S_dev_VA = S_dev_VA

    d.I2_fase = aplicar_redondeo(S_dev_VA / d.E2_fase) if getattr(d, 'E2_fase', 0) else 0

    max_I1 = 0.0
    for pct in all_pct:
        E1_l_tap = d.E1_linea * (1 + pct / 100.0)
        if getattr(d, 'fases', 3) == 1:
            E1_f_tap = E1_l_tap
        else:
            conn1 = getattr(d, 'conn1', 'D')
            E1_f_tap = E1_l_tap if conn1 == 'D' else E1_l_tap / math.sqrt(3)

        N1_f_tap = round(d.N2_fase * (E1_f_tap / d.E2_fase)) if getattr(d, 'E2_fase', 0) else 0
        I1_f_tap = S_dev_VA / E1_f_tap if E1_f_tap else 0
        if I1_f_tap > max_I1:
            max_I1 = I1_f_tap

        d.tap_data[pct] = {
            'Vlinea': aplicar_redondeo(E1_l_tap),
            'Vfase': aplicar_redondeo(E1_f_tap),
            'N_espiras': N1_f_tap,
            'I1': aplicar_redondeo(I1_f_tap)
        }

    d.I1_fase_nom = aplicar_redondeo(S_dev_VA / d.E1_fase) if getattr(d, 'E1_fase', 0) else 0
    d.I1_max = aplicar_redondeo(max_I1)

    d.s1 = aplicar_redondeo(d.I1_max / d.J) if getattr(d, 'J', 0) else 0
    try:
        d.s2_req = float(d.I2_fase) / float(d.J) if getattr(d, 'J', 0) else 0.0
    except Exception:
        d.s2_req = 0.0
    d.s2 = d.s2_req

    # TAP currents and distribution
    d.tap_currents = {}
    d.tap_distribution = {}
    if d.taps_pct:
        for pct, data in d.tap_data.items():
            I_fase_tap = aplicar_redondeo(S_dev_VA / data['Vfase']) if data['Vfase'] else float('inf')
            d.tap_currents[pct] = I_fase_tap

        sorted_keys = sorted(d.tap_data.keys(), reverse=True)
        if len(sorted_keys) > 1:
            diffs = []
            for i in range(len(sorted_keys)-1):
                n_hi = d.tap_data[sorted_keys[i]]['N_espiras']
                n_lo = d.tap_data[sorted_keys[i+1]]['N_espiras']
                diffs.append(int(round(n_hi - n_lo)))

            N_max = d.tap_data[sorted_keys[0]]['N_espiras']
            N_taps_centrales = sum(diffs)
            N_bobina_principal = int(((N_max - N_taps_centrales) / 2.0) + 0.5)
            d.tap_distribution['principal_start'] = N_bobina_principal
            d.tap_distribution['taps'] = []
            for i in range(len(diffs)):
                d.tap_distribution['taps'].append({'from': sorted_keys[i], 'to': sorted_keys[i+1], 'turns': diffs[i]})
            d.tap_distribution['principal_end'] = N_bobina_principal
            d.tap_distribution['total_check'] = N_bobina_principal * 2 + N_taps_centrales
            d.tap_distribution['N_max'] = N_max

    # provisional N1
    try:
        if d.tap_data:
            d.N1_fase = int(d.tap_data[max(d.tap_data.keys())]['N_espiras'])
        else:
            d.N1_fase = int(round(d.N2_fase * (d.E1_fase / d.E2_fase))) if getattr(d, 'E2_fase', 0) else 0
    except Exception:
        d.N1_fase = 0

    # aislamiento props
    try:
        def get_iso_props_completos(V_kV):
            for v_limite in sorted(database.clase_aislamiento_db.keys()):
                if V_kV <= v_limite:
                    props = database.clase_aislamiento_db[v_limite]
                    return props['BIL'], props['d_c'], props['e_y']
            props = database.clase_aislamiento_db[max(database.clase_aislamiento_db.keys())]
            return props['BIL'], props['d_c'], props['e_y']

        # Usar tensión de fase (E1_fase/E2_fase) para determinar la clase de aislamiento (BIL).
        # Si no están disponibles, usar la tensión de línea como fallback.
        V1_volt = getattr(d, 'E1_fase', None) if getattr(d, 'E1_fase', None) not in (None, 0) else getattr(d, 'E1_linea', 0.0)
        V2_volt = getattr(d, 'E2_fase', None) if getattr(d, 'E2_fase', None) not in (None, 0) else getattr(d, 'E2_linea', 0.0)
        V1_kV = float(V1_volt) / 1000.0
        V2_kV = float(V2_volt) / 1000.0
        d.BIL1, d.d_c_mt, d.e_y_mt = get_iso_props_completos(V1_kV)
        d.BIL2, d.d_c_bt, d.e_y_bt = get_iso_props_completos(V2_kV)
        d.margen_total_bt = d.d_c_bt + d.e_y_bt
        d.margen_total_mt = d.d_c_mt + d.e_y_mt
        Rigidez_diel = getattr(database, 'rigidez_papel_presspan', 40.0)
    except Exception:
        d.BIL1 = getattr(d, 'BIL1', 0)
        d.BIL2 = getattr(d, 'BIL2', 0)
        d.d_c_mt = getattr(d, 'd_c_mt', 6.5)
        d.e_y_mt = getattr(d, 'e_y_mt', 1.5)
        d.d_c_bt = getattr(d, 'd_c_bt', 6.5)
        d.e_y_bt = getattr(d, 'e_y_bt', 1.5)
        d.margen_total_bt = d.d_c_bt + d.e_y_bt
        d.margen_total_mt = d.d_c_mt + d.e_y_mt
        Rigidez_diel = 40.0

    # Obtener propiedades de conductores por AWG para primario (referencia)
    # Esto asegura que 'conductor1_props' esté definido antes de su uso más abajo.
    try:
        d.awg1, conductor1_props = utils.find_awg_conductor_for_section(getattr(d, 's1', None))
    except Exception:
        d.awg1, conductor1_props = (None, None)

    # Si encontramos propiedades AWG para el primario (MT), usar su peso/diámetro
    try:
        if conductor1_props:
            # peso_g_m está en g/m en la BD; convertir a kg/m
            peso_g_m = conductor1_props.get('peso_g_m', None)
            if peso_g_m is not None:
                d.peso_conductor_primario_kg_m = float(peso_g_m) / 1000.0
            # diámetro
            d.diam_c1_usado = conductor1_props.get('diametro_mm', d.diam_c1_usado if hasattr(d, 'diam_c1_usado') else 0.63)
    except Exception:
        pass

    # Selección de pletina usando el módulo pletina.select_pletina
    required_area = float(getattr(d, 's2_req', getattr(d, 's2', 0.0)))
    sel = select_pletina(required_area, database)
    d.t_min_pletina = sel['t_min']
    d.pletina2_w_exact = sel['w']
    d.pletina2_t_exact = sel['t']
    d.s2_adoptada = sel['area']
    d.s2_real = aplicar_redondeo(d.s2_adoptada)
    d.awg2 = 'Pletina'
    conductor2_props = {'ancho_mm': sel['w'], 'espesor_mm': sel['t'], 'peso_g_m': sel['area'] * 8.96}

    # Ajustar peso del conductor secundario (BT) desde conductor2_props si está disponible
    try:
        if conductor2_props and 'peso_g_m' in conductor2_props:
            d.peso_conductor_secundario_kg_m = float(conductor2_props['peso_g_m']) / 1000.0
    except Exception:
        pass

    # fallback si conductor2_props no está definido (defensa extra)
    if conductor2_props is None:
        adopted_area = getattr(d, 's2_adoptada', None) or getattr(d, 's2', None) or getattr(d, 's2_req', 0.0)
        w_used = getattr(d, 'pletina2_w_exact', getattr(d, 'pletina2_w', 5.8))
        t_used = getattr(d, 'pletina2_t_exact', getattr(d, 'pletina2_t', 1.0))
        try:
            adopted_area = float(adopted_area)
        except Exception:
            adopted_area = 0.0
        try:
            w_used = float(w_used)
        except Exception:
            w_used = 5.8
        try:
            t_used = float(t_used)
        except Exception:
            t_used = 1.0
        conductor2_props = {'ancho_mm': w_used, 'espesor_mm': t_used, 'peso_g_m': adopted_area * 8.96}
        d.metodo_peso_secundario = 'Pletina'

    # Bobinado (longitudes, espiras por capa)
    try:
        d.rm = aplicar_redondeo(d.D / 2.0 + d.c / 4.0)
    except Exception:
        d.rm = 0.0
    d.lm = aplicar_redondeo(2.0 * math.pi * d.rm / 100.0)

    diametro_c1 = conductor1_props.get('diametro_mm', 0.63) if conductor1_props else 0.63
    d.diam_c1_usado = diametro_c1
    ancho_c2 = conductor2_props.get('ancho_mm', 5.8) if conductor2_props else 5.8
    d.ancho_c2_usado = ancho_c2

    d.Hb2 = aplicar_redondeo(getattr(d, 'b', 0.0) * 10 - 2 * getattr(d, 'margen_total_bt', 0.0))
    d.Hb1 = aplicar_redondeo(getattr(d, 'b', 0.0) * 10 - 2 * getattr(d, 'margen_total_mt', 0.0))

    # Ajuste: permitir un margen adicional en el ancho del conductor tomado desde la base de datos.
    # Esto evita sumar un valor hardcodeado (ej. 0.2) en el cálculo y lo hace configurable.
    try:
        # Por defecto sumar 0.2 mm al ancho del conductor salvo que la BD indique otro valor
        ancho_margin_mm = float(getattr(database, 'conductor_width_margin_mm', 0.2))
    except Exception:
        ancho_margin_mm = 0.2

    ancho_c2_effectivo = (ancho_c2 + ancho_margin_mm) if ancho_c2 is not None else ancho_c2
    d.ancho_c2_effectivo = ancho_c2_effectivo
    d.conductor_width_margin_mm = ancho_margin_mm
    d.Ne_cb2 = int(math.floor(d.Hb2 / ancho_c2_effectivo)) if ancho_c2_effectivo and ancho_c2_effectivo > 0 else 0
    d.Ne_cb1 = int(math.floor(d.Hb1 / diametro_c1)) if diametro_c1 > 0 else 0

    d.Nc_b2 = (d.N2_fase / d.Ne_cb2) if d.Ne_cb2 > 0 else 0
    d.Nc_b1 = (getattr(d, 'N1_fase', 0) / d.Ne_cb1) if d.Ne_cb1 > 0 else 0
    try:
        d.ceil_Nc_b2 = math.ceil(d.Nc_b2) if d.Nc_b2 else 1
    except Exception:
        d.ceil_Nc_b2 = 1
    try:
        d.ceil_Nc_b1 = math.ceil(d.Nc_b1) if d.Nc_b1 else 1
    except Exception:
        d.ceil_Nc_b1 = 1

    # Generar lista de candidatos de pletina (solo cálculo, para presentación en el renderer)
    try:
        w_list = sorted(list(database.pletina_w_std))
        t_list = sorted(list(database.pletina_t_std))
        candidates = []
        for w in w_list:
            for t in t_list:
                area = w * t
                if area >= required_area:
                    meets_eq = (3.0 * (t ** 2) >= required_area)
                    score = abs(t - (w / 3.0))
                    candidates.append({'w': float(w), 't': float(t), 'area': float(area), 'meets_eq': meets_eq, 'score': score})
        # ordenar y guardar los mejores
        candidates.sort(key=lambda x: (not x['meets_eq'], x['score'], x['area']))
        d.pletina_candidates = candidates[:8]
    except Exception:
        d.pletina_candidates = []

    # Calcular y redondear t_min para Media Tensión (si aplica) usando el mismo paso
    try:
        req_s1 = float(getattr(d, 's1', 0.0))
        t_min_mt = math.sqrt(req_s1 / 3.0) if req_s1 and req_s1 > 0 else 0.0
        step = float(getattr(database, 'pletina_thickness_step_mm', 0.1))
        if step > 0 and t_min_mt > 0:
            t_min_mt_rounded = math.ceil(t_min_mt / step) * step
        else:
            t_min_mt_rounded = t_min_mt
        d.t_min_pletina_mt = aplicar_redondeo(t_min_mt_rounded)
    except Exception:
        d.t_min_pletina_mt = getattr(d, 't_min_pletina_mt', 0.0)

    # Aislamiento entre capas
    k_i2 = 0.25
    k_s2 = 3.5
    d.BIL2 = getattr(d, 'BIL2', 0)
    d.Vc2 = 2 * (getattr(d, 'BIL2', 0) / math.ceil(d.Nc_b2)) * k_i2 if math.ceil(d.Nc_b2) > 0 else 0
    Rigidez_diel = 40.0
    d.delta_s2 = k_s2 * (d.Vc2 / Rigidez_diel)

    # Guardar delta redondeado hacia arriba al décimo para presentación
    try:
        d.delta_s2_rounded = math.ceil(float(d.delta_s2) * 10.0) / 10.0 if float(d.delta_s2) > 0 else 0.0
    except Exception:
        d.delta_s2_rounded = getattr(d, 'delta_s2', 0.0)

    k_i1 = 0.75
    k_s1 = 5.0
    d.BIL1 = getattr(d, 'BIL1', 0)
    d.Vc1 = 2 * (getattr(d, 'BIL1', 0) / math.ceil(d.Nc_b1)) * k_i1 if math.ceil(d.Nc_b1) > 0 else 0
    d.delta_s1 = k_s1 * (d.Vc1 / Rigidez_diel)
    try:
        d.delta_s1_rounded = math.ceil(float(d.delta_s1) * 10.0) / 10.0 if float(d.delta_s1) > 0 else 0.0
    except Exception:
        d.delta_s1_rounded = getattr(d, 'delta_s1', 0.0)

    # Normalizar conexion
    try:
        d.conn = getattr(d, 'conn1', getattr(d, 'conn', 'Dyn5'))
    except Exception:
        d.conn = getattr(d, 'conn', 'Dyn5')

    # Pesos y longitudes finales
    d.Lb1 = aplicar_redondeo(d.lm * (getattr(d, 'N1_fase', 0) or 0))
    d.Qb1 = aplicar_redondeo(d.Lb1 * getattr(d, 'peso_conductor_primario_kg_m', 0.0))
    d.Lb2 = aplicar_redondeo(d.lm * getattr(d, 'N2_fase', 0))
    d.Qb2 = aplicar_redondeo(d.Lb2 * getattr(d, 'peso_conductor_secundario_kg_m', 0.0))
    d.Qc_por_bobinado = aplicar_redondeo(d.Qb1 + d.Qb2)

    try:
        factor_fases = 3 if getattr(d, 'fases', 1) == 3 else 1
    except Exception:
        factor_fases = 1
    d.Qc_total = aplicar_redondeo(d.Qc_por_bobinado * factor_fases)
