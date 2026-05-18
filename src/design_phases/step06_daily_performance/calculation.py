# src/design_phases/daily_performance/calculation.py
def run(d):
    """Calcula la energía de salida y las pérdidas de energía en un ciclo de 24h."""
    d.energia_salida_total = 0.0
    d.energia_perdida_cobre_total = 0.0
    d.energia_perdida_hierro_total = 0.0
    d.detalles_ciclo = []

    if not getattr(d, 'ciclo_carga', None):
        return  # No hay ciclo de carga para calcular

    # Pérdidas en el hierro son constantes durante 24h
    # d.Wf está en W, convertir a kW antes de multiplicar por horas
    try:
        d.energia_perdida_hierro_total = (d.Wf / 1000.0) * 24.0
    except Exception:
        d.energia_perdida_hierro_total = 0.0

    for carga_frac, horas in d.ciclo_carga:
        # Energía de salida en este intervalo (kW * h)
        P_salida_kW = d.S * carga_frac  # d.S está en kVA, asumir FP=1 => kW
        energia_salida = P_salida_kW * horas
        d.energia_salida_total += energia_salida

        # Pérdidas de energía en el cobre en este intervalo (W -> kW)
        Wc_variable_kW = (getattr(d, 'Wc', 0.0) / 1000.0) * (carga_frac ** 2)
        energia_perdida_cobre = Wc_variable_kW * horas
        d.energia_perdida_cobre_total += energia_perdida_cobre

        d.detalles_ciclo.append({
            'carga_frac': carga_frac,
            'horas': horas,
            'energia_salida_kwh': energia_salida,
            'energia_perdida_cu_kwh': energia_perdida_cobre
        })

    # Energía total perdida y rendimiento diario
    d.energia_perdida_total = d.energia_perdida_cobre_total + d.energia_perdida_hierro_total
    energia_entrada_total = d.energia_salida_total + d.energia_perdida_total
    d.rendimiento_diario = (d.energia_salida_total / energia_entrada_total) * 100.0 if energia_entrada_total > 0 else 0.0