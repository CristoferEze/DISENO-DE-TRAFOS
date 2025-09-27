# src/core/utils.py
# -*- coding: utf-8 -*-

from . import database as db

def get_promedio(v):
    return (v[0] + v[1]) / 2

def sel_clave(d, val):
    return min([k for k in d if k >= val] or [max(d)])

def f_dec(v):
    return "{:.2f}".format(v)

def f_int(v):
    return "{}".format(int(v))

def get_specific_iron_loss(steel_key, b_kgauss):
    """
    Obtiene las pérdidas específicas en el hierro (Pf en W/kg) de la base de datos,
    seleccionando el valor correspondiente a la densidad de flujo (B) más cercana
    entre 15, 16 y 17 kGauss.
    """
    # Primero, encontrar la entrada correcta para el acero
    steel_data = None
    if steel_key in db.acero_electrico_db:
        steel_data = db.acero_electrico_db[steel_key]
    else:
        for data in db.acero_electrico_db.values():
            if data.get('designacion_antigua') == steel_key:
                steel_data = data
                break

    if not steel_data:
        raise ValueError(f"No se encontraron datos para el acero '{steel_key}'")

    # Obtener las pérdidas para 15, 16 y 17 kGauss
    losses = {
        15: steel_data.get('perdidas_w_kg_15k', 0),
        16: steel_data.get('perdidas_w_kg_16k', 0),
        17: steel_data.get('perdidas_w_kg_17k', 0)
    }

    # Encontrar a qué valor (15, 16, o 17) es más cercano b_kgauss
    closest_b = min(losses.keys(), key=lambda k: abs(k - b_kgauss))

    return losses[closest_b]