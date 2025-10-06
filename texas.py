# ---------------------------
# CONFIGURACION (modifique los valores a continuación)
# ---------------------------
import math


TIPO_TRANSFORMADOR = 'trifasico'   # 'trifasico' o 'monofasico'
S_kVA = 25                         # kVA
E1_LINEA_V = 10500                 # V
E2_LINEA_V = 400                   # V
FRECUENCIA_HZ = 60                 # Hz
CONEXION = 'D-Yn'                  # e.g. 'Dyn5'
TAPS_PCT = [2.5, 5.0]              # % taps
TIPO_ACERO = 'M-5'                 # usar clave del DB: 'M-3','M-4','M-5','M-6'
RELACION_VENTANA_RW = 3.0

# ---------------------------
# BASES DE DATOS (incrustadas)
# ---------------------------
densidad_flujo_db = {
    1: (11, 13),
    10: (13, 16),
    100: (16, 17),
    1000: (17, 18),
    5000: (17.5, 18)
}

acero_electrico_db = {
    'M-3': {'designacion_antigua': '23M3', 'espesor_mm': 0.23, 'fa': 0.960, 'merma': 'Merma 4.0% (23M3)',
            'perdidas_w_kg_15k': 0.87, 'perdidas_w_kg_16k': 1.03, 'perdidas_w_kg_17k': 1.28},
    'M-4': {'designacion_antigua': '27M4', 'espesor_mm': 0.27, 'fa': 0.965, 'merma': 'Merma 3.5% (27M4)',
            'perdidas_w_kg_15k': 1.02, 'perdidas_w_kg_16k': 1.20, 'perdidas_w_kg_17k': 1.47},
    'M-5': {'designacion_antigua': '30M5', 'espesor_mm': 0.30, 'fa': 0.970, 'merma': 'Merma 3.0% (30M5)',
            'perdidas_w_kg_15k': 1.11, 'perdidas_w_kg_16k': 1.30, 'perdidas_w_kg_17k': 1.57},
    'M-6': {'designacion_antigua': '35M6', 'espesor_mm': 0.35, 'fa': 0.975, 'merma': 'Merma 2.5% (35M6)',
            'perdidas_w_kg_15k': 1.28, 'perdidas_w_kg_16k': 1.51, 'perdidas_w_kg_17k': 1.81}
}

coeficiente_kr_db = {
    'Sin merma': {
        1: {5: 0.637}, 2: {15: 0.787}, 3: {50: 0.851},
        4: {200: 0.887}, 5: {500: 0.908}, 6: {750: 0.924}
    },
    'Merma 2.5% (35M6)': {
        1: {5: 0.621}, 2: {15: 0.767}, 3: {50: 0.830},
        4: {200: 0.865}, 5: {500: 0.885}, 6: {750: 0.900}
    },
    'Merma 3.0% (30M5)': {
        1: {5: 0.618}, 2: {15: 0.763}, 3: {50: 0.825},
        4: {200: 0.860}, 5: {500: 0.881}, 6: {750: 0.896}
    }
}

constante_flujo_db = {
    'monofasico_columnas': (1.2, 1.9),
    'trifasico_columnas': (1.0, 1.6)
}

dimensiones_escalones_db = {
    1: [0.707],
    2: [0.850, 0.526],
    3: [0.906, 0.707, 0.424],
    4: [0.934, 0.796, 0.605, 0.356],
    5: [0.950, 0.846, 0.707, 0.534, 0.313],
    6: [0.959, 0.875, 0.768, 0.640, 0.488, 0.281]
}

awg_conductors_db = {
    '4/0': {'diametro_mm': 11.70, 'seccion_mm2': 107.4, 'peso_g_m': 953},
    '1/0': {'diametro_mm': 8.26, 'seccion_mm2': 53.5, 'peso_g_m': 476},
    '4': {'diametro_mm': 5.18, 'seccion_mm2': 21.1, 'peso_g_m': 188},
    '10': {'diametro_mm': 2.59, 'seccion_mm2': 5.27, 'peso_g_m': 46.9},
    '20': {'diametro_mm': 0.81, 'seccion_mm2': 0.517, 'peso_g_m': 4.61}
}

# ---------------------------
# UTILIDADES (incrustadas)
# ---------------------------
def get_promedio(v):
    return (v[0] + v[1]) / 2.0

