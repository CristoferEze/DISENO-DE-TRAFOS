
### **Guía de Diseño de Transformadores (Revisada)**

Este documento detalla los criterios y pasos para el diseño de transformadores de distribución, basándose en la clasificación, materiales y fórmulas de cálculo.

### **Parte 1: Reglas para la Selección de Transformadores por Sector Típico en Perú**




## Conexions Normalizadas

Dyn1	Dy0	Ynd5	Ynd11	Ynyn6	Dd6
Dyn5	Yd1	Yd7	Yy0	Dd0	Dd8
Dyn7	Ynd1	Ynd7	Ynyn0	Dd2	Dd10
Dyn11	Yd5	Yd11	Yy6	Dd4	

## Criterios de Diseño

### **Paso 1: Clasificación del Transformador**

La primera etapa consiste en clasificar el transformador según sus características fundamentales.

#### 1.1. Clasificación según Niveles de Tensión

| Tipo                | Rango de Tensión (Vn) | Tensiones Nominales Comunes                                          |
| :------------------ | :-------------------- | :------------------------------------------------------------------- |
| **Media Tensión (MT)** | 1kV < Vn ≤ 35kV       | 10 kV, 13.2 kV, 13.2/7.62 kV, 20 kV, 22.9 kV, 22.9/13.2 kV, 33/19.05 kV |
| **Baja Tensión (BT)**  | Vn ≤ 1kV              | 220 V, 380/220 V, 440/220 V                                          |

#### 1.2. Clasificación según Capacidad Nominal (S)

Para transformadores de distribución, el rango de potencia se define como **5 kVA < S < 500 kVA**.

| Tipo        | Rango de Potencia   | Potencias Estándar (kVA)          |
| :---------- | :------------------ | :-------------------------------- |
| **Monofásico** | 5 kVA < S < 100 kVA | 5, 10, 15, 25, 37.5, 50, 75      |
| **Trifásico**  | 15 kVA < S < 500 kVA| 25, 37.5, 50, 75, 100, 160, 200, 250 |

#### 1.3. Clasificación según Fases y Tipo de Conexión

| Tipo de Transformador | Conexión Media Tensión | Tensión Nominal (MT) | Conexión Baja Tensión | Tensión Nominal (BT)     |
| :-------------------- | :--------------------- | :------------------- | :-------------------- | :----------------------- |
| **Monofásico**          | Fase-Fase              | 10 kV                | Fase-Fase             | 0.230 kV                 |
|                       | Fase-Neutro            | 13.2 kV              | Fase-Fase             | 0.46 kV                  |
|                       |                        |                      | Fase-Neutro           | 0.23 kV                  |
| **Trifásico**           | Triángulo              | 10 kV                | Triángulo             | 0.231 kV                 |
|                       | Estrella               | 22.9 kV              | Estrella con Neutro   | 0.400 kV / 0.231 kV      |

### **Paso 2: Selección de Materiales y Parámetros del Núcleo**

#### 2.1. Espesor de Laminación y Factor de Apilamiento (fa)

El factor de apilamiento `fa` depende del grado y espesor del acero al silicio utilizado.

| Código de Grado | Espesor de Laminación | Factor de Apilamiento (fa) |
| :-------------- | :-------------------- | :------------------------- |
| **35M6**        | 0.35 mm               | 0.975                      |
| **30M5**        | 0.30 mm               | 0.970                      |
| **27M4**        | 0.27 mm               | 0.965                      |
| **23M3**        | 0.23 mm               | 0.960                      |

#### 2.2. Número de Escalones del Núcleo

El número de escalones se elige en función del área de la sección bruta del núcleo para optimizar el espacio.

| Área de la Sección Bruta (cm²) | Número de Escalones |
| :----------------------------- | :------------------ |
| < 30                           | 1                   |
| [30 - 50)                      | 2                   |
| [50 - 70)                      | 3                   |
| [70 - 150)                     | 4                   |
| [150 - 450)                    | 5                   |
| [450 - 800)                    | 6                   |

#### 2.3. Coeficiente de Plenitud del Hierro (Kr)

