#!/bin/bash
# Script de actualización para Mycodo Plant Analyzer

# Colores para mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Actualización de Mycodo Plant Analyzer ===${NC}"

# Verificar si el entorno virtual existe
VENV_DIR="$HOME/mycodo-plant-analyzer-env"
if [ ! -d "$VENV_DIR" ]; then
  echo -e "${RED}Error: No se encontró el entorno virtual en $VENV_DIR${NC}"
  echo "Por favor, ejecute primero el script de instalación."
  exit 1
fi

# Activar entorno virtual
echo -e "\n${GREEN}Activando entorno virtual...${NC}"
source "$VENV_DIR/bin/activate"

# Actualizar el paquete
echo -e "\n${GREEN}Actualizando Mycodo Plant Analyzer...${NC}"
pip install --upgrade pip
pip install -e . --upgrade

if [ $? -ne 0 ]; then
  echo -e "${RED}Error: No se pudo actualizar el paquete.${NC}"
  exit 1
fi

# Verificar si hay cambios en la configuración de ejemplo
CONFIG_DIR="$HOME/.mycodo-plant-analyzer"
EXAMPLE_CONFIG="config/config.example.json"
USER_CONFIG="$CONFIG_DIR/config.json"

if [ -f "$EXAMPLE_CONFIG" ] && [ -f "$USER_CONFIG" ]; then
  echo -e "\n${GREEN}Verificando cambios en la configuración...${NC}"
  
  # Crear copia de seguridad de la configuración actual
  BACKUP_CONFIG="$USER_CONFIG.backup.$(date +%Y%m%d%H%M%S)"
  cp "$USER_CONFIG" "$BACKUP_CONFIG"
  echo "Copia de seguridad de la configuración creada en $BACKUP_CONFIG"
  
  # Informar al usuario sobre posibles cambios
  echo -e "${YELLOW}Nota: La configuración de ejemplo puede contener nuevas opciones.${NC}"
  echo "Compare su configuración actual con el archivo de ejemplo si es necesario."
  echo "Ejemplo: diff $USER_CONFIG $EXAMPLE_CONFIG"
fi

echo -e "\n${GREEN}¡Actualización completada con éxito!${NC}"
echo -e "Para usar el sistema actualizado, ejecute: ${YELLOW}mycodo-plant-analyzer --profile NOMBRE_PERFIL${NC}"
