# src/design_phases/weights_and_losses/calculation.py
import math
from core import utils

def run(d):
    """
    Calcula los pesos del cobre y del hierro, las pérdidas y el rendimiento.
    """
    # --- CÁLCULO DEL PESO DEL COBRE (sin cambios) ---
    if d.fases == 3:
        d.Qc = 0.021 * d.Kc * d.b * d.c * (2 * d.D + d.c)
    else:
        d.Qc = 0.014 * d.Kc * d.b * d.c * (2 * d.D + d.c)

    # --- NUEVO: Cálculo Preciso del Peso del Hierro (Qr) usando dimensiones del yugo/columnas ---
    # Asegurarse de tener a1 y las longitudes L calculadas; usar fallback razonable si faltan.
    a1 = d.anchos[0] if getattr(d, 'anchos', None) else getattr(d, 'D', 0)
    # Densidad del hierro en kg/cm^3 (7.65 g/cm^3)
    rho_hierro_kg_cm3 = 7.65 / 1000.0

    if d.fases == 3:
        # Volumen = (3 columnas de área An y alto b) + (2 yugos de área An y largo L_trifasico)
        volumen_hierro = (3 * d.An * d.b) + (2 * d.An * getattr(d, 'L_trifasico', (2 * d.c + 2 * d.D + a1)))
        d.Qr = volumen_hierro * rho_hierro_kg_cm3
    else:
        # Monofásico: Volumen = (2 columnas de área An y alto b) + (2 yugos de área An y largo L_monofasico)
        volumen_hierro = (2 * d.An * d.b) + (2 * d.An * getattr(d, 'L_monofasico', (d.c + d.D + a1)))
        d.Qr = volumen_hierro * rho_hierro_kg_cm3

    d.Q_total = d.Qc + d.Qr

    # --- CÁLCULOS DE PÉRDIDAS Y RENDIMIENTO ---
    # 1. Pérdidas en el Cobre (Wc)
    d.Pc = 2.44 * (d.J ** 2)
    d.Wc = d.Qc * d.Pc

    # 2. Pérdidas en el Hierro (Wf)
    d.Pf = utils.get_specific_iron_loss(d.acero, d.B_kgauss)
    d.Wf = d.Qr * d.Pf

    # 3. Rendimiento (η) a plena carga
    P_salida_W = d.S * 1000.0
    P_entrada_W = P_salida_W + d.Wc + d.Wf
    d.rendimiento = (P_salida_W / P_entrada_W) * 100 if P_entrada_W > 0 else 0