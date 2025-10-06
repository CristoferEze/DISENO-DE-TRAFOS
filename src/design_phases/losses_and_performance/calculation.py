# src/design_phases/losses_and_performance/calculation.py
# -*- coding: utf-8 -*-

from core import utils

def run(d):
    """Calcula las pérdidas y el rendimiento a plena carga.

    Notas:
    - Para las pérdidas se usan fórmulas empíricas proporcionadas por el usuario:
        Q_c = 0.021 * Kc * b * c * (2*D + c)
        Q_f = 0.006 * Kf * D^2 * (3*b + 4*c + 5.87*D)
      donde Q_c y Q_f son masas (kg) según las unidades esperadas (b, c, D en cm).
    - Se mantiene el cálculo físico detallado del peso del cobre en la fase de devanados;
      aquí solo se usan las expresiones empíricas para calcular las pérdidas.
    - IMPORTANTE: La fórmula empírica Q_c está definida para el transformador trifásico,
      por lo que no debe multiplicarse por 3 adicionalmente.
    """

    # 1. Pérdidas en el Cobre (Pc específica en W/kg)
    # Usar valor manual si está disponible, si no calcular con fórmula
    if getattr(d, 'usar_valores_opcionales', False) and getattr(d, 'Pc_manual', None) is not None:
        d.Pc = d.Pc_manual
        d.Pc_calculation_method = "Valor manual"
    else:
        d.Pc = 2.44 * (getattr(d, 'J', 0.0) ** 2)
        d.Pc_calculation_method = "Fórmula empírica (2.44 × J²)"

    # Empírica para masa de cobre usada en el cálculo de pérdidas
    Kc_val = getattr(d, 'Kc', 1.0)
    b_val = getattr(d, 'b', 0.0)
    c_val = getattr(d, 'c', 0.0)
    D_val = getattr(d, 'D', 0.0)

    # Qc empírico (kg) — la fórmula ya corresponde a transformador trifásico (no multiplicar por 3)
    try:
        # Constante según tipo: Monofásico: 0.014, Trifásico: 0.021
        constante_Qc = 0.014 if getattr(d, 'fases', 3) == 1 else 0.021
        Qc_emp = constante_Qc * float(Kc_val) * float(b_val) * float(c_val) * (2.0 * float(D_val) + float(c_val))
    except Exception:
        Qc_emp = 0.0
    d.Qc_empirical_por_formula = Qc_emp
    # No multiplicar por 3: la fórmula se aplica directamente para el transformador (trifásico)
    d.Qc_empirical_total = Qc_emp
    
    # CORREGIDO: Selección de la masa de cobre que se usará para calcular pérdidas:
    # - Si es monofásico, usar SIEMPRE el cálculo físico (d.Qc_total)
    # - Si es trifásico, usar SIEMPRE la fórmula empírica (Qc_emp)
    if getattr(d, 'fases', 3) == 1:
        mass_copper_for_losses = getattr(d, 'Qc_total', getattr(d, 'Qc_por_bobinado', 0.0))
        d.copper_calculation_method = "Cálculo manual (monofásico)"
    else:
        mass_copper_for_losses = d.Qc_empirical_por_formula
        d.copper_calculation_method = "Fórmula empírica (trifásico)"
    
    d.Qc_used_for_losses = mass_copper_for_losses
    
    # Pérdidas en W debidas al cobre (W = masa [kg] * Pc [W/kg])
    d.Wc = mass_copper_for_losses * d.Pc

    # 2. Pérdidas en el Hierro (Pf específica en W/kg)
    # Prioridad: 1) Valor manual, 2) Valor opcional, 3) Valor de tabla según acero
    if getattr(d, 'usar_valores_opcionales', False) and getattr(d, 'Pf_manual', None) is not None:
        d.Pf = d.Pf_manual
        d.Pf_calculation_method = "Valor manual"
    elif getattr(d, 'usar_valores_opcionales', False) and getattr(d, 'Pf_opcional', 0):
        d.Pf = d.Pf_opcional
        d.Pf_calculation_method = "Valor opcional de tabla"
    else:
        d.Pf = utils.get_specific_iron_loss(getattr(d, 'acero', None), getattr(d, 'B_kgauss', 0.0))
        d.Pf_calculation_method = f"Valor de tabla para acero {getattr(d, 'acero', '?')}"

    # CORREGIDO: Qf (masa de hierro aplicable a pérdidas)
    # - Si es monofásico, usar SIEMPRE el cálculo físico del peso del hierro
    # - Si es trifásico, usar SIEMPRE la fórmula empírica
    if getattr(d, 'fases', 3) == 1:
        # Para monofásico: usar el peso del hierro calculado físicamente
        d.Qf_empirical = getattr(d, 'Qr', 0.0)  # Peso del hierro calculado
        d.Kf_used_for_Qf = "N/A (cálculo manual)"
        d.iron_calculation_method = "Cálculo manual (monofásico)"
    else:
        # Para trifásico: usar fórmula empírica
        kf_for_Qf = getattr(d, 'Kr_original', None)
        if kf_for_Qf is None:
            kf_for_Qf = getattr(d, 'Kr', 1.0)
        
        try:
            # No redondear kf_for_Qf ni otros intermedios al calcular Qf_emp
            # Constante según tipo: Monofásico: 0.012, Trifásico: 0.006
            constante_Qf = 0.012 if getattr(d, 'fases', 3) == 1 else 0.006
            Qf_emp = constante_Qf * float(kf_for_Qf) * (float(D_val) ** 2) * (3.0 * float(b_val) + 4.0 * float(c_val) + 5.87 * float(D_val))
        except Exception:
            Qf_emp = 0.0
        
        d.Qf_empirical = Qf_emp
        d.Kf_used_for_Qf = kf_for_Qf
        d.iron_calculation_method = "Fórmula empírica (trifásico)"

    # Pérdidas en W debidas al hierro
    d.Wf = d.Qf_empirical * d.Pf

    # 3. Rendimiento (η) a plena carga usando las pérdidas empíricas calculadas
    P_salida_W = getattr(d, 'S', 0.0) * 1000.0
    P_entrada_W = P_salida_W + getattr(d, 'Wc', 0.0) + getattr(d, 'Wf', 0.0)
    d.rendimiento = (P_salida_W / P_entrada_W) * 100.0 if P_entrada_W > 0 else 0.0

    # Guardar valores para trazabilidad
    d.Wc_empirical = getattr(d, 'Wc', 0.0)
    d.Wf_empirical = getattr(d, 'Wf', 0.0)
    d.Qc_used_for_losses = d.Qc_empirical_total
    d.Qf_used_for_losses = d.Qf_empirical