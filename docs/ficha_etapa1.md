# FICHA – ETAPA 1: IDENTIFICACIÓN DE LA NECESIDAD

**Asignatura:** Business Analytics & Big Data II (ING-SOF8-N) · Ingeniería de Software VIII · 1er Corte
**Docente:** Oscar Castiblanco
**Fecha de emisión:** 7 de septiembre de 2026

---

## 1. Información del proyecto

| Campo | Detalle |
|---|---|
| **Nombre del proyecto** | Entidad financiera, proyecto de Riesgo de Crédito |
| **Integrantes** | Caren Dayana Romero Montoya · Karen Jimena Ocampo Otalora · Samuel Esteban Diaz Medina |
| **Empresa / caso** | Grupo 2 – Entidad financiera, proyecto de Riesgo de Crédito |

---

## 2. Problema de negocio

### Problema identificado

> El problema identificado es la dificultad para identificar oportunamente las características asociadas al riesgo de incumplimiento de las solicitudes de crédito, que afecta a los analistas y responsables de la gestión del riesgo, provocando una mayor incertidumbre en la evaluación de las solicitudes y posibles pérdidas por créditos incumplidos.

### ¿A quién afecta?

- **Analistas de crédito**: deben evaluar numerosas solicitudes y determinar su nivel de riesgo.
- **Área de riesgos**: debe controlar posibles incumplimientos de la cartera.
- **Entidad financiera**: posibles pérdidas por créditos que no sean pagados.
- **Solicitantes**: una evaluación poco precisa puede aprobar créditos de alto riesgo o rechazar solicitudes de bajo riesgo.

### ¿Qué consecuencias genera?

- Mayor posibilidad de otorgar créditos con alto riesgo de incumplimiento.
- Incremento potencial de la cartera vencida.
- Posibles pérdidas económicas para la entidad.
- Mayor incertidumbre durante la evaluación de las solicitudes.
- Dificultad para establecer criterios de evaluación respaldados por evidencia histórica.
- Posible rechazo de solicitudes que podrían representar clientes de bajo riesgo.

---

## 3. Pregunta principal de negocio

> **¿Qué características de los solicitantes y de las solicitudes de crédito están relacionadas con el riesgo de incumplimiento?**

### Preguntas complementarias

- ¿Existe relación entre el nivel de ingresos y el incumplimiento?
- ¿El historial crediticio está relacionado con el cumplimiento del crédito?
- ¿La cantidad de deuda está relacionada con una mayor probabilidad de incumplimiento?
- ¿El monto solicitado está relacionado con el riesgo de incumplimiento?
- ¿La antigüedad laboral presenta alguna relación con el cumplimiento?
- ¿El número de créditos que posee una persona está relacionado con su riesgo?
- ¿El plazo del crédito está relacionado con el incumplimiento?
- ¿Existen perfiles de solicitantes que presenten características asociadas a un mayor riesgo?

---

## 4. ¿Qué queremos analizar o predecir?

Queremos analizar y predecir la **probabilidad de que un solicitante de crédito incurra en impago (riesgo de incumplimiento)** con base en su perfil sociodemográfico, su historial crediticio y las condiciones financieras del préstamo solicitado.

1. **Identificar patrones y correlaciones**: descubrir qué variables (ingresos, monto solicitado, historial crediticio, antigüedad laboral, etc.) tienen mayor peso estadístico en el comportamiento de pago de los clientes.
2. **Predecir el nivel de riesgo**: clasificar oportunamente las solicitudes de crédito futuras en categorías de riesgo (bajo riesgo o alto riesgo de incumplimiento).
3. **Apoyar la toma de decisiones**: proveer a los analistas de crédito y al área de riesgos una base empírica respaldada por datos históricos para reducir la incertidumbre, disminuir la cartera vencida y evitar el rechazo injustificado de buenos clientes.

---

## 5. Variables necesarias

| Variable | Justificación |
|---|---|
| Edad / Perfil sociodemográfico | Permite analizar si la edad o etapa de vida del solicitante influye en la estabilidad económica y en su propensión al cumplimiento de las obligaciones crediticias. |
| Ingresos (mensuales / anuales) | Fundamental para medir la capacidad real de pago del solicitante y contrastarla frente al tamaño de la obligación financiera adquirida. |
| Antigüedad laboral | Indica estabilidad del empleo y sostenibilidad de la capacidad de pago en el tiempo. |
| Monto solicitado / Importe del crédito | Permite evaluar si los créditos de mayor cuantía concentran un mayor riesgo de impago o si el tamaño del préstamo afecta la liquidez del deudor. |
| Historial crediticio / Comportamiento de pago | Uno de los predictores más fuertes: indica el comportamiento previo del cliente en el sistema financiero (retrasos pasados, cartera vencida, puntualidad). |
| Número de créditos | Refleja el nivel de exposición y el posible sobreendeudamiento del solicitante. |
| Deuda | Carga financiera actual del solicitante frente a sus ingresos. |
| Plazo | Duración de la obligación y ventana temporal de exposición al riesgo. |
| Cumplimiento (Sí/No) | **Variable objetivo (target)**: permite clasificar el riesgo de incumplimiento. |

