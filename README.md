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
git clone https://github.com/jorge1125/mycodo_plant_analyzer.git
cd mycodo-plant-analyzer
bash scripts/install.sh
```

### Instalación Manual

1. Clone el repositorio:
   ```bash
   git clone https://github.com/jorge1125/mycodo_plant_analyzer.git
   cd mycodo_plant_analyzer
   ```
Para instalar el paquete desde el directorio clonado:
Navega al directorio del repositorio:
bash
cd /home/usuario/mycodo_plant_analyzer

Ejecuta el script de instalación automática:
bash scripts/install.sh



El script realizará todo el proceso de instalación automáticamente. Seguirá estos pasos:
Verificará las dependencias necesarias

Creará un entorno virtual en ~/mycodo-plant-analyzer-env

Instalará el paquete y sus dependencias
Configurará los directorios necesarios
Copiará el archivo de configuración de ejemplo a ~/.mycodo-plant-analyzer/config.json
Creará un acceso directo en ~/bin/mycodo_plant_analyzer
Después de la instalación, necesitarás editar el archivo de configuración para conectarlo con tu instancia de Mycodo:
bash
nano ~/.mycodo-plant-analyzer/config.json

Asegúrate de configurar correctamente:
La conexión a Mycodo (host, puerto, API key)
Los perfiles de plantas con los IDs correctos de tus sensores

Una vez configurado, puedes ejecutar un análisis con:

~/bin/mycodo-plant-analyzer --profile tomate
Los resultados del análisis se guardarán en ~/mycodo-plant-analyzer-output/ y podrás abrir el dashboard HTML generado en tu navegador para ver las visualizaciones.

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