def sel_clave(d, val):
    keys = sorted([k for k in d.keys()])
    for k in keys:
        if k >= val:
            return k
    return keys[-1]

def f_dec(v):
    return "{:.2f}".format(v)

def f_int(v):
    try:
        return "{}".format(int(v))
    except Exception:
        return "0"

def get_specific_iron_loss(steel_key, b_kgauss):
    # buscar por clave o designación antigua
    steel_data = None
    if steel_key in acero_electrico_db:
        steel_data = acero_electrico_db[steel_key]
    else:
        for v in acero_electrico_db.values():
            if v.get('designacion_antigua') == steel_key:
                steel_data = v
                break
    if not steel_data:
        return 0.0
    losses = {
        15: steel_data.get('perdidas_w_kg_15k', 0),
        16: steel_data.get('perdidas_w_kg_16k', 0),
        17: steel_data.get('perdidas_w_kg_17k', 0)
    }
    closest_b = min(losses.keys(), key=lambda k: abs(k - b_kgauss))
    return losses[closest_b]

def find_awg_conductor_for_section(section_mm2):
    if section_mm2 is None:
        return (None, None)
    best = None
    min_sec = float('inf')
    for awg, props in awg_conductors_db.items():
        sec = props.get('seccion_mm2', 0)
        if sec >= section_mm2 and sec < min_sec:
            min_sec = sec
            best = (awg, props)
    return best if best else (None, None)

# ---------------------------
# FUNCIONES DE CÁLCULO (self-contained)
# ---------------------------
def calc_nucleus_and_window(d):
    # B
    if getattr(d, 'B_man', None):
        d.B_kgauss = d.B_man
    else:
        d.B_kgauss = get_promedio(densidad_flujo_db[sel_clave(densidad_flujo_db, d.S)])
    d.B_tesla = d.B_kgauss / 10.0

    # J
    d.J = get_promedio({'ONAN': (3.0, 4.0)}['ONAN']) if not getattr(d, 'J', None) else d.J

    # factor de apilamiento y merma
    # buscar acero por claves compatibles (acepta '30M5', 'M-5' etc.)
    steel_key = d.acero
    # intentar mapear designaciones antiguas
    steel_data = None
    for k, v in acero_electrico_db.items():
        if k == steel_key or v.get('designacion_antigua') == steel_key or v.get('codigo_grado') == steel_key:
            steel_data = v
            break
    if not steel_data:
        # fallback simple: tomar primera entrada
        steel_data = list(acero_electrico_db.values())[0]
    d.fa_original = steel_data.get('fa', 0.975)
    d.fa = float(d.fa_original)
    d.merma_id = steel_data.get('merma', next(iter(coeficiente_kr_db.keys())))

    # C
    if getattr(d, 'C_man', None):
        d.C = d.C_man
    else:
        key = 'trifasico_columnas' if d.fases == 3 else 'monofasico_columnas'
        d.C = get_promedio(constante_flujo_db[key])

    # flujo y areas
    d.flujo = d.C * math.sqrt(d.S / d.f) * 1e6
    # Mostrar flujo en kilolíneas y redondear a 2 decimales para reportería
    try:
        d.flujo_kilolineas = round(d.flujo / 1000.0, 2)
    except Exception:
        d.flujo_kilolineas = 0.0
    d.An = d.flujo / (d.B_kgauss * 1000.0)
    d.Ab = d.An / d.fa
    # num escalones
    def _num_esc(ab):
        if ab < 30: return 1
        if ab < 50: return 2
        if ab < 70: return 3
        if ab < 150: return 4
        if ab < 450: return 5
        return 6
    d.num_escalones = _num_esc(d.Ab)
    # Kr desde DB
    db_kr_acero = coeficiente_kr_db.get(d.merma_id, {})
    db_kr_esc = db_kr_acero.get(d.num_escalones, {})
    d.Kr = db_kr_esc.get(sel_clave(db_kr_esc, d.S), list(db_kr_esc.values())[0] if db_kr_esc else 1.0)
    d.D = 2.0 * math.sqrt(d.An / (math.pi * float(d.Kr)))
    d.anchos = [factor * d.D for factor in dimensiones_escalones_db.get(d.num_escalones, [])]
    d.espesores = []
    suma_e_previos = 0.0
    for a_i in d.anchos:
        e_i = (math.sqrt(d.D**2 - a_i**2) - suma_e_previos) / 2.0
        d.espesores.append(e_i)
        suma_e_previos += 2.0 * e_i
    d.An_verificacion = 2.0 * d.fa * sum([d.anchos[i] * d.espesores[i] for i in range(len(d.anchos))])

    # ventana
    S_VA = d.S * 1000.0
    J_A_m2 = d.J * 1e6
    An_m2 = d.An * 1e-4
    if d.Kc is None:
        # Kc estimation
        E1_kv = d.E1_fase / 1000.0
        kc_n = 8 if d.S <= 10 else (10 if 10 < d.S <= 250 else 12)
        d.Kc = (kc_n / (30.0 + E1_kv)) * 1.15
    d.Aw_m2 = (S_VA) / (3.33 * d.f * d.B_tesla * J_A_m2 * d.Kc * An_m2) if (d.B_tesla and J_A_m2 and d.Kc and An_m2) else 0.0
    d.Aw = d.Aw_m2 * 1e4
    d.b = math.sqrt(d.rel_rw * d.Aw) if d.Aw >= 0 else 0.0
    d.M = (d.Aw / d.b) + d.D if d.b != 0 else d.D
    d.c_prima = d.M - (d.anchos[0] if d.anchos else d.D)
    d.c = d.M - d.D

