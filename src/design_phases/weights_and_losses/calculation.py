# src/design_phases/weights_and_losses/calculation.py
import math
from core import utils

def run(d):
    """
    Calcula los pesos del cobre y del hierro, las pérdidas y el rendimiento.
    """
    # --- CÁLCULOS DE PESO (EXISTENTES) ---
    if d.fases == 3:
        d.Qc = 0.021 * d.Kc * d.b * d.c * (2 * d.D + d.c)
    else:
        d.Qc = 0.014 * d.Kc * d.b * d.c * (2 * d.D + d.c)
    
    a1 = d.anchos[0] if d.anchos else d.D
    if d.fases == 3:
        d.Qr = 0.006 * d.Kr * (d.D**2) * (3 * d.b + 4 * d.c + 4 * d.D + 2 * a1)
    else:
        d.Qr = 0.012 * d.Kr * (d.D**2) * (d.b + d.c + d.D + a1)

    d.Q_total = d.Qc + d.Qr

    # --- NUEVO: CÁLCULOS DE PÉRDIDAS Y RENDIMIENTO ---
    
    # 1. Pérdidas en el Cobre (Wc)
    # Fórmula (1.65a): Pc = 2.44 * J^2 [W/kg]
    d.Pc = 2.44 * (d.J ** 2)
    # Fórmula (1.66): Wc = Qc * Pc [W]
    d.Wc = d.Qc * d.Pc

    # 2. Pérdidas en el Hierro (Wf)
    # Obtenemos Pf de la base de datos usando la nueva función de utils
    d.Pf = utils.get_specific_iron_loss(d.acero, d.B_kgauss)
    # Fórmula (1.67): Wf = Qr * Pf [W]
    d.Wf = d.Qr * d.Pf

    # 3. Rendimiento (η) a plena carga
    # Potencia de salida en Watts (asumiendo factor de potencia = 1)
    P_salida_W = d.S * 1000.0
    # Potencia de entrada = Potencia de salida + pérdidas totales
    P_entrada_W = P_salida_W + d.Wc + d.Wf
    # Fórmula (1.69): η = (P_salida / P_entrada) * 100
    d.rendimiento = (P_salida_W / P_entrada_W) * 100