Este coeficiente, también conocido como factor de utilización del núcleo, depende de la potencia, el número de escalones y el tipo de laminación (asociado a la merma).

| Potencia (kVA)        | **5** | **15** | **50** | **200** | **500** | **750** |
| :-------------------- | :---: | :----: | :----: | :-----: | :-----: | :-----: |
| **Nº Escalones**      | **1** | **2**  | **3**  | **4**   | **5**   | **6**   |
| **Sin merma**         | 0.637 | 0.787  | 0.851  | 0.887   | 0.908   | 0.924   |
| **Merma 2.5% (35M6)** | 0.621 | 0.767  | 0.830  | 0.865   | 0.885   | 0.900   |
| **Merma 3.0% (30M5)** | 0.618 | 0.763  | 0.825  | 0.860   | 0.881   | 0.896   |
| **Merma 3.5% (27M4)** | 0.615 | 0.759  | 0.821  | 0.856   | 0.876   | 0.891   |
| **Merma 4.0% (23M3)** | 0.612 | 0.756  | 0.817  | 0.852   | 0.872   | 0.887   |

#### 2.4. Dimensiones de los Escalones

Las dimensiones se calculan en función del diámetro del círculo circunscrito (D).

| Nº de Escalones | a (ancho 1) | a₁ (ancho 2) | a₂ (ancho 3) | a₃ (ancho 4) | a₄ (ancho 5) | a₅ (ancho 6) |
| :-------------- | :---------- | :----------- | :----------- | :----------- | :----------- | :----------- |
| **1**           | 0.707D      | -            | -            | -            | -            | -            |
| **2**           | 0.850D      | 0.526D       | -            | -            | -            | -            |
| **3**           | 0.906D      | 0.707D       | 0.424D       | -            | -            | -            |
| **4**           | 0.934D      | 0.796D       | 0.605D       | 0.356D       | -            | -            |
| **5**           | 0.950D      | 0.846D       | 0.707D       | 0.534D       | 0.313D       | -            |
| **6**           | 0.959D      | 0.875D       | 0.768D       | 0.640D       | 0.488D       | 0.281D       |

### **Paso 3: Parámetros Eléctricos y Constantes**

#### 3.1. Densidad de Flujo Magnético (B)

La selección de la densidad de flujo magnético es crucial y depende de la potencia nominal del transformador.

| Rango de Potencia (S) en kVA | Densidad de Flujo (B) en kgauss |
| :--------------------------- | :------------------------------ |
| S ≤ 1                        | 11 - 13                         |
| 1 < S ≤ 10                   | 13 - 16                         |
| 10 < S ≤ 100                 | 16 - 17                         |
| 100 < S ≤ 1000               | 17 - 18                         |
| 1000 < S ≤ 5000              | 17.5 - 18                       |

#### 3.2. Constante de Flujo Magnético (C)
Nota: Solo usar los limites de C(superior, inferior o promedio), dependerá de que coincida el flujo con el número de escalones. Tendrias que escoger el que mejor se adapte con la tabla 2.4 y la 2.2 y 3.1, tanto para monofasico como para trifasico

| Tipo de Transformador       | Rango del Valor C |
| :-------------------------- | :---------------- |
| Monofásico a 2 columnas     | 1.2 - 1.9         |
| Monofásico tipo acorazado   | 3 - 4             |
| Trifásico a 3 columnas      | 1 - 1.6           |
| Trifásico tipo acorazado    | 2 - 3             |

#### 3.3. Coeficiente de Plenitud del Cobre (Kc)

Para transformadores en aceite, el valor de `Kc` se calcula con las siguientes fórmulas, aplicando un **incremento del 15%** al resultado final. `E1` es la **tensión de fase** del bobinado primario en kV.

| Rango de Potencia (S) en kVA | Fórmula Base de Kc      |
| :--------------------------- | :---------------------- |
| S ≤ 10                       | `Kc = 8 / (30 + E1)`    |
| 10 < S ≤ 250                 | `Kc = 10 / (30 + E1)`   |
| 250 < S ≤ 1000               | `Kc = 12 / (30 + E1)`   |

