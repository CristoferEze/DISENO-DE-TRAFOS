# -*- coding: utf-8 -*-
# ==================================================================
# CONSTANTES Y BASES DE DATOS DEL DISEÑO
# Fuentes: Guía de Diseño de Transformadores y ANEXO N° 1
# ==================================================================
#
# (Este módulo ya es compatible y no requiere cambios)
#

# ------------------------------------------------------------------
# DATOS EXTRAÍDOS DEL "ANEXO N° 1" Y FUSIONADOS
# ------------------------------------------------------------------

# Tabla 1: Densidad de Flujo Magnético (B) en kgauss
# Fuente: ANEXO N° 1, Tabla 1
densidad_flujo_db = {
    1: (11, 13),
    10: (13, 16),
    100: (16, 17),
    1000: (17, 18),
    5000: (17.5, 18)
}

# Tabla 2: Propiedades de Acero Eléctrico al Silicio (CRGO)
# Fuente: Fusión de la base de datos existente y ANEXO N° 1, Tabla 2
# Combina 'fa', 'merma', y pérdidas específicas (W/kg).
acero_electrico_db = {
    'M-3': {
        'designacion_antigua': '23M3', 'espesor_mm': 0.23, 'fa': 0.960,
        'merma': 'Merma 4.0% (23M3)', 'codigo_grado': '23M3',
        'perdidas_w_kg_15k': 0.87, 'perdidas_w_kg_16k': 1.03, 'perdidas_w_kg_17k': 1.28
    },
    'M-4': {
        'designacion_antigua': '27M4', 'espesor_mm': 0.27, 'fa': 0.965,
        'merma': 'Merma 3.5% (27M4)', 'codigo_grado': '27M4',
        'perdidas_w_kg_15k': 1.02, 'perdidas_w_kg_16k': 1.20, 'perdidas_w_kg_17k': 1.47
    },
    'M-5': {
        'designacion_antigua': '30M5', 'espesor_mm': 0.30, 'fa': 0.970,
        'merma': 'Merma 3.0% (30M5)', 'codigo_grado': '30M5',
        'perdidas_w_kg_15k': 1.11, 'perdidas_w_kg_16k': 1.30, 'perdidas_w_kg_17k': 1.57
    },
    'M-6': {
        'designacion_antigua': '35M6', 'espesor_mm': 0.35, 'fa': 0.975,
        'merma': 'Merma 2.5% (35M6)', 'codigo_grado': '35M6',
        'perdidas_w_kg_15k': 1.28, 'perdidas_w_kg_16k': 1.51, 'perdidas_w_kg_17k': 1.81
    }
}

# Tabla 3: Densidad de Corriente (J) en A/mm^2 por tipo de enfriamiento
# Fuente: ANEXO N° 1, Tabla 3
densidad_corriente_db = {
    'AN':   {'Cobre': (1.2, 2.0), 'Aluminio': (0.8, 1.3)},
    'AF':   {'Cobre': (2.0, 2.5), 'Aluminio': (1.3, 1.7)},
    'ONAN': {'Cobre': (3.0, 4.0), 'Aluminio': (1.7, 2.7)},
    'ONAF': {'Cobre': (3.5, 4.5), 'Aluminio': (2.3, 3.0)},
    'ODAF': {'Cobre': (4.0, 5.0), 'Aluminio': (2.7, 3.3)}
}

# ------------------------------------------------------------------
# DATOS DE LA GUÍA DE DISEÑO (EXISTENTES Y CONSERVADOS)
# ------------------------------------------------------------------

# Conexiones Normalizadas (para validación en la UI)
conexiones_normalizadas_db = [
    'Dyn1', 'Dy0', 'Ynd5', 'Ynd11', 'Ynyn6', 'Dd6',
    'Dyn5', 'Yd1', 'Yd7', 'Yy0', 'Dd0', 'Dd8',
    'Dyn7', 'Ynd1', 'Ynd7', 'Ynyn0', 'Dd2', 'Dd10',
    'Dyn11', 'Yd5', 'Yd11', 'Yy6', 'Dd4'
]

