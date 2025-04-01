# Guía de Uso de Mycodo Plant Analyzer

Esta guía explica cómo utilizar el Sistema de Análisis de Plantas con Mycodo para monitorear y optimizar el crecimiento de sus plantas.

## Contenido

1. [Introducción](#introducción)
2. [Instalación](#instalación)
3. [Configuración](#configuración)
4. [Uso Básico](#uso-básico)
5. [Interpretación de Resultados](#interpretación-de-resultados)
6. [Visualizaciones](#visualizaciones)
7. [Solución de Problemas](#solución-de-problemas)
8. [Preguntas Frecuentes](#preguntas-frecuentes)

## Introducción

Mycodo Plant Analyzer es un sistema completo para analizar datos de plantas recopilados por Mycodo. El sistema permite:

- Monitorear el crecimiento de plantas
- Evaluar condiciones ambientales
- Detectar tendencias y patrones
- Generar recomendaciones específicas
- Visualizar resultados con gráficos informativos

## Instalación

### Requisitos Previos

- Raspberry Pi (3 o superior recomendado)
- Mycodo instalado y configurado (versión 8.0 o superior)
- Python 3.7 o superior
- Sensores compatibles con Mycodo

### Pasos de Instalación

1. Clone el repositorio:
   ```bash
   git clone https://github.com/jorge1125/mycodo-plant-analyzer.git
   cd mycodo-plant-analyzer
   ```

2. Ejecute el script de instalación:
   ```bash
   bash scripts/install.sh
   ```

3. Siga las instrucciones en pantalla para completar la instalación.

## Configuración

### Configuración de Conexión con Mycodo

Edite el archivo de configuración en `~/.mycodo-plant-analyzer/config.json`:

```json
"mycodo": {
  "connection_method": "api",
  "host": "localhost",
  "port": 8080,
  "api_key": "SU_CLAVE_API_DE_MYCODO",
  "ssl": false
}
```

Para obtener su clave API de Mycodo:
1. Acceda a la interfaz web de Mycodo
2. Vaya a `Configuración` → `API`
3. Genere una nueva clave API si no tiene una

### Configuración de Perfiles de Plantas

Cada planta necesita un perfil con rangos óptimos y mapeo de sensores:

```json
"tomate": {
  "type": "tomato",
  "sensor_mapping": {
    "temperature": "input_1",
    "humidity": "input_1",
    "light": "input_2",
    "soil_moisture": "input_3"
  },
  "optimal_ranges": {
    "temperature": {"min": 20, "max": 26, "unit": "°C"},
    "humidity": {"min": 65, "max": 85, "unit": "%"},
    "light": {"min": 15000, "max": 30000, "unit": "lux"},
    "soil_moisture": {"min": 60, "max": 80, "unit": "%"}
  }
}
```

Para más detalles sobre la configuración de perfiles, consulte [plant_profiles.md](config/plant_profiles.md).

## Uso Básico

### Ejecutar un Análisis

Para analizar una planta específica:

```bash
mycodo-plant-analyzer --profile tomate
```

Opciones adicionales:

```bash
mycodo-plant-analyzer --profile tomate --days 14 --output /ruta/personalizada
```

Donde:
- `--profile`: Perfil de planta a utilizar (requerido)
- `--days`: Número de días de datos históricos a analizar (por defecto: 30)
- `--output`: Directorio personalizado para guardar resultados

### Programar Análisis Automáticos

Para ejecutar análisis automáticos, puede usar cron:

```bash
# Editar crontab
crontab -e

# Añadir una línea para ejecutar el análisis diariamente a las 8:00 AM
0 8 * * * $HOME/bin/mycodo-plant-analyzer --profile tomate
```

## Interpretación de Resultados

### Dashboard HTML

Después de ejecutar un análisis, se genera un dashboard HTML en el directorio de salida:

```
~/mycodo-plant-analyzer-output/dashboard_tomate.html
```

Abra este archivo en un navegador para ver:

- Puntuación general de crecimiento
- Análisis de parámetros individuales
- Tendencias detectadas
- Recomendaciones específicas

### Puntuación de Crecimiento

La puntuación general se clasifica en:

- **Excelente (80-100)**: Condiciones óptimas para el crecimiento
- **Bueno (60-79)**: Buenas condiciones, pequeñas mejoras posibles
- **Aceptable (40-59)**: Condiciones aceptables, mejoras recomendadas
- **Deficiente (0-39)**: Condiciones subóptimas, mejoras necesarias

### Estado de Parámetros

Cada parámetro se clasifica como:

- **Óptimo**: El parámetro está dentro del rango ideal la mayor parte del tiempo
- **Aceptable**: El parámetro está dentro del rango ideal al menos el 60% del tiempo
- **Subóptimo**: El parámetro está fuera del rango ideal con frecuencia

## Visualizaciones

El sistema genera varias visualizaciones:

### Gráficos de Parámetros

![Ejemplo de gráfico de parámetro](https://i.imgur.com/example1.png)

Estos gráficos muestran:
- Valores del parámetro a lo largo del tiempo
- Rango óptimo (área verde)
- Línea de tendencia
- Estadísticas clave

### Análisis General

![Ejemplo de análisis general](https://i.imgur.com/example2.png)

Este gráfico muestra:
- Puntuación general de crecimiento
- Estado de cada parámetro
- Distribución de tendencias
- Recomendaciones principales

## Solución de Problemas

### Problemas de Conexión con Mycodo

Si tiene problemas para conectarse a Mycodo:

1. Verifique que Mycodo esté en ejecución:
   ```bash
   sudo systemctl status mycodo
   ```

2. Verifique que la API esté habilitada en Mycodo:
   - Acceda a la interfaz web de Mycodo
   - Vaya a `Configuración` → `API`
   - Asegúrese de que la API esté habilitada

3. Verifique la clave API en su configuración:
   ```bash
   nano ~/.mycodo-plant-analyzer/config.json
   ```

### No se Encuentran Datos de Sensores

Si el sistema no puede encontrar datos de sensores:

1. Verifique el mapeo de sensores en su perfil:
   ```bash
   nano ~/.mycodo-plant-analyzer/config.json
   ```

2. Confirme los IDs de sensores en Mycodo:
   - Acceda a la interfaz web de Mycodo
   - Vaya a `Configuración` → `Entradas`
   - Anote los IDs correctos de sus sensores

3. Verifique que los sensores estén recopilando datos:
   - Vaya a `Datos` → `Mediciones en vivo` en Mycodo
   - Confirme que los sensores muestren lecturas recientes

## Preguntas Frecuentes

### ¿Cuántos datos históricos necesito para un buen análisis?

Se recomienda al menos 7 días de datos para obtener resultados significativos. El análisis mejora con más datos históricos, siendo 30 días un período ideal para detectar patrones y tendencias.

### ¿Puedo analizar múltiples plantas al mismo tiempo?

Actualmente, el sistema analiza una planta a la vez. Para analizar múltiples plantas, ejecute el comando para cada perfil por separado:

```bash
mycodo-plant-analyzer --profile tomate
mycodo-plant-analyzer --profile lechuga
```

### ¿Cómo actualizo el sistema?

Para actualizar a la última versión:

```bash
cd ~/mycodo-plant-analyzer
git pull
bash scripts/update.sh
```

### ¿Puedo usar el sistema sin Mycodo local?

Sí, puede configurar el sistema para conectarse a una instancia remota de Mycodo:

```json
"mycodo": {
  "connection_method": "api",
  "host": "192.168.1.100",
  "port": 8080,
  "api_key": "SU_CLAVE_API_DE_MYCODO",
  "ssl": false
}
```

### ¿Cómo desinstalo el sistema?

Para desinstalar completamente:

```bash
bash ~/mycodo-plant-analyzer/scripts/uninstall.sh
```

Siga las instrucciones en pantalla para completar la desinstalación.
