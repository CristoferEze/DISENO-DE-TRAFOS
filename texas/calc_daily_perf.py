# Modulo: calc_daily_perf
# Calcula el rendimiento y las perdidas en un ciclo diario.

def run(d):
    """Calcula la energia de salida y las perdidas en un ciclo de 24h."""
    d.energia_salida_total = 0.0
    d.energia_perdida_cobre_total = 0.0
    d.energia_perdida_hierro_total = 0.0
    d.detalles_ciclo = []
    d.rendimiento_diario = 0.0

    ciclo_carga = getattr(d, 'ciclo_carga', None)
    if not ciclo_carga: return

    Wf_watts = getattr(d, 'Wf', 0.0)
    d.energia_perdida_hierro_total = (Wf_watts / 1000.0) * 24.0

    for carga_frac, horas in ciclo_carga:
        S_nominal_kVA = getattr(d, 'S', 0.0)
        P_salida_kW = S_nominal_kVA * carga_frac
        energia_salida = P_salida_kW * horas
        d.energia_salida_total += energia_salida

        Wc_watts = getattr(d, 'Wc', 0.0)
        Wc_variable_kW = (Wc_watts / 1000.0) * (carga_frac ** 2)
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
    
    if energia_entrada_total > 0:
        d.rendimiento_diario = (d.energia_salida_total / energia_entrada_total) * 100.0
    else:
        d.rendimiento_diario = 0.0