# Coeficiente de Plenitud del Hierro (Kr)
# Fuente: Tabla 2.3 de la guía de diseño
coeficiente_kr_db = {
    'Sin merma': {
        1: {5: 0.637}, 2: {15: 0.787}, 3: {50: 0.851},
        4: {200: 0.887}, 5: {500: 0.908}, 6: {750: 0.924}
    },
    'Merma 2.5% (35M6)': {
        1: {5: 0.621}, 2: {15: 0.767}, 3: {50: 0.830},
        4: {200: 0.865}, 5: {500: 0.885}, 6: {750: 0.900}
    },
    'Merma 3.0% (30M5)': {
        1: {5: 0.618}, 2: {15: 0.763}, 3: {50: 0.825},
        4: {200: 0.860}, 5: {500: 0.881}, 6: {750: 0.896}
    },
    'Merma 3.5% (27M4)': {
        1: {5: 0.615}, 2: {15: 0.759}, 3: {50: 0.821},
        4: {200: 0.856}, 5: {500: 0.876}, 6: {750: 0.891}
    },
    'Merma 4.0% (23M3)': {
        1: {5: 0.612}, 2: {15: 0.756}, 3: {50: 0.817},
        4: {200: 0.852}, 5: {500: 0.872}, 6: {750: 0.887}
    }
}

# Constante de Flujo Magnético (C)
# Fuente: Tabla 3.2 de la guía de diseño
constante_flujo_db = {
    'monofasico_columnas': (1.2, 1.9),
    'monofasico_acorazado': (3.0, 4.0),
    'trifasico_columnas': (1.0, 1.6),
    'trifasico_acorazado': (2.0, 3.0)
}

# Dimensiones de los Escalones como factor del Diámetro (D)
# Fuente: Tabla 2.4 de la guía de diseño
dimensiones_escalones_db = {
    1: [0.707],
    2: [0.850, 0.526],
    3: [0.906, 0.707, 0.424],
    4: [0.934, 0.796, 0.605, 0.356],
    5: [0.950, 0.846, 0.707, 0.534, 0.313],
    6: [0.959, 0.875, 0.768, 0.640, 0.488, 0.281]
}

