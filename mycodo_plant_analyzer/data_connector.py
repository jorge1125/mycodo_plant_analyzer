"""
Módulo principal para la conexión con Mycodo.
"""
import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from influxdb import InfluxDBClient

class MycodoConnector:
    """
    Clase para conectar con Mycodo y obtener datos de sensores.
    Soporta múltiples métodos de conexión: API REST, acceso directo a InfluxDB,
    o importación de datos exportados.
    """
    
    def __init__(self, config=None, config_file=None):
        """
        Inicializa el conector con la configuración proporcionada.
        
        Args:
            config: Diccionario de configuración (opcional)
            config_file: Ruta al archivo de configuración JSON (opcional)
        """
        # Cargar configuración
        self.config = config or {}
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.config.update(json.load(f))
        
        # Configuración de Mycodo
        self.mycodo_config = self.config.get('mycodo', {})
        self.connection_method = self.mycodo_config.get('connection_method', 'api')
        
        # Inicializar conexión según el método seleccionado
        if self.connection_method == 'api':
            self._init_api_connection()
        elif self.connection_method == 'influxdb':
            self._init_influxdb_connection()
        elif self.connection_method == 'export':
            self._init_export_connection()
        elif self.connection_method == 'daemon':
            self._init_daemon_connection()
    
    def _init_api_connection(self):
        """Inicializa la conexión a la API REST de Mycodo"""
        self.api_url = f"http{'s' if self.mycodo_config.get('ssl', False) else ''}://{self.mycodo_config.get('host', 'localhost')}:{self.mycodo_config.get('port', 8080)}/api"
        self.api_key = self.mycodo_config.get('api_key', '')
        self.headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def _init_influxdb_connection(self):
        """Inicializa la conexión directa a InfluxDB"""
        influxdb_config = self.mycodo_config.get('influxdb', {})
        self.influxdb_client = InfluxDBClient(
            host=influxdb_config.get('host', 'localhost'),
            port=influxdb_config.get('port', 8086),
            username=influxdb_config.get('username', ''),
            password=influxdb_config.get('password', ''),
            database=influxdb_config.get('database', 'mycodo_db')
        )
    
    def _init_export_connection(self):
        """Inicializa la conexión a archivos exportados"""
        self.export_dir = self.mycodo_config.get('export_dir', '/var/mycodo-export')
    
    def _init_daemon_connection(self):
        """Inicializa la conexión al daemon de Mycodo"""
        try:
            # Importar DaemonControl de Mycodo
            daemon_path = self.mycodo_config.get('daemon_path', '/var/mycodo-root')
            if daemon_path not in os.sys.path:
                os.sys.path.append(daemon_path)
            from mycodo.mycodo_client import DaemonControl
            self.daemon_control = DaemonControl()
        except ImportError:
            print("Error: No se pudo importar DaemonControl. Verifique la ruta del daemon de Mycodo.")
            self.daemon_control = None
    
    def get_input_devices(self):
        """
        Obtiene la lista de dispositivos de entrada (sensores) de Mycodo.
        
        Returns:
            Lista de dispositivos de entrada
        """
        if self.connection_method == 'api':
            response = requests.get(f"{self.api_url}/inputs", headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error al obtener dispositivos de entrada: {response.status_code}")
                return []
        elif self.connection_method == 'daemon':
            if self.daemon_control:
                return self.daemon_control.input_get_all()
            return []
        else:
            print("Método de conexión no soporta esta operación")
            return []
    
    def get_measurements(self, input_id=None, days=30):
        """
        Obtiene mediciones de un sensor específico o de todos los sensores.
        
        Args:
            input_id: ID del sensor (opcional)
            days: Número de días de datos históricos a obtener
            
        Returns:
            DataFrame con las mediciones
        """
        if self.connection_method == 'api':
            return self._get_measurements_api(input_id, days)
        elif self.connection_method == 'influxdb':
            return self._get_measurements_influxdb(input_id, days)
        elif self.connection_method == 'export':
            return self._get_measurements_export(input_id, days)
        elif self.connection_method == 'daemon':
            return self._get_measurements_daemon(input_id, days)
        else:
            print("Método de conexión no reconocido")
            return pd.DataFrame()
    
    def _get_measurements_api(self, input_id, days):
        """Obtiene mediciones usando la API REST"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # Formatear fechas para la API
        start_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Construir URL
        url = f"{self.api_url}/measurements/historical"
        if input_id:
            url += f"/{input_id}"
        
        # Parámetros de consulta
        params = {
            'start': start_str,
            'end': end_str
        }
        
        # Realizar solicitud
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Convertir a DataFrame
            measurements = []
            for item in data:
                measurements.append({
                    'timestamp': datetime.fromisoformat(item['time']),
                    'value': float(item['value']),
                    'input_id': item.get('input_id', input_id),
                    'measurement': item.get('measurement', 'unknown')
                })
            
            return pd.DataFrame(measurements)
        else:
            print(f"Error al obtener mediciones: {response.status_code}")
            return pd.DataFrame()
    
    def _get_measurements_influxdb(self, input_id, days):
        """Obtiene mediciones directamente de InfluxDB"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # Formatear fechas para InfluxDB
        start_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # Construir consulta
        query = f'SELECT * FROM "measurements" WHERE time >= \'{start_str}\' AND time <= \'{end_str}\''
        if input_id:
            query += f' AND "input_id" = \'{input_id}\''
        
        # Ejecutar consulta
        result = self.influxdb_client.query(query)
        
        # Convertir a DataFrame
        if result:
            points = list(result.get_points())
            df = pd.DataFrame(points)
            
            # Convertir columna de tiempo a datetime
            if 'time' in df.columns:
                df['timestamp'] = pd.to_datetime(df['time'])
                df.drop('time', axis=1, inplace=True)
            
            return df
        else:
            return pd.DataFrame()
    
    def _get_measurements_export(self, input_id, days):
        """Obtiene mediciones de archivos exportados"""
        # Buscar archivos CSV en el directorio de exportación
        csv_files = []
        for file in os.listdir(self.export_dir):
            if file.endswith('.csv'):
                file_path = os.path.join(self.export_dir, file)
                # Verificar si el archivo es reciente (dentro del rango de días)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if (datetime.now() - file_time).days <= days:
                    csv_files.append(file_path)
        
        # Leer y combinar archivos CSV
        dfs = []
        for file in csv_files:
            try:
                df = pd.read_csv(file)
                # Verificar si el archivo contiene datos del sensor solicitado
                if input_id and 'input_id' in df.columns and not df[df['input_id'] == input_id].empty:
                    df = df[df['input_id'] == input_id]
                dfs.append(df)
            except Exception as e:
                print(f"Error al leer archivo {file}: {e}")
        
        # Combinar DataFrames
        if dfs:
            combined_df = pd.concat(dfs, ignore_index=True)
            
            # Convertir columna de tiempo a datetime
            if 'timestamp' in combined_df.columns:
                combined_df['timestamp'] = pd.to_datetime(combined_df['timestamp'])
            
            # Filtrar por fecha
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            combined_df = combined_df[(combined_df['timestamp'] >= start_time) & 
                                     (combined_df['timestamp'] <= end_time)]
            
            return combined_df
        else:
            return pd.DataFrame()
    
    def _get_measurements_daemon(self, input_id, days):
        """Obtiene mediciones usando DaemonControl"""
        if not self.daemon_control:
            return pd.DataFrame()
        
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        try:
            # Obtener mediciones a través del daemon
            measurements = self.daemon_control.influxdb_get_measurements(
                input_id, 
                start_str=start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                end_str=end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            )
            
            # Convertir a DataFrame
            data = []
            for item in measurements:
                data.append({
                    'timestamp': datetime.fromisoformat(item['time']),
                    'value': float(item['value']),
                    'input_id': item.get('input_id', input_id),
                    'measurement': item.get('measurement', 'unknown')
                })
            
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error al obtener mediciones del daemon: {e}")
            return pd.DataFrame()
    
    def get_sensor_data_for_profile(self, profile_name, days=30):
        """
        Obtiene datos de sensores para un perfil de planta específico.
        
        Args:
            profile_name: Nombre del perfil de planta
            days: Número de días de datos históricos a obtener
            
        Returns:
            Diccionario con DataFrames de diferentes parámetros
        """
        # Obtener perfiles de plantas
        plant_profiles = self.config.get('plant_profiles', {})
        
        # Verificar si existe el perfil
        if profile_name not in plant_profiles:
            print(f"Error: Perfil '{profile_name}' no encontrado")
            return {}
        
        # Obtener mapeo de sensores para el perfil
        profile = plant_profiles[profile_name]
        sensor_mapping = profile.get('sensor_mapping', {})
        
        # Obtener datos para cada parámetro
        sensor_data = {}
        for param, input_id in sensor_mapping.items():
            df = self.get_measurements(input_id, days)
            if not df.empty:
                sensor_data[param] = df
        
        return sensor_data