def calc_windings_and_taps(d):
    # espiras secundario
    d.N2_fase = int(round((d.E2_fase * 1e8) / (4.44 * d.f * d.flujo))) if getattr(d, 'flujo', 0) else 0
    all_pct = sorted(list(set([-p for p in d.taps_pct] + [0] + d.taps_pct)))
    d.tap_data = {}
    for pct in all_pct:
        E1_l_tap = d.E1_linea * (1.0 + pct / 100.0)
        E1_f_tap = E1_l_tap if (d.fases == 3 and ('D' in (getattr(d, 'conn1', '') or d.conn))) else E1_l_tap / math.sqrt(3.0)
        try:
            N1_f_tap = int(round(d.N2_fase * (E1_f_tap / d.E2_fase))) if d.E2_fase != 0 else 0
        except Exception:
            N1_f_tap = 0
        d.tap_data[pct] = {'Vlinea': E1_l_tap, 'Vfase': E1_f_tap, 'N_espiras': N1_f_tap}

    # corrientes y secciones
    S_dev_VA = (d.S * 1000.0) / d.fases
    d.I1_fase_nom = S_dev_VA / d.E1_fase if d.E1_fase else 0.0
    d.I2_fase = S_dev_VA / d.E2_fase if d.E2_fase else 0.0
    d.s1 = d.I1_fase_nom / d.J if d.J else 0.0
    d.s2 = d.I2_fase / d.J if d.J else 0.0

    # radio medio y lm
    try:
        d.rm = (d.D / 2.0) + (d.c / 4.0)
    except Exception:
        d.rm = 0.0
    d.lm = 2.0 * math.pi * d.rm / 100.0  # metros

    # elegir AWG
    awg1, props1 = find_awg_conductor_for_section(d.s1)
    awg2, props2 = find_awg_conductor_for_section(d.s2)
    d.awg1, d.awg2 = awg1, awg2
    if props1:
        d.peso_conductor_primario_kg_m = props1.get('peso_g_m', 0) / 1000.0
    else:
        rho_cobre_kg_mm3 = 8.96e-6
        d.peso_conductor_primario_kg_m = d.s1 * rho_cobre_kg_mm3 * 1000.0

    if props2:
        d.peso_conductor_secundario_kg_m = props2.get('peso_g_m', 0) / 1000.0
    else:
        rho_cobre_kg_mm3 = 8.96e-6
        d.peso_conductor_secundario_kg_m = d.s2 * rho_cobre_kg_mm3 * 1000.0

    # N1 calculado si no hay taps
    if d.tap_data:
        try:
            d.N1_fase = d.tap_data[max(d.tap_data.keys())]['N_espiras']
        except Exception:
            d.N1_fase = 0
    else:
        N1_calc = d.N2_fase * (d.E1_fase / d.E2_fase) if d.E2_fase else 0
        d.N1_fase = int(round(N1_calc))

    # longitudes y pesos por bobinado
    d.Lb1 = d.lm * d.N1_fase
    d.Qb1 = d.Lb1 * d.peso_conductor_primario_kg_m
    d.Lb2 = d.lm * d.N2_fase
    d.Qb2 = d.Lb2 * d.peso_conductor_secundario_kg_m
    d.Qc_por_bobinado = d.Qb1 + d.Qb2
    d.Qc_total = d.Qc_por_bobinado * (3 if d.fases == 3 else 1)

