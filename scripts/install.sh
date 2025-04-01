#!/bin/bash
# Script de instalación para Mycodo Plant Analyzer

# Colores para mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Instalación de Mycodo Plant Analyzer ===${NC}"
echo "Este script instalará el sistema de análisis de plantas para Mycodo."

# Verificar si se está ejecutando como root
if [ "$EUID" -eq 0 ]; then
  echo -e "${YELLOW}Advertencia: No es recomendable ejecutar este script como root.${NC}"
  read -p "¿Desea continuar de todos modos? (s/n): " choice
  if [ "$choice" != "s" ]; then
    echo "Instalación cancelada."
    exit 1
  fi
fi

# Verificar si Mycodo está instalado
if [ ! -d "/var/mycodo-root" ]; then
  echo -e "${YELLOW}Advertencia: No se detectó una instalación de Mycodo en /var/mycodo-root${NC}"
  echo "El sistema puede funcionar sin Mycodo local, pero necesitará configurar la conexión a un Mycodo remoto."
  read -p "¿Desea continuar de todos modos? (s/n): " choice
  if [ "$choice" != "s" ]; then
    echo "Instalación cancelada."
    exit 1
  fi
fi

# Verificar dependencias del sistema
echo -e "\n${GREEN}Verificando dependencias del sistema...${NC}"
DEPS_NEEDED=()

# Verificar Python
if ! command -v python3 &> /dev/null; then
  DEPS_NEEDED+=("python3")
fi

# Verificar pip
if ! command -v pip3 &> /dev/null; then
  DEPS_NEEDED+=("python3-pip")
fi

# Instalar dependencias si es necesario
if [ ${#DEPS_NEEDED[@]} -gt 0 ]; then
  echo -e "${YELLOW}Se necesitan instalar las siguientes dependencias: ${DEPS_NEEDED[*]}${NC}"
  read -p "¿Desea instalarlas ahora? (s/n): " choice
  if [ "$choice" = "s" ]; then
    echo "Instalando dependencias..."
    sudo apt update
    sudo apt install -y ${DEPS_NEEDED[*]}
  else
    echo -e "${RED}Error: Dependencias requeridas no instaladas. Abortando.${NC}"
    exit 1
  fi
fi

# Crear entorno virtual
echo -e "\n${GREEN}Creando entorno virtual...${NC}"
VENV_DIR="$HOME/mycodo-plant-analyzer-env"

if [ -d "$VENV_DIR" ]; then
  echo -e "${YELLOW}El entorno virtual ya existe en $VENV_DIR${NC}"
  read -p "¿Desea eliminarlo y crear uno nuevo? (s/n): " choice
  if [ "$choice" = "s" ]; then
    rm -rf "$VENV_DIR"
  else
    echo "Se utilizará el entorno virtual existente."
  fi
fi

if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
  if [ $? -ne 0 ]; then
    echo -e "${RED}Error: No se pudo crear el entorno virtual.${NC}"
    exit 1
  fi
fi

# Activar entorno virtual
echo -e "\n${GREEN}Activando entorno virtual...${NC}"
source "$VENV_DIR/bin/activate"

# Instalar el paquete
echo -e "\n${GREEN}Instalando Mycodo Plant Analyzer...${NC}"
pip install --upgrade pip
pip install -e .

if [ $? -ne 0 ]; then
  echo -e "${RED}Error: No se pudo instalar el paquete.${NC}"
  exit 1
fi

# Crear directorio de configuración
echo -e "\n${GREEN}Configurando el sistema...${NC}"
CONFIG_DIR="$HOME/.mycodo-plant-analyzer"
mkdir -p "$CONFIG_DIR"

# Copiar archivo de configuración de ejemplo si no existe
if [ ! -f "$CONFIG_DIR/config.json" ]; then
  cp config/config.example.json "$CONFIG_DIR/config.json"
  echo "Archivo de configuración copiado a $CONFIG_DIR/config.json"
  echo -e "${YELLOW}Importante: Edite este archivo para configurar su conexión con Mycodo y perfiles de plantas.${NC}"
else
  echo "El archivo de configuración ya existe en $CONFIG_DIR/config.json"
fi

# Crear directorio de salida
OUTPUT_DIR="$HOME/mycodo-plant-analyzer-output"
mkdir -p "$OUTPUT_DIR"
echo "Directorio de salida creado en $OUTPUT_DIR"

# Crear script de acceso directo
SHORTCUT="$HOME/bin/mycodo-plant-analyzer"
mkdir -p "$HOME/bin"

cat > "$SHORTCUT" << EOF
#!/bin/bash
source "$VENV_DIR/bin/activate"
python -m mycodo_plant_analyzer.run_analyzer --config "$CONFIG_DIR/config.json" "\$@"
EOF

chmod +x "$SHORTCUT"
echo "Script de acceso directo creado en $SHORTCUT"

# Verificar si $HOME/bin está en PATH
if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
  echo -e "${YELLOW}Nota: $HOME/bin no está en su PATH. Añádalo a su .bashrc o .profile para usar el comando mycodo-plant-analyzer directamente.${NC}"
  echo 'export PATH="$HOME/bin:$PATH"'
fi

echo -e "\n${GREEN}¡Instalación completada con éxito!${NC}"
echo -e "Para usar el sistema, ejecute: ${YELLOW}mycodo-plant-analyzer --profile NOMBRE_PERFIL${NC}"
echo -e "Ejemplo: ${YELLOW}mycodo-plant-analyzer --profile tomate${NC}"
echo -e "\nRecuerde editar el archivo de configuración en: ${YELLOW}$CONFIG_DIR/config.json${NC}"
echo -e "Los resultados del análisis se guardarán en: ${YELLOW}$OUTPUT_DIR${NC}"
