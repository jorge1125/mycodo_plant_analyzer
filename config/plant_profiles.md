# Configuración de Perfiles de Plantas

Este archivo explica cómo configurar perfiles personalizados para sus plantas en el sistema Mycodo Plant Analyzer.

## Estructura Básica

Cada perfil de planta tiene la siguiente estructura:

```json
"nombre_perfil": {
  "type": "tipo_planta",
  "base_growth_rate": tasa_crecimiento,
  "sensor_mapping": {
    "parametro1": "id_sensor1",
    "parametro2": "id_sensor2",
    ...
  },
  "optimal_ranges": {
    "parametro1": {"min": valor_min, "max": valor_max, "unit": "unidad"},
    "parametro2": {"min": valor_min, "max": valor_max, "unit": "unidad"},
    ...
  }
}
```

## Parámetros Principales

- **nombre_perfil**: Identificador único para el perfil (ej. "tomate", "lechuga")
- **type**: Tipo de planta (ej. "tomato", "lettuce")
- **base_growth_rate**: Tasa base de crecimiento en condiciones óptimas (cm/día)
- **sensor_mapping**: Mapeo entre parámetros y sensores de Mycodo
- **optimal_ranges**: Rangos óptimos para cada parámetro

## Mapeo de Sensores

El mapeo de sensores conecta los parámetros ambientales con los sensores configurados en Mycodo:

```json
"sensor_mapping": {
  "temperature": "input_1",
  "humidity": "input_1",
  "light": "input_2",
  "soil_moisture": "input_3"
}
```

Donde:
- **temperature**: Temperatura ambiente
- **humidity**: Humedad relativa del aire
- **light**: Intensidad de luz
- **soil_moisture**: Humedad del suelo

Los valores (`input_1`, `input_2`, etc.) son los IDs de los sensores en Mycodo.

## Rangos Óptimos

Los rangos óptimos definen las condiciones ideales para cada parámetro:

```json
"optimal_ranges": {
  "temperature": {"min": 20, "max": 26, "unit": "°C"},
  "humidity": {"min": 65, "max": 85, "unit": "%"},
  "light": {"min": 15000, "max": 30000, "unit": "lux"},
  "soil_moisture": {"min": 60, "max": 80, "unit": "%"}
}
```

## Cómo Encontrar IDs de Sensores en Mycodo

1. Acceda a la interfaz web de Mycodo
2. Vaya a `Configuración` → `Entradas`
3. Anote el ID de cada sensor (generalmente mostrado como `input_X`)

## Ejemplo Completo

```json
"albahaca": {
  "type": "basil",
  "base_growth_rate": 1.5,
  "sensor_mapping": {
    "temperature": "input_1",
    "humidity": "input_1",
    "light": "input_2",
    "soil_moisture": "input_3"
  },
  "optimal_ranges": {
    "temperature": {"min": 18, "max": 24, "unit": "°C"},
    "humidity": {"min": 60, "max": 80, "unit": "%"},
    "light": {"min": 12000, "max": 25000, "unit": "lux"},
    "soil_moisture": {"min": 55, "max": 75, "unit": "%"}
  }
}
```

## Rangos Óptimos Recomendados para Plantas Comunes

### Tomate
- **Temperatura**: 20-26°C
- **Humedad**: 65-85%
- **Luz**: 15000-30000 lux
- **Humedad del suelo**: 60-80%

### Lechuga
- **Temperatura**: 15-22°C
- **Humedad**: 70-90%
- **Luz**: 10000-25000 lux
- **Humedad del suelo**: 65-85%

### Pimiento
- **Temperatura**: 21-29°C
- **Humedad**: 50-70%
- **Luz**: 18000-35000 lux
- **Humedad del suelo**: 55-75%

### Fresa
- **Temperatura**: 18-24°C
- **Humedad**: 60-80%
- **Luz**: 12000-28000 lux
- **Humedad del suelo**: 60-75%

### Albahaca
- **Temperatura**: 18-24°C
- **Humedad**: 60-80%
- **Luz**: 12000-25000 lux
- **Humedad del suelo**: 55-75%

### Espinaca
- **Temperatura**: 15-21°C
- **Humedad**: 65-85%
- **Luz**: 8000-20000 lux
- **Humedad del suelo**: 60-80%
