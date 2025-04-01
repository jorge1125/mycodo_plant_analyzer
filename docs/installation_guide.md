# Guía de Instalación de Mycodo Plant Analyzer

Esta guía proporciona instrucciones detalladas para instalar y configurar el Sistema de Análisis de Plantas con Mycodo.

## Requisitos del Sistema

### Hardware
- Raspberry Pi 3 o superior (recomendado)
- Sensores compatibles con Mycodo:
  - Sensor de temperatura y humedad (DHT22, BME280, etc.)
  - Sensor de luz (TSL2561, BH1750, etc.)
  - Sensor de humedad del suelo (capacitivo o resistivo)

### Software
- Raspberry Pi OS (anteriormente Raspbian) o cualquier distribución Linux compatible
- Python 3.7 o superior
- Mycodo 8.0 o superior instalado y configurado
- Git

## Instalación Paso a Paso

### 1. Preparación del Sistema

Asegúrese de que su sistema esté actualizado:

```bash
sudo apt update
sudo apt upgrade -y
```

Instale las dependencias necesarias:

```bash
sudo apt install -y python3-pip python3-venv git
```

### 2. Instalación de Mycodo (si aún no está instalado)

Si aún no tiene Mycodo instalado, siga las instrucciones oficiales en [https://github.com/kizniche/Mycodo](https://github.com/kizniche/Mycodo).

Resumen rápido:

```bash
cd ~
wget https://raw.githubusercontent.com/kizniche/Mycodo/master/install/install_mycodo.sh
sudo bash install_mycodo.sh
```

### 3. Configuración de Mycodo

1. Acceda a la interfaz web de Mycodo (generalmente en `http://IP_DE_SU_RASPBERRY:7880`)
2. Configure sus sensores en `Configuración` → `Entradas`
3. Anote los IDs de sus sensores (aparecen como `input_X`)
4. Habilite la API en `Configuración` → `API`
5. Genere una clave API y anótela

### 4. Instalación de Mycodo Plant Analyzer

Clone el repositorio:

```bash
cd ~
git clone https://github.com/jorge1125/mycodo-plant-analyzer.git
cd mycodo-plant-analyzer
```

Ejecute el script de instalación:

```bash
bash scripts/install.sh
```

El script realizará las siguientes acciones:
- Verificará las dependencias del sistema
- Creará un entorno virtual de Python
- Instalará el paquete y sus dependencias
- Configurará los directorios necesarios
- Creará un script de acceso directo

### 5. Configuración del Sistema

Edite el archivo de configuración:

```bash
nano ~/.mycodo-plant-analyzer/config.json
```

Configure la conexión con Mycodo:

```json
"mycodo": {
  "connection_method": "api",
  "host": "localhost",
  "port": 8080,
  "api_key": "SU_CLAVE_API_DE_MYCODO",
  "ssl": false
}
```

Configure los perfiles de plantas:

```json
"plant_profiles": {
  "tomate": {
    "type": "tomato",
    "base_growth_rate": 2.5,
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
}
```

Reemplace `input_1`, `input_2`, etc. con los IDs reales de sus sensores en Mycodo.

## Verificación de la Instalación

Ejecute un análisis de prueba:

```bash
mycodo-plant-analyzer --profile tomate
```

Si todo está configurado correctamente, debería ver:
1. Mensajes de progreso en la terminal
2. Un archivo HTML generado en `~/mycodo-plant-analyzer-output/dashboard_tomate.html`

Abra el archivo HTML en un navegador para ver los resultados del análisis.

## Configuración Avanzada

### Métodos de Conexión Alternativos

El sistema admite varios métodos para conectarse a Mycodo:

#### Conexión Directa a InfluxDB

```json
"mycodo": {
  "connection_method": "influxdb",
  "influxdb": {
    "host": "localhost",
    "port": 8086,
    "database": "mycodo_db",
    "username": "",
    "password": ""
  }
}
```

#### Conexión a Archivos Exportados

```json
"mycodo": {
  "connection_method": "export",
  "export_dir": "/var/mycodo-export"
}
```

#### Conexión al Daemon de Mycodo

```json
"mycodo": {
  "connection_method": "daemon",
  "daemon_path": "/var/mycodo-root"
}
```

### Configuración de Ejecución Automática

Para ejecutar análisis automáticos periódicamente, configure una tarea cron:

```bash
crontab -e
```

Añada una línea para ejecutar el análisis diariamente a las 8:00 AM:

```
0 8 * * * $HOME/bin/mycodo-plant-analyzer --profile tomate
```

## Solución de Problemas de Instalación

### Error: "No se pudo crear el entorno virtual"

Asegúrese de tener instalado python3-venv:

```bash
sudo apt install -y python3-venv
```

### Error: "No se pudo instalar el paquete"

Verifique que tiene las dependencias de desarrollo necesarias:

```bash
sudo apt install -y python3-dev build-essential
```

### Error: "No se pudo conectar a Mycodo"

Verifique:
1. Que Mycodo esté en ejecución: `sudo systemctl status mycodo`
2. Que la API esté habilitada en Mycodo
3. Que la clave API sea correcta
4. Que el host y puerto sean correctos

### Error: "No se encontraron datos de sensores"

Verifique:
1. Que los IDs de sensores en su configuración sean correctos
2. Que los sensores estén recopilando datos en Mycodo
3. Que haya datos históricos disponibles para el período solicitado

## Actualización del Sistema

Para actualizar a la última versión:

```bash
cd ~/mycodo-plant-analyzer
git pull
bash scripts/update.sh
```

## Desinstalación

Si necesita desinstalar el sistema:

```bash
bash ~/mycodo-plant-analyzer/scripts/uninstall.sh
```

Siga las instrucciones en pantalla para completar la desinstalación.