---

## 6. Datasets considerados

### Dataset 1 — Encuesta de Carga Financiera y Educación Financiera de los Hogares (IEFIC) 2017-2018

- **Fuente:** Departamento Administrativo Nacional de Estadística (DANE) – Colombia
- **Enlace:** https://microdatos.dane.gov.co/catalog/626/data_dictionary
- **Registros:** archivos IEFIC_2017 e IEFIC_2018 (verificar al descargar)
- **Variables:** 331 (ingresos, nivel educativo, características del hogar, vivienda, créditos, saldo de deudas, cuotas, capital, intereses, endeudamiento)
- **Formato:** CSV / JSON
- **Utilidad:** analizar las características económicas y financieras de los hogares colombianos y estudiar factores relacionados con el endeudamiento y el comportamiento de sus obligaciones crediticias.

### Dataset 2 — Distribución de cartera por producto

- **Fuente:** Superintendencia Financiera de Colombia – Datos Abiertos Colombia
- **Enlace:** https://www.datos.gov.co/Public-Finance/Distribuci-n-de-cartera-por-producto/rvii-eis8
- **Registros:** actualización mensual (verificar al descargar)
- **Variables:** entidad financiera, modalidad de crédito, producto, saldo de cartera, altura de mora, calificación de riesgo
- **Formato:** CSV
- **Utilidad:** analizar el comportamiento de la cartera crediticia en Colombia, especialmente los niveles de mora y las categorías de riesgo.

### Dataset 3 — Comportamiento de Cartera y Crédito

- **Fuente:** Instituto Colombiano de Crédito Educativo y Estudios Técnicos en el Exterior (ICETEX) – Datos Abiertos Colombia
- **Enlace:** https://www.datos.gov.co/Education/Comportamiento-de-Cartera-y-Cr-dito-/dugh-vkir
- **Registros:** cartera activa, actualización trimestral (verificar al descargar)
- **Variables:** 11 (fecha de corte, departamento de residencia, créditos al día, mora menor a 90 días, mora mayor a 90 días, saldo de capital, saldo total, saldo en mora)
- **Formato:** CSV
- **Utilidad:** analizar el comportamiento de los créditos y los niveles de mora en Colombia, así como las diferencias según el departamento de residencia.

---

## 7. Dataset seleccionado y justificación

**Seleccionado:** Encuesta de Carga Financiera y Educación Financiera de los Hogares (IEFIC) 2017-2018 — DANE.

**¿Por qué lo seleccionamos?**

- Presenta una alta correspondencia con el problema de investigación: contiene información financiera y socioeconómica de hogares colombianos.
- Cuenta con 331 variables (ingresos, nivel educativo, características del hogar, vivienda, créditos, saldo de deudas, capital, intereses, valor de las cuotas) que permiten analizar factores asociados al nivel de endeudamiento y al comportamiento de las obligaciones financieras.
- Permite un enfoque específico en Colombia, con información proveniente de una entidad oficial del país, lo que aumenta la pertinencia de los resultados para el contexto nacional.
- A partir de los datos se podrán identificar patrones de endeudamiento, analizar qué factores presentan mayor relación con la situación financiera de los deudores y generar información de apoyo para la gestión del riesgo de crédito.
- Aunque la IEFIC no corresponde exactamente a una base de solicitudes de crédito bancario con una variable binaria de "default", sí proporciona información relevante sobre endeudamiento, créditos y obligaciones financieras, por lo que se considera adecuada para una primera etapa de análisis exploratorio y de identificación de factores asociados al riesgo de incumplimiento en el contexto colombiano.

---

## 8. Design Thinking

### 8.1 Personas involucradas

**a. Parte solicitante (cliente)**

- **Acreditado / Deudor principal**: persona física o moral que solicita el préstamo, recibe los fondos y asume la obligación de pagarlo en las condiciones pactadas.
- **Coacreditado**: comparte la responsabilidad del crédito en las mismas condiciones que el deudor principal (común en créditos hipotecarios o de montos elevados).
- **Aval o fiador**: se compromete a responder por el pago de la deuda en caso de que el deudor principal incumpla.
- **Garante hipotecario / prendario**: aporta un bien (inmueble, vehículo, etc.) como garantía del crédito, sin ser necesariamente el deudor directo.

**b. Parte otorgante (entidad financiera)**

- **Ejecutivo / Asesor de crédito**: primer contacto; prospecta, recopila los documentos del cliente, arma el expediente y da seguimiento al trámite.
- **Analista de riesgos**: evalúa la capacidad de pago, el historial crediticio (central de riesgos) y el perfil del solicitante para determinar si el crédito es viable.
- **Comité de crédito**: autoriza o rechaza las solicitudes que superan ciertos montos o niveles de riesgo.
- **Mesa de formalización / contratación**: elabora los contratos y la documentación legal del préstamo.
- **Mesa de operaciones / dispersión**: realiza la transferencia o entrega efectiva de los fondos autorizados.
- **Gestor de cobranza**: interviene en caso de atrasos para gestionar el cobro de las cuotas pendientes.

