# Modulo: calc_nucleus (Actualizado)
# Realiza los calculos del nucleo y la ventana.

import math
import database as db
import utils

def _find_steel_data(steel_key):
    if steel_key in db.acero_electrico_db: return db.acero_electrico_db[steel_key]
    for data in db.acero_electrico_db.values():
        if data.get('designacion_antigua') == steel_key: return data
    raise KeyError("No se encontraron datos para el tipo de acero '{}'".format(steel_key))

def run(d):
    # --- Parametros Base ---
    if getattr(d, 'usar_valores_opcionales', False) and getattr(d, 'B_opcional', None):
        d.B_kgauss = d.B_opcional
    else:
        d.B_kgauss = getattr(d, 'B_man', None) or utils.get_promedio(db.densidad_flujo_db[utils.sel_clave(db.densidad_flujo_db, d.S)])
    d.B_tesla = d.B_kgauss / 10.0
    
    if getattr(d, 'usar_valores_opcionales', False) and getattr(d, 'J_opcional', None):
        d.J = d.J_opcional
    else:
        material = getattr(d, 'material_conductor', 'Cobre')
        d.J = utils.get_promedio(db.densidad_corriente_db[getattr(d, 'refrig', 'ONAN')][material])

    try:
        steel_data = _find_steel_data(getattr(d, 'acero', 'M-6'))
        if getattr(d, 'usar_valores_opcionales', False) and getattr(d, 'fa_opcional', None) is not None:
            d.fa_original = d.fa_opcional
        else:
            d.fa_original = steel_data.get('fa', 0.975)
        d.fa = float(d.fa_original)
        d.merma_id = steel_data['merma']
    except KeyError:
        raise ValueError("El tipo de acero '{}' no es valido.".format(getattr(d, 'acero', '')))

    # << CAMBIO: Se usa d.fases en lugar de d.tipo >>
    constante_flujo_key = 'trifasico_columnas' if getattr(d, 'fases', 3) == 3 else 'monofasico_columnas'
    if getattr(d, 'usar_valores_opcionales', False) and getattr(d, 'C_opcional', None):
        d.C = d.C_opcional
    else:
        d.C = getattr(d, 'C_man', None) or utils.get_promedio(db.constante_flujo_db[constante_flujo_key])

    # --- Tensiones de fase ---
    if getattr(d, 'fases', 3) == 3:
        d.conn1 = 'D' if 'D' in getattr(d, 'conn', 'Dyn').upper() else 'Y'
        d.conn2 = 'D' if getattr(d, 'conn', 'Dyn').upper()[1:].find('D') != -1 else 'Y'
        d.E1_fase = d.E1_linea if d.conn1 == 'D' else d.E1_linea / math.sqrt(3)
        d.E2_fase = d.E2_linea if d.conn2 == 'D' else d.E2_linea / math.sqrt(3)
    else:
        d.E1_fase, d.E2_fase = d.E1_linea, d.E2_linea

    # --- Constante Kc ---
    if getattr(d, 'usar_valores_opcionales', False) and getattr(d, 'Kc_opcional', None):
        d.Kc_original = d.Kc_opcional
    elif getattr(d, 'Kc_man', None):
        d.Kc_original = d.Kc_man
    else:
        E1_kv = d.E1_fase / 1000.0
        kc_n = 8 if d.S <= 10 else (10 if 10 < d.S <= 250 else 12)
        d.Kc_original = (kc_n / (30 + E1_kv)) * 1.15
    d.Kc = round(d.Kc_original, 2) if getattr(d, 'redondear_2_decimales', False) else round(d.Kc_original, 4)

    # --- Nucleo ---
    d.flujo_original = d.C * math.sqrt(d.S / d.f) * 1e6
    d.flujo_kilolineas = round(d.flujo_original / 1000, 1)
    d.flujo = d.flujo_original
    
    d.An = d.flujo / (d.B_kgauss * 1000)
    d.Ab = d.An / d.fa_original
    d.num_escalones = d._num_esc(d.Ab)
    
    if getattr(d, 'usar_valores_opcionales', False) and getattr(d, 'Kr_opcional', None):
        d.Kr_original = d.Kr_opcional
    else:
        db_kr_acero = db.coeficiente_kr_db.get(d.merma_id, {})
        db_kr_esc = db_kr_acero.get(d.num_escalones, {})
        d.Kr_original = db_kr_esc[utils.sel_clave(db_kr_esc, d.S)]
    d.Kr = float(d.Kr_original)
    
    d.D = 2 * math.sqrt(d.An / (math.pi * d.Kr))
    d.anchos = [factor * d.D for factor in db.dimensiones_escalones_db.get(d.num_escalones, [])]
    d.espesores, suma_e_previos = [], 0
    for a_i in d.anchos:
        e_i = (math.sqrt(d.D**2 - a_i**2) - suma_e_previos) / 2.0 if d.D**2 >= a_i**2 else 0
        d.espesores.append(e_i)
        suma_e_previos += 2 * e_i
    d.An_verificacion = 2 * d.fa_original * sum([d.anchos[i] * d.espesores[i] for i in range(len(d.anchos))])

    # --- Ventana ---
    S_VA, J_A_m2, An_m2 = d.S * 1000, d.J * 1e6, d.An * 1e-4
    constante_ventana = 2.22 if getattr(d, 'fases', 3) == 1 else 3.33
    Aw_m2 = S_VA / (constante_ventana * d.f * d.B_tesla * J_A_m2 * d.Kc * An_m2)
    d.Aw = Aw_m2 * 1e4
    d.b = math.sqrt(getattr(d, 'rel_rw', 3) * d.Aw)
    
    # << CAMBIO: Se calculan y guardan M, c, c_prima, g y L >>
    d.M = (d.Aw / d.b) + d.D if d.b > 0 else 0
    d.c = d.M - d.D
    a1 = d.anchos[0] if d.anchos else 0
    d.c_prima = d.M - a1
    d.g = d.An / a1 if a1 > 0 else 0
    d.L_monofasico = d.c + d.D + a1
    d.L_trifasico = 2 * d.c + 2 * d.D + a1