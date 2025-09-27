# src/design_phases/nucleus_and_window/calculation.py
# -*- coding: utf-8 -*-

import math
from core import database as db, utils

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
    # Lógica de _calcular_parametros_base
    d.B_kgauss = d.B_man if d.B_man else utils.get_promedio(db.densidad_flujo_db[utils.sel_clave(db.densidad_flujo_db, d.S)])
    d.B_tesla = d.B_kgauss / 10.0
    d.J = utils.get_promedio(db.densidad_corriente_db[d.refrig]['Cobre'])
    
    # --- INICIO DE LA CORRECCIÓN ---
    # En lugar de acceder directamente al diccionario, usamos la función auxiliar
    # para encontrar los datos del acero de manera segura.
    try:
        steel_data = _find_steel_data(d.acero)
        d.fa = steel_data['fa']
        d.merma_id = steel_data['merma']
    except KeyError as e:
        # Propagamos el error con un mensaje más descriptivo si la función falla.
        raise ValueError(f"El tipo de acero '{d.acero}' no es válido o no se encuentra en la base de datos.") from e
    # --- FIN DE LA CORRECCIÓN ---
    
    tipo_nucleo_key = f"{d.tipo}_columnas"
    d.C = d.C_man if d.C_man else utils.get_promedio(db.constante_flujo_db[tipo_nucleo_key])
    
    # Lógica de _calcular_tensiones_fase (robusta frente a entradas inválidas)
    if d.fases == 3:
        conn_str = (d.conn or '').upper()
        if '-' in conn_str:
            parts = conn_str.split('-', 1)
            d.conn1, d.conn2 = parts[0], parts[1]
        elif conn_str:
            d.conn1 = d.conn2 = conn_str
        else:
            d.conn1, d.conn2 = 'D', 'YN'
        d.E1_fase = d.E1_linea if 'D' in d.conn1 else d.E1_linea / math.sqrt(3)
        d.E2_fase = d.E2_linea if 'D' in d.conn2 else d.E2_linea / math.sqrt(3)
    else:
        d.conn1 = d.conn2 = "Monofasico"
        d.E1_fase = d.E1_linea
        d.E2_fase = d.E2_linea

    # Lógica de _calcular_kc
    if d.Kc_man: d.Kc = d.Kc_man
    else:
        E1_kv = d.E1_fase / 1000.0
        kc_n = 8 if d.S <= 10 else (10 if 10 < d.S <= 250 else 12)
        d.Kc = (kc_n / (30 + E1_kv)) * 1.15

    # Lógica de _calcular_nucleo
    d.flujo = d.C * math.sqrt(d.S / d.f) * 1e6
    d.An = d.flujo / (d.B_kgauss * 1000)
    d.Ab = d.An / d.fa
    d.num_escalones = d._num_esc(d.Ab)
    db_kr_acero = db.coeficiente_kr_db.get(d.merma_id, {})
    db_kr_esc = db_kr_acero.get(d.num_escalones, {})
    d.Kr = db_kr_esc[utils.sel_clave(db_kr_esc, d.S)]
    d.D = 2 * math.sqrt(d.An / (math.pi * d.Kr))
    d.anchos = [factor * d.D for factor in db.dimensiones_escalones_db.get(d.num_escalones, [])]
    d.espesores = []
    suma_e_previos = 0
    for a_i in d.anchos:
        e_i = (math.sqrt(d.D**2 - a_i**2) - suma_e_previos) / 2.0
        d.espesores.append(e_i)
        suma_e_previos += 2 * e_i
    d.An_verificacion = 2 * d.fa * sum([d.anchos[i] * d.espesores[i] for i in range(len(d.anchos))])

    # Lógica de _calcular_ventana
    S_VA = d.S * 1000; J_A_m2 = d.J * 1e6; An_m2 = d.An * 1e-4
    Aw_m2 = (S_VA) / (3.33 * d.f * d.B_tesla * J_A_m2 * d.Kc * An_m2)
    d.Aw = Aw_m2 * 1e4
    d.b = math.sqrt(d.rel_rw * d.Aw)
    d.M = (d.Aw / d.b) + d.D
    d.c_prima = d.M - d.anchos[0] if d.anchos else None
    d.c = d.M - d.D