def calc_core_and_lamination_weights(d):
    d.peso_por_escalon = []
    d.Qr_por_laminaciones = 0.0
    if getattr(d, 'usar_valores_opcionales', False) and getattr(d, 'rho_acero_opcional', None):
        rho_kg_cm3 = d.rho_acero_opcional
    else:
        rho_kg_cm3 = 7.65 / 1000.0
    # obtener espesor lamina
    # intentar mapear acero a entrada del db
    steel_data = None
    for v in acero_electrico_db.values():
        steel_data = v
        break
    espesor_lamina_mm = steel_data.get('espesor_mm', 0.35)
    espesor_lamina_cm = espesor_lamina_mm / 10.0
    factor_apilamiento = getattr(d, 'fa_original', d.fa)
    if getattr(d, 'anchos', None) and getattr(d, 'espesores', None):
        for i, espesor_escalon in enumerate(d.espesores):
            ancho_escalon_cm = d.anchos[i]
            ancho_paquete_cm = (espesor_escalon * 2.0) if espesor_escalon else espesor_lamina_cm
            num_laminas = int(math.ceil(ancho_paquete_cm / espesor_lamina_cm)) if espesor_lamina_cm > 0 else 0
            # Definir piezas según tipo de corte (Recto o Diagonal) y calcular dimensiones
            cut_type = getattr(d, 'cut_type', 'Recto')
            piezas = []
            if cut_type == 'Recto':
                # base_mayor = l, base_menor = w en corte recto
                piezas = [{
                    'l': ancho_escalon_cm + d.b,
                    'w': ancho_escalon_cm,
                    'n_por_capa': (3 if d.fases == 3 else 2),
                    'base_mayor': (ancho_escalon_cm + d.b),
                    'base_menor': ancho_escalon_cm,
                    'ancho': ancho_escalon_cm
                }]
            else:
                # Corte diagonal: aproximar por trapecio (base mayor, base menor, altura = ancho_escalon_cm)
                base_menor = d.b
                base_mayor = 2.0 * ancho_escalon_cm + d.b
                area_trap = (base_menor + base_mayor) * ancho_escalon_cm / 2.0
                piezas = [{
                    'area': area_trap,
                    'w': ancho_escalon_cm,
                    'n_por_capa': (3 if d.fases == 3 else 2),
                    'base_mayor': base_mayor,
                    'base_menor': base_menor,
                    'ancho': ancho_escalon_cm
                }]

            peso_total_escalon = 0.0
            detalles = []
            for p in piezas:
                num_piezas_total = num_laminas * p['n_por_capa']
                # Volumen según tipo (área * espesor) o l*w*espesor
                if 'area' in p:
                    volumen_una_lamina = p['area'] * espesor_lamina_cm
                    largo_efectivo = p['area'] / p['w'] if p.get('w') else p['area']
                else:
                    volumen_una_lamina = p['l'] * p['w'] * espesor_lamina_cm
                    largo_efectivo = p['l']
                peso_tipo = volumen_una_lamina * rho_kg_cm3 * num_piezas_total * factor_apilamiento

                detalle_item = {
                    'num_piezas': num_piezas_total,
                    'peso_kg': peso_tipo,
                    'ancho_lamina_cm': ancho_escalon_cm,
                    'espesor_lamina_mm': espesor_lamina_mm,
                    'base_mayor_cm': p.get('base_mayor'),
                    'base_menor_cm': p.get('base_menor'),
                    'ancho_cm': p.get('ancho'),
                    'largo_efectivo_cm': largo_efectivo
                }

                detalles.append(detalle_item)
                peso_total_escalon += peso_tipo
            d.peso_por_escalon.append({'escalon': i + 1, 'detalles': detalles, 'peso_total_escalon': peso_total_escalon})
            d.Qr_por_laminaciones += peso_total_escalon
    d.Qr = d.Qr_por_laminaciones if d.Qr_por_laminaciones else 0.0

