# -*- coding: utf-8 -*-
# ==================================================================
# CONSTANTES Y BASES DE DATOS DEL DISEÑO
# Fuentes: Guía de Diseño de Transformadores y ANEXO N° 1
# ==================================================================

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

# Alias público para compatibilidad con la UI (uso: from core.database import conexiones_normalizadas)
conexiones_normalizadas = conexiones_normalizadas_db