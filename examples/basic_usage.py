#!/usr/bin/env python3
"""
Ejemplo de uso básico de Mycodo Plant Analyzer.

Este script muestra cómo utilizar los componentes principales del sistema
para analizar datos de plantas desde Python.
"""
import os
import sys
import json
from datetime import datetime

# Añadir el directorio actual al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mycodo_plant_analyzer.data_connector import MycodoConnector
from mycodo_plant_analyzer.data_analyzer import DataPreprocessor, GrowthAnalyzer, VisualizationGenerator

def main():
    """Función principal para demostrar el uso básico del sistema."""
    # Configuración
    config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              'config', 'config.example.json')
    
    # Verificar si existe el archivo de configuración
    if not os.path.exists(config_file):
        print(f"Error: Archivo de configuración '{config_file}' no encontrado")
        sys.exit(1)
    
    # Cargar configuración
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Establecer directorio de salida
    output_dir = os.path.join(os.getcwd(), 'output')
    os.makedirs(output_dir, exist_ok=True)
    config['output_dir'] = output_dir
    
    # Perfil de planta a analizar
    plant_profile = 'tomate'
    days = 30
    
    # Verificar si el perfil existe
    if plant_profile not in config.get('plant_profiles', {}):
        print(f"Error: Perfil de planta '{plant_profile}' no encontrado en la configuración")
        sys.exit(1)
    
    print(f"Iniciando análisis para perfil de planta: {plant_profile}")
    print(f"Analizando datos de los últimos {days} días")
    
    try:
        # Inicializar componentes
        connector = MycodoConnector(config=config)
        preprocessor = DataPreprocessor(config=config)
        analyzer = GrowthAnalyzer(config=config)
        visualizer = VisualizationGenerator(output_dir=output_dir)
        
        # Obtener datos de sensores
        print("Obteniendo datos de sensores de Mycodo...")
        # Nota: En este ejemplo, generamos datos simulados en lugar de conectar con Mycodo
        sensor_data = generate_sample_data(plant_profile, days)
        
        if not sensor_data:
            print("Error: No se pudieron obtener datos de sensores")
            sys.exit(1)
        
        # Preprocesar datos
        print("Preprocesando datos...")
        for param, df in sensor_data.items():
            sensor_data[param] = preprocessor.clean_data(df)
        
        # Realizar análisis
        print("Analizando condiciones de crecimiento...")
        analysis_results = analyzer.analyze_growth_conditions(sensor_data, plant_profile)
        
        if analysis_results['status'] != 'success':
            print(f"Error en el análisis: {analysis_results.get('message', 'Error desconocido')}")
            sys.exit(1)
        
        # Generar dashboard
        print("Generando dashboard...")
        dashboard_file = visualizer.generate_dashboard(
            analysis_results,
            output_file=os.path.join(output_dir, f"dashboard_{plant_profile}.html")
        )
        
        # Mostrar resultados
        overall_analysis = analysis_results.get('overall_analysis', {})
        print("\nAnálisis completado con éxito!")
        print(f"Puntuación general: {overall_analysis.get('overall_score', 0):.1f}/100 ({overall_analysis.get('category', 'desconocido').upper()})")
        print(f"Evaluación: {overall_analysis.get('message', 'No disponible')}")
        
        # Mostrar recomendaciones
        recommendations = overall_analysis.get('recommendations', [])
        if recommendations:
            print("\nRecomendaciones:")
            for i, rec in enumerate(recommendations):
                print(f"{i+1}. {rec}")
        
        print(f"\nDashboard generado: {dashboard_file}")
        print(f"Abra este archivo en su navegador para ver el análisis completo.")
        
    except Exception as e:
        print(f"Error durante el análisis: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def generate_sample_data(plant_profile, days=30):
    """
    Genera datos de muestra para demostración.
    
    Args:
        plant_profile: Nombre del perfil de planta
        days: Número de días de datos históricos
        
    Returns:
        Diccionario con DataFrames de diferentes sensores
    """
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    # Fecha de inicio (hace X días)
    start_date = datetime.now() - timedelta(days=days)
    
    # Generar timestamps
    timestamps = [start_date + timedelta(hours=i) for i in range(days * 24)]
    
    # Generar datos para diferentes parámetros
    sensor_data = {}
    
    # Temperatura (patrón diario con tendencia creciente)
    temp_values = []
    for i, ts in enumerate(timestamps):
        # Patrón diario (más caliente durante el día, más frío durante la noche)
        hour = ts.hour
        daily_pattern = 3 * np.sin(hour * np.pi / 12)
        
        # Tendencia creciente leve
        trend = i * 0.001
        
        # Valor base + patrón + tendencia + ruido
        base_temp = 22
        noise = np.random.normal(0, 0.5)
        value = base_temp + daily_pattern + trend + noise
        
        temp_values.append(value)
    
    sensor_data['temperature'] = pd.DataFrame({
        'timestamp': timestamps,
        'value': temp_values
    })
    
    # Humedad (patrón inverso a temperatura)
    humidity_values = []
    for i, ts in enumerate(timestamps):
        hour = ts.hour
        daily_pattern = -5 * np.sin(hour * np.pi / 12)  # Inverso a temperatura
        
        # Tendencia decreciente leve
        trend = -i * 0.0005
        
        # Valor base + patrón + tendencia + ruido
        base_humidity = 70
        noise = np.random.normal(0, 1)  # Más variabilidad
        value = base_humidity + daily_pattern + trend + noise
        
        humidity_values.append(value)
    
    sensor_data['humidity'] = pd.DataFrame({
        'timestamp': timestamps,
        'value': humidity_values
    })
    
    # Luz (solo durante el día)
    light_values = []
    for ts in timestamps:
        hour = ts.hour
        
        # Luz solo durante el día (6am - 8pm)
        if 6 <= hour <= 20:
            # Patrón de campana centrado al mediodía
            hour_normalized = (hour - 6) / 14  # 0 a 1 durante las horas de luz
            light_pattern = np.sin(hour_normalized * np.pi)
            
            base_light = 20000
            value = base_light * light_pattern + np.random.normal(0, 1000)
        else:
            value = np.random.normal(0, 100)  # Casi cero durante la noche
        
        light_values.append(max(0, value))  # No permitir valores negativos
    
    sensor_data['light'] = pd.DataFrame({
        'timestamp': timestamps,
        'value': light_values
    })
    
    # Humedad del suelo (patrón de riego)
    soil_values = []
    last_watering = start_date - timedelta(hours=12)  # Último riego antes del inicio
    
    for ts in timestamps:
        # Calcular tiempo desde el último riego
        hours_since_watering = (ts - last_watering).total_seconds() / 3600
        
        # Patrón de secado (exponencial decreciente)
        drying_factor = np.exp(-hours_since_watering / 48)  # Secado en ~2 días
        
        # Valor base + patrón + ruido
        base_moisture = 40  # Nivel base
        watering_boost = 35  # Incremento al regar
        moisture = base_moisture + watering_boost * drying_factor
        
        # Añadir ruido
        moisture += np.random.normal(0, 1)
        
        # Regar cuando la humedad baja de cierto umbral
        if moisture < 50:
            last_watering = ts
            moisture = base_moisture + watering_boost
        
        soil_values.append(max(0, min(100, moisture)))  # Limitar entre 0-100%
    
    sensor_data['soil_moisture'] = pd.DataFrame({
        'timestamp': timestamps,
        'value': soil_values
    })
    
    return sensor_data

if __name__ == "__main__":
    main()
