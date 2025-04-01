"""
Módulo principal para ejecutar el análisis de plantas.
"""
import os
import sys
import json
import argparse
from datetime import datetime

from mycodo_plant_analyzer.data_connector import MycodoConnector
from mycodo_plant_analyzer.data_analyzer import DataPreprocessor, GrowthAnalyzer, VisualizationGenerator

def main():
    """Función principal para ejecutar el análisis de plantas."""
    # Parsear argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Mycodo Plant Analyzer - Sistema de análisis de plantas')
    parser.add_argument('--config', type=str, default='config/config.json',
                        help='Ruta al archivo de configuración (por defecto: config/config.json)')
    parser.add_argument('--profile', type=str, required=True,
                        help='Perfil de planta a utilizar')
    parser.add_argument('--days', type=int, default=30,
                        help='Número de días de datos históricos a analizar (por defecto: 30)')
    parser.add_argument('--output', type=str, default=None,
                        help='Directorio de salida para informes y visualizaciones')
    
    args = parser.parse_args()
    
    # Verificar si existe el archivo de configuración
    if not os.path.exists(args.config):
        print(f"Error: Archivo de configuración '{args.config}' no encontrado")
        sys.exit(1)
    
    # Cargar configuración
    with open(args.config, 'r') as f:
        config = json.load(f)
    
    # Establecer directorio de salida
    if args.output:
        config['output_dir'] = args.output
    elif 'output_dir' not in config:
        config['output_dir'] = os.path.join(os.getcwd(), 'output')
    
    # Crear directorio de salida si no existe
    os.makedirs(config['output_dir'], exist_ok=True)
    
    # Verificar si el perfil existe
    if args.profile not in config.get('plant_profiles', {}):
        print(f"Error: Perfil de planta '{args.profile}' no encontrado en la configuración")
        sys.exit(1)
    
    print(f"Iniciando análisis para perfil de planta: {args.profile}")
    print(f"Analizando datos de los últimos {args.days} días")
    
    try:
        # Inicializar componentes
        connector = MycodoConnector(config=config, config_file=args.config)
        preprocessor = DataPreprocessor(config=config)
        analyzer = GrowthAnalyzer(config=config, config_file=args.config)
        visualizer = VisualizationGenerator(output_dir=config['output_dir'])
        
        # Obtener datos de sensores
        print("Obteniendo datos de sensores de Mycodo...")
        sensor_data = connector.get_sensor_data_for_profile(args.profile, days=args.days)
        
        if not sensor_data:
            print("Error: No se pudieron obtener datos de sensores")
            sys.exit(1)
        
        # Preprocesar datos
        print("Preprocesando datos...")
        for param, df in sensor_data.items():
            sensor_data[param] = preprocessor.clean_data(df)
        
        # Realizar análisis
        print("Analizando condiciones de crecimiento...")
        analysis_results = analyzer.analyze_growth_conditions(sensor_data, args.profile)
        
        if analysis_results['status'] != 'success':
            print(f"Error en el análisis: {analysis_results.get('message', 'Error desconocido')}")
            sys.exit(1)
        
        # Generar dashboard
        print("Generando dashboard...")
        dashboard_file = visualizer.generate_dashboard(
            analysis_results,
            output_file=os.path.join(config['output_dir'], f"dashboard_{args.profile}.html")
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

if __name__ == "__main__":
    main()
