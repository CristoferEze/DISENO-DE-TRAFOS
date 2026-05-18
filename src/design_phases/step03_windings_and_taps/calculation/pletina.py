import math

def select_pletina(required_area, database):
    """Selecciona pletina mínima por exceso para un área requerida.

    Retorna un diccionario con keys: w, t, area, t_min
    """
    w_candidates = sorted(database.pletina_w_std)
    t_list = sorted(database.pletina_t_std)

    try:
        t_min_from_eq = math.sqrt(required_area / 3.0)
    except Exception:
        t_min_from_eq = 0.0

    # Redondear t_min al incremento definido en la base de datos si está disponible
    try:
        step = float(getattr(database, 'pletina_thickness_step_mm', 0.05))
        if step > 0:
            t_min_rounded = math.ceil(t_min_from_eq / step) * step
        else:
            t_min_rounded = t_min_from_eq
    except Exception:
        t_min_rounded = t_min_from_eq

    # Regla nueva solicitada:
    # 1) Calcular t_min = sqrt(s2/3)
    # 2) Escoger el t estándar más cercano a t_min (si empate, preferir el mayor -> 'redondeado hacia arriba')
    # 3) Con ese t, seleccionar el menor w estándar tal que w * t >= required_area
    # 4) Si ningún w cumple para ese t, probar con el siguiente t mayor en la lista (iterar hacia arriba)
    # 5) Si no se encuentra nada, fallback a máximos disponibles

    # Manejo de listas vacías
    if not t_list or not w_candidates:
        w_std = max(w_candidates) if w_candidates else 0.0
        t_std = max(t_list) if t_list else 0.0
        area_std = w_std * t_std
    else:
        # 2) Seleccionar t = el primer valor estándar >= t_min_from_eq (redondeo hacia arriba).
        t_std = None
        for t in t_list:
            if t >= t_min_from_eq:
                t_std = t
                break
        # Si no hay t >= t_min_from_eq, usar el mayor disponible (fallback)
        if t_std is None:
            t_std = t_list[-1]

        # 3) Con ese t, buscar el menor w tal que w * t >= required_area. Si no hay, intentar con t mayores.
        w_std = None
        try:
            start_idx = t_list.index(t_std)
        except ValueError:
            start_idx = 0

        found = False
        for t in t_list[start_idx:]:
            for w in w_candidates:
                if w * t >= required_area:
                    w_std = w
                    t_std = t
                    found = True
                    break
            if found:
                break

        # 4) fallback si aún no hay selección: tomar máximos disponibles
        if w_std is None:
            w_std = w_candidates[-1]
            t_std = t_list[-1]
        area_std = w_std * t_std

        return {
        'w': float(w_std),
        't': float(t_std),
        'area': float(area_std),
        # Retornar t_min redondeado para mostrar el valor práctico de espesor mínimo
        't_min': float(t_min_rounded)
    }