**c. Terceros involucrados**

- **Notario público**: interviene en créditos de gran cuantía (como los hipotecarios) para dar fe pública del contrato y formalizar las garantías.
- **Valuador / perito**: evalúa el valor comercial de los bienes que se dejarán en garantía.

### 8.2 Necesidades identificadas

- Los analistas necesitan contar con información clara y suficiente para evaluar el riesgo de incumplimiento de una solicitud.
- La entidad financiera necesita identificar qué características de los solicitantes están relacionadas con el incumplimiento.
- El área de riesgos necesita reducir la posibilidad de otorgar créditos a perfiles con alta probabilidad de incumplimiento.
- La entidad necesita mantener un equilibrio entre la aprobación de créditos y la disminución de pérdidas por incumplimiento.
- Los responsables de la toma de decisiones necesitan información que permita respaldar sus criterios de evaluación.

### 8.3 Situación problemática observada

La entidad financiera recibe numerosas solicitudes de crédito con características diferentes entre los solicitantes. Actualmente existe la necesidad de comprender mejor cuáles características están relacionadas con el riesgo de incumplimiento. Una evaluación inadecuada puede generar dos situaciones: otorgar créditos a personas con alto riesgo de incumplimiento (aumentando las posibles pérdidas) o rechazar solicitudes de personas que podrían cumplir adecuadamente con sus obligaciones (perdiendo oportunidades de negocio). Por esta razón, la entidad necesita analizar la relación entre las características de las solicitudes y el comportamiento de cumplimiento observado.

---

## 9. Diagrama de Ishikawa

**Problema central:** Dificultad para identificar y evaluar oportunamente el riesgo de incumplimiento de las solicitudes de crédito.

> 📎 **Archivo adjunto:** `ishikawa.html` — diagrama visual generado por el grupo (abrir en navegador, imprimir o capturar como imagen).

### Causas por categoría (hipótesis iniciales)

**1. Personas**
- Diferencias en los criterios utilizados por los analistas.
- Experiencia variable de los responsables de evaluar solicitudes.
- Posibles errores humanos durante la evaluación.
- Dificultad para interpretar múltiples características del solicitante.

**2. Procesos**
- Criterios de evaluación que podrían no considerar adecuadamente todas las características disponibles.
- Proceso de evaluación complejo cuando existe un gran número de solicitudes.
- Falta de criterios suficientemente estandarizados para identificar perfiles de riesgo.
- Dificultad para comparar solicitudes con características diferentes.

**3. Tecnología**
- Herramientas de apoyo insuficientes para analizar grandes cantidades de solicitudes.
- Dificultad para identificar patrones cuando existen muchas variables.
- Procesos de evaluación que dependen demasiado de revisiones manuales.

**4. Producto / Servicio (crédito)**
- Montos de crédito diferentes entre solicitantes.
- Plazos de crédito diferentes.
- Diferentes niveles de endeudamiento de los solicitantes.
- Características del crédito que podrían aumentar o disminuir el riesgo de incumplimiento.

**5. Información / Datos**
- Historial crediticio desfavorable.
- Nivel de deuda elevado.
- Ingresos insuficientes frente al monto solicitado.
- Información histórica que puede presentar patrones difíciles de identificar manualmente.
- Diferencias en las características de los solicitantes que pueden estar asociadas con el cumplimiento.

**6. Entorno**
- Cambios en las condiciones económicas.
- Variaciones en la estabilidad laboral.
- Cambios en la capacidad de pago de los solicitantes.
- Condiciones externas que pueden afectar el cumplimiento de las obligaciones financieras.

---

## 10. Relación causas – datos

| # | Causa / hipótesis | Pregunta que se puede responder con datos | Dato necesario |
|---|---|---|---|
| 1 | Historial crediticio desfavorable | ¿Las personas con un historial crediticio desfavorable presentan mayor nivel de incumplimiento? | Historial crediticio + cumplimiento |
| 2 | Nivel de deuda elevado | ¿Existe relación entre el nivel de deuda y el incumplimiento? | Deuda + cumplimiento |
| 3 | Ingresos insuficientes | ¿Los solicitantes con menores ingresos presentan mayor riesgo de incumplimiento? | Ingresos + cumplimiento |
| 4 | Monto solicitado elevado | ¿Existe relación entre el monto solicitado y el incumplimiento? | Monto solicitado + cumplimiento |
| 5 | Plazo del crédito | ¿Los créditos con plazos mayores presentan mayor nivel de incumplimiento? | Plazo + cumplimiento |
| 6 | Número de créditos | ¿Las personas con mayor número de créditos presentan mayor riesgo de incumplimiento? | Número de créditos + cumplimiento |
| 7 | Antigüedad laboral | ¿La antigüedad laboral está relacionada con el cumplimiento de las obligaciones? | Antigüedad laboral + cumplimiento |
| 8 | Edad | ¿Existen diferencias en el nivel de incumplimiento según la edad del solicitante? | Edad + cumplimiento |

---

*Documento elaborado por el Grupo Estoicos — Business Analytics & Big Data II · 1er Corte.*