def calc_losses_and_performance(d):
    # Pc específica W/kg (empírico)
    d.Pc = 2.44 * (getattr(d, 'J', 0.0) ** 2)
    # Qc empírico (kg) — usar fórmula si trifásico
    Kc_val = getattr(d, 'Kc', 1.0)
    b_val = getattr(d, 'b', 0.0)
    c_val = getattr(d, 'c', 0.0)
    D_val = getattr(d, 'D', 0.0)
    try:
        Qc_emp = 0.021 * float(Kc_val) * float(b_val) * float(c_val) * (2.0 * float(D_val) + float(c_val))
    except Exception:
        Qc_emp = 0.0
    d.Qc_empirical_por_formula = Qc_emp
    d.Qc_empirical_total = Qc_emp
    # seleccionar masa cobre para pérdidas
    if getattr(d, 'fases', 3) == 1:
        mass_copper_for_losses = getattr(d, 'Qc_total', getattr(d, 'Qc_por_bobinado', 0.0))
    else:
        mass_copper_for_losses = d.Qc_empirical_por_formula
    d.Qc_used_for_losses = mass_copper_for_losses
    d.Wc = mass_copper_for_losses * d.Pc
    # Pf específica
    if getattr(d, 'usar_valores_opcionales', False) and getattr(d, 'Pf_opcional', None):
        d.Pf = d.Pf_opcional
    else:
        d.Pf = get_specific_iron_loss(getattr(d, 'acero', None), getattr(d, 'B_kgauss', 0.0))
    # Qf empírico
    if getattr(d, 'fases', 3) == 1:
        d.Qf_empirical = getattr(d, 'Qr', 0.0)
    else:
        kr_for_Qf = getattr(d, 'Kr', 1.0)
        try:
            d.Qf_empirical = 0.006 * float(kr_for_Qf) * (float(D_val) ** 2) * (3.0 * float(b_val) + 4.0 * float(c_val) + 5.87 * float(D_val))
        except Exception:
            d.Qf_empirical = 0.0
    d.Wf = d.Qf_empirical * d.Pf
    # rendimiento plena carga
    P_salida_W = getattr(d, 'S', 0.0) * 1000.0
    P_entrada_W = P_salida_W + getattr(d, 'Wc', 0.0) + getattr(d, 'Wf', 0.0)
    d.rendimiento = (P_salida_W / P_entrada_W) * 100.0 if P_entrada_W > 0 else 0.0

def calc_daily_performance(d):
    d.energia_salida_total = 0.0
    d.energia_perdida_cobre_total = 0.0
    d.energia_perdida_hierro_total = 0.0
    d.detalles_ciclo = []
    if not getattr(d, 'ciclo_carga', None):
        return
    try:
        d.energia_perdida_hierro_total = (d.Wf / 1000.0) * 24.0
    except Exception:
        d.energia_perdida_hierro_total = 0.0
    for carga_frac, horas in d.ciclo_carga:
        P_salida_kW = d.S * carga_frac
        energia_salida = P_salida_kW * horas
        d.energia_salida_total += energia_salida
        Wc_variable_kW = (getattr(d, 'Wc', 0.0) / 1000.0) * (carga_frac ** 2)
        energia_perdida_cobre = Wc_variable_kW * horas
        d.energia_perdida_cobre_total += energia_perdida_cobre
        d.detalles_ciclo.append({
            'carga_frac': carga_frac,
            'horas': horas,
            'energia_salida_kwh': energia_salida,
            'energia_perdida_cu_kwh': energia_perdida_cobre
        })
    d.energia_perdida_total = d.energia_perdida_cobre_total + d.energia_perdida_hierro_total
    energia_entrada_total = d.energia_salida_total + d.energia_perdida_total
    d.rendimiento_diario = (d.energia_salida_total / energia_entrada_total) * 100.0 if energia_entrada_total > 0 else 0.0

