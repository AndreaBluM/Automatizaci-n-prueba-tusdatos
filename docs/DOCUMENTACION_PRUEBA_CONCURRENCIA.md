# 🧪 CASO DE PRUEBA: 15 CONSULTAS PARALELAS

## 📋 Documentación Técnica

### 🎯 **OBJETIVO PRINCIPAL**
Verificar que el sistema de consultas automáticas de la Registraduría Nacional puede manejar múltiples consultas simultáneas sin ser bloqueado por la página web.

### 🔍 **OBJETIVOS ESPECÍFICOS**
- ✅ **Verificar ausencia de bloqueos**: Comprobar que la página no bloquee consultas concurrentes
- ⏱️ **Registrar tiempos de respuesta**: Medir la duración de cada consulta individual
- 📊 **Documentar éxito/fallo**: Registrar qué consultas completaron exitosamente
- 🔄 **Analizar concurrencia**: Evaluar el paralelismo efectivo del sistema

---

## 🛠️ **METODOLOGÍA DE PRUEBA**

### **Configuración**
```python
- Total de consultas: 15 simultáneas
- Timeout por consulta: 300 segundos (5 minutos)
- Delay entre lanzamientos: 0.5 segundos
- Modo de ejecución: Threading paralelo
- Aislamiento: Subprocess por consulta
```

### **Datos de Prueba**
Utilizamos 15 combinaciones de cédula/fecha realistas:
- Cédulas de prueba estándar
- Fechas distribuidas entre 1985-2000
- Datos que simularían consultas reales

### **Métricas Registradas**
1. **Por consulta individual**:
   - 🕐 Tiempo de inicio y finalización
   - ⏱️ Duración total de ejecución
   - ✅/❌ Estado de éxito o fallo
   - 📄 Datos extraídos (si/no)
   - 🚫 Bloqueos detectados
   - 🧵 Thread ID para rastreo

2. **Métricas globales**:
   - 📈 Tasa de éxito general
   - ⏳ Tiempo total de todas las consultas
   - 🔄 Máximo de consultas ejecutándose simultáneamente
   - 🚀 Velocidad (consultas por segundo)
   - 📊 Estadísticas de tiempos (promedio, mediana, desviación)

---

## 📁 **ARCHIVOS GENERADOS**

### **Script Principal**
- `test_15_consultas_paralelas.py` - Ejecutor de pruebas
- `prueba_concurrencia.py` - Versión avanzada con más análisis

### **Resultados**
- `reporte_15_consultas_[timestamp].json` - Reporte detallado
- `consulta_[cedula]_[timestamp].json` - Datos por consulta exitosa
- `certificado_[cedula]_[timestamp].pdf` - PDFs descargados (si aplica)

---

## 🔬 **ANÁLISIS DE RESULTADOS**

### **Criterios de Evaluación**

| Métrica | Valor Objetivo | Crítico |
|---------|---------------|---------|
| Tasa de éxito | ≥ 80% | ≥ 60% |
| Bloqueos detectados | 0 | ≤ 2 |
| Tiempo promedio | ≤ 60s | ≤ 120s |
| Consultas simultáneas | ≥ 10 | ≥ 5 |

### **Indicadores de Bloqueo**
- ⏰ **Timeouts**: Consultas que exceden 5 minutos
- 🚫 **Errores HTTP**: Códigos 429, 503, 403
- 🔒 **Patrones de fallo**: Múltiples fallos consecutivos
- 📉 **Degradación**: Aumento progresivo de tiempos

### **Análisis de Concurrencia**
```python
# Cálculo de paralelismo efectivo
max_paralelas = máximo_consultas_ejecutándose_simultáneamente
eficiencia = consultas_exitosas / tiempo_total
throughput = total_consultas / tiempo_total
```

---

## 📊 **ESTRUCTURA DEL REPORTE**

### **Sección 1: Metadata**
- Fecha y hora de ejecución
- Versión del script
- Configuración utilizada

### **Sección 2: Resultados Generales**
- Tasa de éxito/fallo
- Consultas con datos extraídos
- Bloqueos detectados
- Tiempo total de ejecución