#### 3.4. Intervalo de variacion del paso de regulacion comun

Toma de tesnion regulacion objetivo Paso de fase objetivo Intervalo admisible de variacion del paso de fase cumpliendo el error IEC

---

## Ejemplos de Diseño

### **Ejemplo 1: Transformador Monofásico 10 kVA**

#### **Datos de Entrada:**
*   **Potencia (S):** 10 kVA
*   **Tensión (E1/E2):** 13.2 / 0.23 kV
*   **Frecuencia (f):** 60 Hz
*   **Refrigeración:** ONAN
*   **Material del núcleo:** Acero M6 de 0.35mm

#### **Cálculos de Diseño:**

1.  **Parámetros Seleccionados de Tablas:**
    *   Inducción Magnética (B): `14500 líneas/cm²` o `1.45 T`
    *   Densidad de Corriente (J): `3.5 A/mm²`
    *   Constante de Flujo (C): `1.55` (para monofásico de 2 columnas)
    *   Coeficiente de plenitud del hierro (Kr): `0.767` (para 15 kVA y 2 escalones)
    *   Factor de apilamiento (fa): `0.975` (para M6 de 0.35mm)
    *   Coeficiente de plenitud del cobre (Kc): `Kc = (8 / (30 + 13.2)) * 1.15 = 0.21`

2.  **Flujo Magnético (Φ):**
    ```
    Φ = C * ((S/f)^0.5) * 10^6  [líneas]
    Φ = 1.55 * ((10/60)^0.5) * 10^6 = 632,782 líneas
    ```

3.  **Área del Núcleo:**
    *   **Área Neta (An):** `An = Φ / B = 632,782 / 14,500 = 43.64 cm²`
    *   **Área Bruta (Ab):** `Ab = An / fa = 43.64 / 0.975 = 44.76 cm²`

4.  **Dimensiones del Núcleo (2 Escalones):**
    *   **Diámetro Circunscrito (D):** `D = 2 * (An / (π * Kr))^0.5 = 8.52 cm`
    *   **Anchos (a, a₁):** `a = 0.850 * D = 7.24 cm`, `a₁ = 0.526 * D = 4.48 cm`
    *   **Espesores (e, e₁):** `e = 2.25 cm`, `e₁ = 1.37 cm`

5.  **Área y Dimensiones de la Ventana:**
    *   **Área de Ventana (Aw):** `159.4 cm²` (calculada con fórmula compleja)

6.  **Número de Espiras:**
    *   **Bobinado Secundario (N₂):** `N₂ = (230 * 10^8) / (4.44 * 60 * 632,782) = 136 espiras`
    *   **Bobinado Primario (N₁):** `N₁ = 136 * (13200 / 230) = 7810 espiras`

7.  **Corrientes y Secciones:**
    *   **Corriente Secundaria (I₂):** `I₂ = 10,000 / 230 = 43.48 A`
    *   **Corriente Primaria (I₁):** `I₁ = 10,000 / 13,200 = 0.76 A`
    *   **Sección del Conductor Secundario (S₂):** `S₂ = 43.48 / 3.5 = 12.42 mm²`
    *   **Sección del Conductor Primario (S₁):** `S₁ = 0.76 / 3.5 = 0.22 mm²`

---

### **Ejemplo 2: Transformador Monofásico 15 kVA con TAPS**

#### **Datos de Entrada:**
*   **Potencia (S):** 15 kVA
*   **Tensión (E1/E2):** 13.2 kV ± 2*2.5% / 230 V
*   **Frecuencia (f):** 60 Hz
*   **Refrigeración:** ONAN
*   **Material del núcleo:** Acero M6 de 0.35mm

#### **Cálculos de Diseño:**

1.  **Parámetros Seleccionados de Tablas:**
    *   Inducción Magnética (B): `16500 gauss` o `1.65 T`
    *   Densidad de Corriente (J): `3.5 A/mm²`
    *   Coeficiente Kr: `0.767` (para 15 kVA, 2 escalones)
    *   Coeficiente Kc: `0.27`
    *   Constante de Flujo (C): `1.55`