# ---------------------------
# CLASE DE DATOS Y EJECUCIÓN
# ---------------------------
class Diseno:
    def __init__(self, tipo='trifasico', S=25.0, E1=10500.0, E2=400.0, f=60.0, conn='D-Yn', acero='30M5', taps=None, rel_rw=3.0):
        self.tipo = tipo
        self.S = float(S)
        self.E1_linea = float(E1)
        self.E2_linea = float(E2)
        self.f = float(f)
        self.refrig = 'ONAN'
        self.acero = acero
        self.conn = conn
        self.taps_pct = taps or []
        self.rel_rw = rel_rw
        self.fases = 3 if self.tipo == 'trifasico' else 1

        # valores opcionales
        self.usar_valores_opcionales = False
        self.redondear_2_decimales = False
        self.B_man = None
        self.C_man = None
        self.Kc_man = None
        self.Kc = None

        # inicializaciones para evitar atributos faltantes
        self.E1_fase = None
        self.E2_fase = None
        self.conn1 = None
        self.conn2 = None

    def preparar_conexiones(self):
        if self.fases == 3:
            conn_str = (self.conn or '').upper()
            parts = conn_str.split('-', 1) if '-' in conn_str else [conn_str, conn_str]
            self.conn1 = parts[0]
            self.conn2 = parts[1] if len(parts) > 1 else parts[0]
            self.E1_fase = self.E1_linea if 'D' in self.conn1 else self.E1_linea / math.sqrt(3.0)
            self.E2_fase = self.E2_linea if 'D' in self.conn2 else self.E2_linea / math.sqrt(3.0)
        else:
            self.conn1 = self.conn2 = 'Monofasico'
            self.E1_fase = self.E1_linea
            self.E2_fase = self.E2_linea

    def ejecutar_todas_fases(self):
        # preparar
        self.preparar_conexiones()
        if self.Kc_man:
            self.Kc = self.Kc_man
        # 1 nucleo y ventana
        calc_nucleus_and_window(self)
        # 2 devanados y taps
        calc_windings_and_taps(self)
        # 3 peso laminaciones
        calc_core_and_lamination_weights(self)
        # 4 perdidas y rendimiento
        calc_losses_and_performance(self)
        # 5 desempeño diario (ejemplo de ciclo, puede modificarse)
        if not hasattr(self, 'ciclo_carga'):
            self.ciclo_carga = [(1.0, 8.0), (0.5, 8.0), (0.25, 8.0)]
        calc_daily_performance(self)

