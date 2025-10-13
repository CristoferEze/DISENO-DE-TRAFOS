# Modulo: calc_losses (Actualizado)
# Calcula las perdidas y el rendimiento a plena carga.

import utils

def run(d):
    fases = getattr(d, 'fases', 3)
    
    # 1. Perdidas en el Cobre
    if getattr(d, 'usar_valores_opcionales', False) and getattr(d, 'Pc_manual', None) is not None:
        d.Pc = d.Pc_manual
    else:
        d.Pc = 2.44 * (getattr(d, 'J', 0.0) ** 2)

    if fases == 1:
        mass_copper = getattr(d, 'Qc_total', 0.0)
    else:
        constante_Qc = 0.021
        Kc = getattr(d, 'Kc', 1.0)
        b = getattr(d, 'b', 0.0)
        c = getattr(d, 'c', 0.0)
        D = getattr(d, 'D', 0.0)
        mass_copper = constante_Qc * float(Kc) * float(b) * float(c) * (2.0 * float(D) + float(c))
    d.Qc_used_for_losses = mass_copper
    d.Wc = mass_copper * d.Pc

    # 2. Perdidas en el Hierro
    # << CAMBIO: Se anade la logica para d.Pf_opcional >>
    if getattr(d, 'usar_valores_opcionales', False) and getattr(d, 'Pf_opcional', None) is not None:
        d.Pf = d.Pf_opcional
    elif getattr(d, 'usar_valores_opcionales', False) and getattr(d, 'Pf_manual', None) is not None:
        d.Pf = d.Pf_manual
    else:
        d.Pf = utils.get_specific_iron_loss(getattr(d, 'acero', None), getattr(d, 'B_kgauss', 0.0))

    if fases == 1:
        mass_iron = getattr(d, 'Qr', 0.0)
    else:
        kf = getattr(d, 'Kr_original', getattr(d, 'Kr', 1.0))
        constante_Qf = 0.006
        D = getattr(d, 'D', 0.0)
        b = getattr(d, 'b', 0.0)
        c = getattr(d, 'c', 0.0)
        mass_iron = constante_Qf * float(kf) * (D**2) * (3.0*b + 4.0*c + 5.87*D)
    d.Qf_used_for_losses = mass_iron
    d.Wf = mass_iron * d.Pf

    # 3. Rendimiento
    P_salida_W = getattr(d, 'S', 0.0) * 1000.0
    P_entrada_W = P_salida_W + getattr(d, 'Wc', 0.0) + getattr(d, 'Wf', 0.0)
    d.rendimiento = (P_salida_W / P_entrada_W) * 100.0 if P_entrada_W > 0 else 0.0