### **Sección 3: Análisis de Tiempos**
- Estadísticas descriptivas completas
- Distribución de tiempos
- Identificación de outliers

### **Sección 4: Análisis de Concurrencia**
- Paralelismo máximo alcanzado
- Eficiencia del sistema
- Detección de cuellos de botella

### **Sección 5: Errores y Bloqueos**
- Categorización de errores
- Patrones de fallo identificados
- Recomendaciones de mejora

### **Sección 6: Resultados Detallados**
- Log completo de cada consulta
- Trazabilidad por thread
- Datos extraídos por consulta

### **Sección 7: Conclusiones Automáticas**
- Evaluación automática vs criterios
- Recomendaciones del sistema
- Estado general de la prueba

---

## 🚀 **EJECUCIÓN**

### **Prerequisitos**
```bash
# Dependencias requeridas
pip install requests selenium PyPDF2 pdfplumber

# ChromeDriver actualizado
# Tesseract OCR instalado y configurado
```

### **Comando de Ejecución**
```bash
python test_15_consultas_paralelas.py
```

### **Proceso**
1. 🔧 Validación de dependencias
2. ⚠️ Advertencia al usuario sobre el impacto
3. 🚀 Lanzamiento de 15 threads paralelos
4. 📊 Monitoreo en tiempo real
5. 📄 Generación de reporte detallado
6. 🎯 Análisis automático de resultados

---

## 🔒 **CONSIDERACIONES DE SEGURIDAD**

### **Impacto en el Servidor**
- Las 15 consultas simultáneas pueden representar una carga significativa
- Implementamos delays entre lanzamientos (0.5s) para suavizar el impacto
- Timeout de 5 minutos previene consultas infinitas

### **Detección de Límites**
- Monitoreo de códigos de respuesta HTTP
- Detección de patrones de bloqueo
- Análisis de degradación de rendimiento

### **Buenas Prácticas**
- Ejecución controlada con confirmación del usuario
- Logging detallado para auditoría
- Cleanup automático de recursos

---

## 📈 **INTERPRETACIÓN DE RESULTADOS**

### **✅ Escenario Ideal**
- Tasa de éxito: 100% (15/15)
- Bloqueos: 0
- Tiempo promedio: 30-45 segundos
- **Conclusión**: Sistema robusto para concurrencia

### **⚠️ Escenario Aceptable**
- Tasa de éxito: 80-99% (12-14/15)
- Bloqueos: 1-2 consultas
- Tiempo promedio: 45-60 segundos
- **Conclusión**: Sistema funcional con limitaciones menores

### **❌ Escenario Problemático**
- Tasa de éxito: <80% (<12/15)
- Bloqueos: >2 consultas
- Tiempo promedio: >60 segundos
- **Conclusión**: Sistema no apto para uso concurrente

---

## 🛠️ **RESOLUCIÓN DE PROBLEMAS**

### **Errores Comunes**

| Error | Causa Probable | Solución |
|-------|---------------|----------|
| Timeout | Página lenta/bloqueo | Reducir consultas paralelas |
| Código 429 | Rate limiting | Implementar delays mayores |
| OCR fallos | CAPTCHA complejo | Mejorar preprocesamiento |
| Selenium crash | Recursos insuficientes | Aumentar memoria/CPU |

### **Optimizaciones Sugeridas**
- Reducir paralelismo si hay muchos bloqueos
- Implementar retry logic inteligente
- Usar proxies para distribuir carga
- Optimizar timeouts por tipo de error

---

## 📋 **CHECKLIST DE EJECUCIÓN**

- [ ] ✅ Dependencias instaladas y verificadas
- [ ] 🔧 ChromeDriver actualizado
- [ ] 🖼️ Tesseract OCR configurado
- [ ] 💾 Espacio en disco suficiente (>100MB)
- [ ] 🌐 Conexión estable a internet
- [ ] ⚠️ Usuario informado del impacto
- [ ] 📊 Sistema de monitoreo preparado
- [ ] 🚀 Ejecución confirmada
- [ ] 📄 Reporte generado y revisado
- [ ] 🎯 Conclusiones documentadas

---

**Fecha de creación**: 29/11/2025  
**Versión**: 1.0  
**Autor**: Sistema Automatizado de Pruebas