2.  **Flujo Magnético (Φ):**
    ```
    Φ = 1.55 * ((15/60)^0.5) * 10^6 = 775,000 líneas
    ```

3.  **Área del Núcleo:**
    *   **Área Neta (An):** `An = 775,000 / 16,500 = 46.97 cm²`
    *   **Área Bruta (Ab):** `Ab = 46.97 / 0.975 = 48.17 cm²`

4.  **Dimensiones del Núcleo (2 Escalones):**
    *   **Diámetro (D):** `D = 2 * (46.97 / (π * 0.767))^0.5 = 8.84 cm`
    *   **Anchos (a, a₁):** `a = 7.51 cm`, `a₁ = 4.65 cm`
    *   **Espesores (e, e₁):** `e = 2.33 cm`, `e₁ = 1.43 cm`

5.  **Tensiones y Corrientes por Toma (TAP):**
    *   **Tensiones Primarias (E₁):** Nominal `13,200 V`, con tomas a `13,860 V`, `13,530 V`, `12,870 V`, `12,540 V`
    *   **Tensión Secundaria (E₂):** `230 V`
    *   **Corrientes Primarias (I₁):** Nominal `1.14 A`, con un rango de `1.08 A` a `1.20 A`
    *   **Corriente Secundaria (I₂):** `15000 / 230 = 65.22 A`

6.  **Número de Espiras por Toma:**
    *   **Bobinado Secundario (N₂):** `111 espiras`
    *   **Bobinado Primario (N₁):** Nominal `6366 espiras`, con un rango de `6684 espiras` (toma +5%) a `6048 espiras` (toma -5%)

7.  **Diagrama de Conexionado (Distribución de Espiras):**
    *   **Devanado de Baja Tensión (BT):** `X1 - X2`: **111 espiras**
    *   **Devanado de Media Tensión (MT):**
        *   Sección `H1 - 5`: 3026 espiras
        *   Sección `5 - 3`: 159 espiras
        *   Sección `3 - 1`: 160 espiras
        *   Sección `2 - 4`: 160 espiras
        *   Sección `4 - 6`: 159 espiras
        *   Sección `6 - H2`: 3026 espiras
        *   **Total:** `6690 espiras` (Valor cercano a 6684, ajustado por redondeo)84, ajustado por redondeo)
## Fórmulas Detalladas (Referencia rápida)

A continuación se listan las fórmulas usadas en el flujo de diseño, con definición de variables y unidades.

- Notación:
  - S: potencia aparente en kVA (kilo-VA)
  - E1, E2: tensiones en V (línea) a entradas que corresponden a primario y secundario
  - E1_fase, E2_fase: tensiones de fase en V
  - f: frecuencia en Hz
  - Φ: flujo magnético en líneas (líneas = 1e-4 Wb)
  - C: constante de flujo (adimensional)
  - B: inducción magnética en kgauss (1 kgauss = 0.1 T)
  - B_t: inducción en Tesla (B_t = B_kgauss / 10)
  - J: densidad de corriente en A/mm²
  - Kc: coeficiente de plenitud del cobre (adimensional)
  - Kr: coeficiente de plenitud del hierro (adimensional)
  - fa: factor de apilamiento (adimensional)
  - An: área neta del núcleo en cm²
  - Ab: área bruta del núcleo en cm²
  - D: diámetro circunscrito en cm
  - Aw: área de ventana en cm²
  - b: alto (o ancho) de ventana en cm (según convención del cálculo)
  - M: distancia entre centros en cm
  - c, c' : anchos de ventana en cm
  - N1, N2: número de espiras (primario/secundario)
  - I1, I2: corrientes en A

### Conversión unidades usadas en fórmulas
- S [VA] = S[kVA] * 1000
- J [A/m²] = J [A/mm²] * 1e6
- An [cm²] ⇄ An [m²] = An * 1e-4
- Φ [líneas] = Φ (líneas). Para usar en fórmulas electromagnéticas se suele usar Φ en líneas.

