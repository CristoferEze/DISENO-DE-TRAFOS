import sys
import os
from pathlib import Path

# Asegurar que la carpeta 'src' esté en sys.path para que imports como
# `design_phases` o `src.core` funcionen independientemente del cwd.
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = REPO_ROOT / 'src'
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from src.core.engine import DisenoTransformador


if __name__ == '__main__':
    # Crear diseño con valores por defecto (sin UI)
    d = DisenoTransformador()
    d.ejecutar_calculo_completo()

    # Imprimir resultados clave
    keys = [
        'S', 'E1_linea', 'E2_linea', 'fases',
        'N2_fase', 'N1_fase', 'Ne_cb2', 'Nc_b2', 'Ne_cb1', 'Nc_b1',
        'Lb1', 'Lb2', 'Qb1', 'Qb2', 'Qc_por_bobinado', 'Qc_total', 'Qr'
    ]
    for k in keys:
        print(f"{k}: {getattr(d, k, None)}")

    print('\nPesos por metro usados:')
    print('peso_conductor_primario_kg_m =', getattr(d, 'peso_conductor_primario_kg_m', None))
    print('peso_conductor_secundario_kg_m =', getattr(d, 'peso_conductor_secundario_kg_m', None))
