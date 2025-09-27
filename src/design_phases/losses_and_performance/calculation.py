# src/design_phases/losses_and_performance/calculation.py
# -*- coding: utf-8 -*-

from core import utils

def run(d):
    """Calcula las pérdidas y el rendimiento a plena carga."""
    # 1. Pérdidas en el Cobre (Pc específica en W/kg)
    d.Pc = 2.44 * (getattr(d, 'J', 0.0) ** 2)
    # Usamos el peso del cobre más detallado, calculado en la fase de devanados
    d.Wc = getattr(d, 'Qc_por_bobinado', 0.0) * d.Pc

    # 2. Pérdidas en el Hierro (Pf específica en W/kg)
    d.Pf = utils.get_specific_iron_loss(getattr(d, 'acero', None), getattr(d, 'B_kgauss', 0.0))
    d.Wf = getattr(d, 'Qr', 0.0) * d.Pf

    # 3. Rendimiento (η) a plena carga
    P_salida_W = getattr(d, 'S', 0.0) * 1000.0
    P_entrada_W = P_salida_W + d.Wc + d.Wf
    d.rendimiento = (P_salida_W / P_entrada_W) * 100.0 if P_entrada_W > 0 else 0.0