### 1) Tensiones de fase
- Si el primario es en línea (E1_linea) y la conexión es estrella:
  - E1_fase = E1_linea / sqrt(3)
- Si está en triángulo:
  - E1_fase = E1_linea

(igual para E2_fase)

### 2) Coeficiente de plenitud del cobre (Kc)
- Fórmula base según S (kVA) y E1_fase (en kV):
  - Kc_base = kc_n / (30 + E1_kV)
    - kc_n = 8  si S ≤ 10
    - kc_n = 10 si 10 < S ≤ 250
    - kc_n = 12 si 250 < S ≤ 1000
  - Kc = Kc_base * 1.15
  - donde E1_kV = E1_fase / 1000

### 3) Flujo magnético (Φ)
- Φ [líneas] = C * sqrt(S / f) * 10^6
  - (S en kVA, f en Hz)

### 4) Área neta del núcleo (An) y área bruta (Ab)
- An [cm²] = Φ / (B_kgauss * 1000)   (porque B_kgauss*1000 da líneas/cm²)
- Ab [cm²] = An / fa

### 5) Coeficiente Kr y diámetro del núcleo D
- Seleccionar Kr desde tablas según merma y número de escalones.
- D [cm] = 2 * sqrt( An / (π * Kr) )

### 6) Dimensiones de escalones
- Anchos a_i = factor_i * D  (factores dados en tabla de dimensiones)
- Espesores desde geometría:
  - e_1 = ( sqrt(D^2 - a_1^2) ) / 2
  - e_i = ( sqrt(D^2 - a_i^2) - suma_previos ) / 2
- Verificación:
  - An_verificación = 2 * fa * sum( a_i * e_i )

### 7) Área de ventana (Aw), alto b, distancia entre centros M y ancho de ventana c
- Cálculo usado (forma general):
  - Aw [m²] = (S_VA) / (3.33 * f * B_t * J_A_m2 * Kc * An_m2)
    - S_VA = S[kVA] * 1000
    - B_t = B_kgauss / 10       (Tesla)
    - J_A_m2 = J [A/mm²] * 1e6
    - An_m2 = An [cm²] * 1e-4
  - Aw [cm²] = Aw_m2 * 1e4
- Alto de ventana b [cm]:
  - b = sqrt( rel_rw * Aw )   (rel_rw = relación b^2 / Aw o similar según convención)
- Distancia entre centros:
  - M = (Aw / b) + D
- Ancho de ventana:
  - c' = M - a_1   (o M - a según diseño)
  - c  = M - D

### 8) Número de espiras
- N2 (secundario):
  - N2 = (E2_fase * 10^8) / (4.44 * f * Φ)
    - E2_fase en V
    - Φ en líneas
- N1 (primario) relativo:
  - N1 = N2 * (E1_fase / E2_fase)

### 9) Corrientes y secciones de conductor
- Potencia aparente por devanado (por fase):
  - S_dev_VA = (S[kVA] * 1000) / fases
- Corrientes:
  - I1_fase = S_dev_VA / E1_fase
  - I2_fase = S_dev_VA / E2_fase
- Secciones (mm²):
  - s1 = I1_fase / J
  - s2 = I2_fase / J

### 10) TAPs (tomas de regulación)
- Para un porcentaje pct (%), la tensión de línea en la toma:
  - E1_linea_tap = E1_linea * (1 + pct/100)
- Tensión de fase en la toma (según conexión):
  - E1_fase_tap = E1_linea_tap / sqrt(3)  (si aplica)
- Número de espiras primario en toma:
  - N1_tap = round( N2 * (E1_fase_tap / E2_fase) )

---

### Notas prácticas
- Mantener consistencia de unidades: convertir kVA→VA, mm²→m², kgauss→Tesla cuando se mezclen fórmulas.
- Redondeos: Números de espiras deben redondearse y luego ajustarse en el bobinado final por manufactura.
- Si deseas, puedo generar una sección LaTeX con estas fórmulas (`1ER_EXAM.md` → sección con ecuaciones) o insertar las ecuaciones en formato matemático ya dentro del archivo.