# --- NUEVO: Tabla de Propiedades de Conductores de Cobre AWG ---
# Fuente: tabla de calibres AWG con diámetro, sección y peso por metro (g/m)
# Clave: Calibre AWG (str), Valor: diccionario con propiedades
awg_conductors_db = {
    '250 MCM': {'diametro_mm': 12.70, 'seccion_mm2': 126.6, 'peso_g_m': 1126},
    '4/0': {'diametro_mm': 11.70, 'seccion_mm2': 107.4, 'peso_g_m': 953},
    '3/0': {'diametro_mm': 10.40, 'seccion_mm2': 85.03, 'peso_g_m': 756},
    '2/0': {'diametro_mm': 9.27, 'seccion_mm2': 67.4, 'peso_g_m': 600},
    '1/0': {'diametro_mm': 8.26, 'seccion_mm2': 53.5, 'peso_g_m': 476},
    '1':   {'diametro_mm': 7.35, 'seccion_mm2': 42.4, 'peso_g_m': 377},
    '2':   {'diametro_mm': 6.54, 'seccion_mm2': 33.6, 'peso_g_m': 299},
    '3':   {'diametro_mm': 5.83, 'seccion_mm2': 26.6, 'peso_g_m': 237},
    '4':   {'diametro_mm': 5.18, 'seccion_mm2': 21.1, 'peso_g_m': 188},
    '5':   {'diametro_mm': 4.62, 'seccion_mm2': 16.8, 'peso_g_m': 149},
    '6':   {'diametro_mm': 4.11, 'seccion_mm2': 13.3, 'peso_g_m': 118},
    '7':   {'diametro_mm': 3.66, 'seccion_mm2': 10.5, 'peso_g_m': 93.8},
    '8':   {'diametro_mm': 3.25, 'seccion_mm2': 8.3, 'peso_g_m': 74.38},
    '9':   {'diametro_mm': 2.89, 'seccion_mm2': 6.59, 'peso_g_m': 58.6},
    '10':  {'diametro_mm': 2.59, 'seccion_mm2': 5.27, 'peso_g_m': 46.9},
    '11':  {'diametro_mm': 2.30, 'seccion_mm2': 4.17, 'peso_g_m': 37.1},
    '12':  {'diametro_mm': 2.05, 'seccion_mm2': 3.31, 'peso_g_m': 29.4},
    '13':  {'diametro_mm': 1.83, 'seccion_mm2': 2.63, 'peso_g_m': 23.4},
    '14':  {'diametro_mm': 1.63, 'seccion_mm2': 2.08, 'peso_g_m': 18.5},
    '15':  {'diametro_mm': 1.45, 'seccion_mm2': 1.65, 'peso_g_m': 14.7},
    '16':  {'diametro_mm': 1.29, 'seccion_mm2': 1.31, 'peso_g_m': 11.6},
    '17':  {'diametro_mm': 1.15, 'seccion_mm2': 1.04, 'peso_g_m': 9.24},
    '18':  {'diametro_mm': 1.02, 'seccion_mm2': 0.821, 'peso_g_m': 7.32},
    '19':  {'diametro_mm': 0.91, 'seccion_mm2': 0.654, 'peso_g_m': 5.8},
    '20':  {'diametro_mm': 0.81, 'seccion_mm2': 0.517, 'peso_g_m': 4.61},
    '21':  {'diametro_mm': 0.72, 'seccion_mm2': 0.411, 'peso_g_m': 3.66},
    '22':  {'diametro_mm': 0.64, 'seccion_mm2': 0.324, 'peso_g_m': 2.88},
    '23':  {'diametro_mm': 0.57, 'seccion_mm2': 0.259, 'peso_g_m': 2.31},
    '24':  {'diametro_mm': 0.51, 'seccion_mm2': 0.205, 'peso_g_m': 1.81},
    '25':  {'diametro_mm': 0.45, 'seccion_mm2': 0.162, 'peso_g_m': 1.44},
    '26':  {'diametro_mm': 0.40, 'seccion_mm2': 0.128, 'peso_g_m': 1.14},
    '27':  {'diametro_mm': 0.36, 'seccion_mm2': 0.102, 'peso_g_m': 0.908},
    '28':  {'diametro_mm': 0.32, 'seccion_mm2': 0.080, 'peso_g_m': 0.715},
    '29':  {'diametro_mm': 0.29, 'seccion_mm2': 0.065, 'peso_g_m': 0.575},
    '30':  {'diametro_mm': 0.25, 'seccion_mm2': 0.0507, 'peso_g_m': 0.450},
    '31':  {'diametro_mm': 0.23, 'seccion_mm2': 0.0401, 'peso_g_m': 0.357},
    '32':  {'diametro_mm': 0.20, 'seccion_mm2': 0.0324, 'peso_g_m': 0.288},
    '33':  {'diametro_mm': 0.18, 'seccion_mm2': 0.0255, 'peso_g_m': 0.227},
    '34':  {'diametro_mm': 0.16, 'seccion_mm2': 0.0201, 'peso_g_m': 0.179},
    '35':  {'diametro_mm': 0.14, 'seccion_mm2': 0.0190, 'peso_g_m': 0.141},
    '36':  {'diametro_mm': 0.13, 'seccion_mm2': 0.0127, 'peso_g_m': 0.113},
    '37':  {'diametro_mm': 0.11, 'seccion_mm2': 0.0103, 'peso_g_m': 0.091},
    '38':  {'diametro_mm': 0.10, 'seccion_mm2': 0.0081, 'peso_g_m': 0.072},
    '39':  {'diametro_mm': 0.09, 'seccion_mm2': 0.0062, 'peso_g_m': 0.055},
    '40':  {'diametro_mm': 0.08, 'seccion_mm2': 0.0049, 'peso_g_m': 0.043}
}

# Alias público para compatibilidad con la UI (uso: from core.database import conexiones_normalizadas)
conexiones_normalizadas = conexiones_normalizadas_db