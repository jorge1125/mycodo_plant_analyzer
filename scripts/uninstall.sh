#!/bin/bash
# Script de desinstalación para Mycodo Plant Analyzer

# Colores para mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${RED}=== Desinstalación de Mycodo Plant Analyzer ===${NC}"
echo "Este script eliminará el sistema de análisis de plantas para Mycodo."
echo -e "${YELLOW}Advertencia: Esta acción no se puede deshacer.${NC}"

read -p "¿Está seguro de que desea desinstalar Mycodo Plant Analyzer? (s/n): " choice
if [ "$choice" != "s" ]; then
  echo "Desinstalación cancelada."
  exit 0
fi

# Verificar si el entorno virtual existe
VENV_DIR="$HOME/mycodo-plant-analyzer-env"
if [ -d "$VENV_DIR" ]; then
  echo -e "\n${GREEN}Eliminando entorno virtual...${NC}"
  rm -rf "$VENV_DIR"
  echo "Entorno virtual eliminado."
else
  echo "No se encontró el entorno virtual en $VENV_DIR"
fi

# Verificar si existe el directorio de configuración
CONFIG_DIR="$HOME/.mycodo-plant-analyzer"
if [ -d "$CONFIG_DIR" ]; then
  echo -e "\n${YELLOW}Se encontró el directorio de configuración en $CONFIG_DIR${NC}"
  read -p "¿Desea conservar sus archivos de configuración? (s/n): " choice
  if [ "$choice" != "s" ]; then
    echo "Eliminando directorio de configuración..."
    rm -rf "$CONFIG_DIR"
    echo "Directorio de configuración eliminado."
  else
    echo "Conservando archivos de configuración."
  fi
fi

# Verificar si existe el directorio de salida
OUTPUT_DIR="$HOME/mycodo-plant-analyzer-output"
if [ -d "$OUTPUT_DIR" ]; then
  echo -e "\n${YELLOW}Se encontró el directorio de salida en $OUTPUT_DIR${NC}"
  read -p "¿Desea conservar sus archivos de análisis y visualizaciones? (s/n): " choice
  if [ "$choice" != "s" ]; then
    echo "Eliminando directorio de salida..."
    rm -rf "$OUTPUT_DIR"
    echo "Directorio de salida eliminado."
  else
    echo "Conservando archivos de análisis y visualizaciones."
  fi
fi

# Eliminar script de acceso directo
SHORTCUT="$HOME/bin/mycodo-plant-analyzer"
if [ -f "$SHORTCUT" ]; then
  echo -e "\n${GREEN}Eliminando script de acceso directo...${NC}"
  rm "$SHORTCUT"
  echo "Script de acceso directo eliminado."
fi

echo -e "\n${GREEN}¡Desinstalación completada!${NC}"
echo "Mycodo Plant Analyzer ha sido desinstalado de su sistema."
echo -e "${YELLOW}Nota: Si instaló el paquete en modo desarrollo (-e), es posible que desee eliminar también el directorio del código fuente.${NC}"