def mostrar_resumen(d):
    # Sección: datos de tablas y parámetros usados
    print("\n# --- DATOS Y PARAMETROS USADOS ---")
    print("Tipo: {}".format(d.tipo))
    print("S (kVA): {}".format(d.S))
    print("Frecuencia (Hz): {}".format(d.f))
    print("Conexion: {}".format(d.conn))
    print("Taps (%): {}".format(d.taps_pct))
    print("Acero (clave): {}".format(d.acero))
    print("Factor apilamiento (fa): {}".format(getattr(d, 'fa', None)))
    print("Coeficiente Kr: {}".format(getattr(d, 'Kr', None)))
    print("Coeficiente Kc: {}".format(getattr(d, 'Kc', None)))
    print("Densidad de corriente J (A/mm2): {}".format(getattr(d, 'J', None)))

    # Flujo y areas
    print("\n# --- FLUJO MAGNETICO Y AREAS ---")
    # Mostrar flujo en kilolíneas redondeado a 2 decimales
    print("Flujo (kilolineas): {}".format(f_dec(getattr(d, 'flujo_kilolineas', 0))))
    print("B (kGauss): {}".format(getattr(d, 'B_kgauss', None)))
    print("B (Tesla): {}".format(getattr(d, 'B_tesla', None)))
    print("Area Neta An (cm2): {}".format(f_dec(getattr(d, 'An', 0))))
    print("Area Bruta Ab (cm2): {}".format(f_dec(getattr(d, 'Ab', 0))))
    print("Numero de escalones: {}".format(getattr(d, 'num_escalones', None)))

    # Dimensiones nucleo
    print("\n# --- DIMENSIONES DEL NUCLEO ---")
    print("Diametro D (cm): {}".format(f_dec(getattr(d, 'D', 0))))
    if getattr(d, 'anchos', None):
        for i in range(len(d.anchos)):
            a_val = d.anchos[i]
            e_val = d.espesores[i] if i < len(d.espesores) else None
            print("  Escalon {}: ancho a{} = {} cm, espesor e{} = {} cm".format(i+1, i+1, f_dec(a_val), i+1, f_dec(e_val)))
    print("Verificacion An (cm2): {}".format(f_dec(getattr(d, 'An_verificacion', 0))))

    # Ventana
    print("\n# --- VENTANA ---")
    print("Area Ventana Aw (cm2): {}".format(f_dec(getattr(d, 'Aw', 0))))
    print("Alto de ventana b (cm): {}".format(f_dec(getattr(d, 'b', 0))))
    print("Distancia entre ejes M (cm): {}".format(f_dec(getattr(d, 'M', 0))))
    print("Ancho ventana c (cm): {}".format(f_dec(getattr(d, 'c', 0))))
    print("c' (cm): {}".format(f_dec(getattr(d, 'c_prima', 0))))

    # Tensiones y espiras
    print("\n# --- TENSIONES Y ESPIRAS ---")
    print("E1 Linea (V): {}".format(f_int(getattr(d, 'E1_linea', 0))))
    print("E2 Linea (V): {}".format(f_int(getattr(d, 'E2_linea', 0))))
    print("E1 Fase (V): {}".format(f_dec(getattr(d, 'E1_fase', 0))))
    print("E2 Fase (V): {}".format(f_dec(getattr(d, 'E2_fase', 0))))
    print("N2 por fase (espiras): {}".format(getattr(d, 'N2_fase', None)))
    # Mostrar datos de taps detallados
    if getattr(d, 'tap_data', None):
        keys = sorted(d.tap_data.keys(), reverse=True)
        print("Tomas (detalle):")
        for pct in keys:
            td = d.tap_data[pct]
            print("  Toma {:+.1f}%: Vlinea={} V, Vfase={} V, N_espiras={}".format(pct, f_int(td.get('Vlinea',0)), f_dec(td.get('Vfase',0)), td.get('N_espiras',0)))

    # Corrientes y secciones
    print("\n# --- CORRIENTES Y CALIBRES ---")
    print("I1 fase nominal (A): {}".format(f_dec(getattr(d, 'I1_fase_nom', 0))))
    print("I2 fase (A): {}".format(f_dec(getattr(d, 'I2_fase', 0))))
    print("Seccion s1 (mm2): {}".format(f_dec(getattr(d, 's1', 0))))
    print("Seccion s2 (mm2): {}".format(f_dec(getattr(d, 's2', 0))))

    # Distribucion de espiras (si hay taps)
    if getattr(d, 'tap_data', None) and len(d.tap_data) > 1:
        print("\n# --- DISTRIBUCION DE ESPIRAS (TAPS) ---")
        s_k = sorted(d.tap_data.keys(), reverse=True)
        diffs = []
        for i in range(len(s_k)-1):
            n_hi = d.tap_data[s_k[i]]['N_espiras']
            n_lo = d.tap_data[s_k[i+1]]['N_espiras']
            diffs.append(int(round(n_hi - n_lo)))
        N_max = d.tap_data[s_k[0]]['N_espiras']
        N_taps_centrales = 0
        for v in diffs:
            N_taps_centrales += v
        N_bobina_principal = int(((N_max - N_taps_centrales) / 2.0) + 0.5)
        print("  N_max: {}".format(N_max))
        print("  Espiras bobina principal (inicio): {}".format(N_bobina_principal))
        for i in range(len(diffs)):
            print("  De tap {:+.1f}% a tap {:+.1f}%: {} espiras".format(s_k[i], s_k[i+1], diffs[i]))
        print("  Espiras bobina principal (final): {}".format(N_bobina_principal))
        print("  Verificacion total: {} (debe ser N_max={})".format(N_bobina_principal*2 + N_taps_centrales, N_max))

    # Pesos y bobinados
    print("\n# --- BOBINADOS Y PESOS DE COBRE ---")
    print("Longitud espira media lm (m): {}".format(f_dec(getattr(d, 'lm', 0))))
    print("Largo bobinado primario Lb1 (m): {}".format(f_dec(getattr(d, 'Lb1', 0))))
    print("Peso bobinado primario Qb1 (kg): {}".format(f_dec(getattr(d, 'Qb1', 0))))
    print("Largo bobinado secundario Lb2 (m): {}".format(f_dec(getattr(d, 'Lb2', 0))))
    print("Peso bobinado secundario Qb2 (kg): {}".format(f_dec(getattr(d, 'Qb2', 0))))
    print("Qc por bobinado (kg): {}".format(f_dec(getattr(d, 'Qc_por_bobinado', 0))))
    print("Qc total (kg): {}".format(f_dec(getattr(d, 'Qc_total', 0))))

    # Pesos de hierro y laminaciones
    print("\n# --- PESO HIERRO Y LAMINACIONES ---")
    if getattr(d, 'peso_por_escalon', None):
        for pe in d.peso_por_escalon:
            print("  Escalon {}: peso_total_escalon = {}".format(pe.get('escalon'), f_dec(pe.get('peso_total_escalon',0))))
            detalles = pe.get('detalles', [])
            for det in detalles:
                # Mostrar número de piezas, peso y dimensiones (base mayor, base menor, ancho)
                print("    Piezas: {}, Peso(kg): {}, Base mayor(cm): {}, Base menor(cm): {}, Ancho(cm): {}".format(
                    det.get('num_piezas'),
                    f_dec(det.get('peso_kg',0)),
                    f_dec(det.get('base_mayor_cm', 0)) if det.get('base_mayor_cm') is not None else "0.00",
                    f_dec(det.get('base_menor_cm', 0)) if det.get('base_menor_cm') is not None else "0.00",
                    f_dec(det.get('ancho_cm', 0)) if det.get('ancho_cm') is not None else "0.00"
                ))
    print("Qr (kg hierro total): {}".format(f_dec(getattr(d, 'Qr', 0))))

    # Perdidas y rendimiento
    print("\n# --- PERDIDAS Y RENDIMIENTO ---")
    print("Pc especifica (W/kg): {}".format(f_dec(getattr(d, 'Pc', 0))))
    print("Qc usada para perdidas (kg): {}".format(f_dec(getattr(d, 'Qc_used_for_losses', 0))))
    print("Wc (W): {}".format(f_dec(getattr(d, 'Wc', 0))))
    print("Qf emp (kg): {}".format(f_dec(getattr(d, 'Qf_empirical', 0))))
    print("Pf especifica (W/kg): {}".format(f_dec(getattr(d, 'Pf', 0))))
    print("Wf (W): {}".format(f_dec(getattr(d, 'Wf', 0))))
    print("Rendimiento a plena carga (%): {}".format(f_dec(getattr(d, 'rendimiento', 0))))

    # Desempeño diario: detallar ciclo
    if getattr(d, 'detalles_ciclo', None):
        print("\n# --- DESEMPEÑO DIARIO (detalles por intervalo) ---")
        for idx in range(len(d.detalles_ciclo)):
            it = d.detalles_ciclo[idx]
            print("  Intervalo {}: carga_frac={}, horas={}, energia_salida_kWh={}, energia_perdida_cobre_kWh={}".format(
                idx+1, it.get('carga_frac'), it.get('horas'), f_dec(it.get('energia_salida_kwh',0)), f_dec(it.get('energia_perdida_cu_kwh',0))
            ))
        print("  Energia perdida hierro total (kWh/d): {}".format(f_dec(getattr(d, 'energia_perdida_hierro_total', 0))))
        print("  Energia perdida cobre total (kWh/d): {}".format(f_dec(getattr(d, 'energia_perdida_cobre_total', 0))))
        print("  Energia salida total (kWh/d): {}".format(f_dec(getattr(d, 'energia_salida_total', 0))))
        print("  Energia perdida total (kWh/d): {}".format(f_dec(getattr(d, 'energia_perdida_total', 0))))
        print("  Rendimiento diario (%): {}".format(f_dec(getattr(d, 'rendimiento_diario', 0))))

    print("\n--- FIN DEL RESUMEN ---")

d = Diseno(
        tipo='trifasico',
        S=25,
        E1=10500,
        E2=400,
        f=60,
        conn='D-Yn',
        acero='M-5',  # usa clave del db para mejor mapeo
        taps=[2.5, 5.0],
        rel_rw=3.0
    )
d.ejecutar_todas_fases()
mostrar_resumen(d)
