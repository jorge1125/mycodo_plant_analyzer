# Mycodo Plant Analyzer

Un sistema completo para analizar datos de plantas recopilados por Mycodo, evaluar el crecimiento y generar visualizaciones interactivas.

## Características Principales

- **Conexión con Mycodo**: Obtiene datos de sensores a través de la API REST, InfluxDB o archivos exportados
- **Análisis de Crecimiento**: Evalúa condiciones ambientales y detecta tendencias
- **Visualizaciones Avanzadas**: Genera dashboards interactivos y gráficos informativos
- **Perfiles de Plantas**: Configuración personalizada para diferentes tipos de plantas
- **Análisis Automatizado**: Programación de análisis periódicos con notificaciones

## Instalación

### Método Rápido

```bash
git clone https://github.com/jorge1125/mycodo-plant-analyzer.git
cd mycodo-plant-analyzer
bash scripts/install.sh
```

### Instalación Manual

1. Clone el repositorio:
   ```bash
   git clone https://github.com/jorge1125/mycodo-plant-analyzer.git
   cd mycodo-plant-analyzer
   ```

2. Cree un entorno virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instale el paquete:
   ```bash
   pip install -e .
   ```

4. Configure el sistema:
   ```bash
   mkdir -p ~/.mycodo-plant-analyzer
   cp config/config.example.json ~/.mycodo-plant-analyzer/config.json
   ```

## Uso Básico

```bash
# Ejecutar análisis para un perfil de planta
mycodo-plant-analyzer --profile tomate

# Especificar días de datos históricos
mycodo-plant-analyzer --profile tomate --days 14

# Especificar directorio de salida personalizado
mycodo-plant-analyzer --profile tomate --output /ruta/personalizada
```

## Ejemplos

El repositorio incluye varios ejemplos para demostrar diferentes funcionalidades:

- **basic_usage.py**: Uso básico del sistema con datos simulados
- **automated_analysis.py**: Configuración de análisis automáticos periódicos
- **advanced_visualization.py**: Creación de visualizaciones personalizadas

Para ejecutar los ejemplos:

```bash
python examples/basic_usage.py
python examples/advanced_visualization.py --profile tomate
```

## Documentación

Para obtener información detallada sobre la instalación, configuración y uso del sistema, consulte:

- [Guía de Instalación](docs/installation_guide.md)
- [Guía de Usuario](docs/user_guide.md)
- [Configuración de Perfiles de Plantas](config/plant_profiles.md)

## Requisitos

- Python 3.7 o superior
- Mycodo 8.0 o superior (para conexión en vivo)
- Raspberry Pi u otro sistema Linux compatible

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - vea el archivo [LICENSE](LICENSE) para más detalles.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, siéntase libre de enviar pull requests o abrir issues para mejorar el sistema.
