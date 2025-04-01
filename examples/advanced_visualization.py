#!/usr/bin/env python3
"""
Ejemplo de visualización avanzada con Mycodo Plant Analyzer.

Este script muestra cómo crear visualizaciones personalizadas
y paneles de control interactivos con los datos de plantas.
"""
import os
import sys
import json
import argparse
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Añadir el directorio actual al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mycodo_plant_analyzer.data_connector import MycodoConnector
from mycodo_plant_analyzer.data_analyzer import DataPreprocessor, GrowthAnalyzer

def create_custom_dashboard(sensor_data, analysis_results, output_file):
    """
    Crea un dashboard personalizado con visualizaciones avanzadas.
    
    Args:
        sensor_data: Diccionario con DataFrames de diferentes sensores
        analysis_results: Resultados del análisis
        output_file: Ruta al archivo de salida HTML
        
    Returns:
        Ruta al archivo HTML generado
    """
    # Crear HTML básico
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html lang='es'>")
    html.append("<head>")
    html.append("  <meta charset='UTF-8'>")
    html.append("  <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    html.append(f"  <title>Dashboard Visual - {analysis_results.get('plant_profile', 'Desconocido')}</title>")
    html.append("  <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css' rel='stylesheet'>")
    html.append("  <script src='https://cdn.jsdelivr.net/npm/chart.js'></script>")
    html.append("  <style>")
    html.append("    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; }")
    html.append("    .dashboard-card { background-color: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px; }")
    html.append("    .score-display { font-size: 48px; font-weight: bold; text-align: center; }")
    html.append("    .excellent { color: #28a745; }")
    html.append("    .good { color: #5cb85c; }")
    html.append("    .fair { color: #f0ad4e; }")
    html.append("    .poor { color: #d9534f; }")
    html.append("    .parameter-card { height: 100%; }")
    html.append("    .parameter-value { font-size: 24px; font-weight: bold; }")
    html.append("    .optimal { color: #28a745; }")
    html.append("    .acceptable { color: #5cb85c; }")
    html.append("    .suboptimal { color: #d9534f; }")
    html.append("    .recommendation-item { margin-bottom: 10px; padding: 10px; background-color: #f8f9fa; border-radius: 5px; }")
    html.append("  </style>")
    html.append("</head>")
    html.append("<body>")
    html.append("  <div class='container py-4'>")
    
    # Encabezado
    html.append("    <header class='pb-3 mb-4 border-bottom'>")
    html.append("      <div class='d-flex align-items-center text-dark text-decoration-none'>")
    html.append("        <span class='fs-4'>Dashboard Visual de Análisis de Plantas</span>")
    html.append("      </div>")
    html.append("    </header>")
    
    # Información general
    html.append("    <div class='row align-items-md-stretch'>")
    html.append("      <div class='col-md-6'>")
    html.append("        <div class='h-100 p-5 dashboard-card'>")
    html.append(f"          <h2>Perfil: {analysis_results.get('plant_profile', 'Desconocido').capitalize()}</h2>")
    html.append(f"          <p>Fecha de análisis: {datetime.fromisoformat(analysis_results.get('timestamp', datetime.now().isoformat())).strftime('%d/%m/%Y %H:%M')}</p>")
    
    # Evaluación general
    overall_analysis = analysis_results.get('overall_analysis', {})
    overall_score = overall_analysis.get('overall_score', 0)
    category = overall_analysis.get('category', 'fair')
    
    html.append(f"          <div class='score-display {category}'>{overall_score:.1f}</div>")
    html.append(f"          <p class='text-center'><strong>Categoría:</strong> {category.upper()}</p>")
    html.append(f"          <p class='text-center'>{overall_analysis.get('message', '')}</p>")
    html.append("        </div>")
    html.append("      </div>")
    
    # Gráfico de radar
    html.append("      <div class='col-md-6'>")
    html.append("        <div class='h-100 p-5 dashboard-card'>")
    html.append("          <h2>Análisis de Parámetros</h2>")
    html.append("          <canvas id='radarChart'></canvas>")
    html.append("        </div>")
    html.append("      </div>")
    html.append("    </div>")
    
    # Parámetros individuales
    html.append("    <div class='row mt-4'>")
    
    param_analysis = analysis_results.get('parameter_analysis', {})
    for param, analysis in param_analysis.items():
        # Determinar estado
        status = 'unknown'
        if 'range_analysis' in analysis and 'status' in analysis['range_analysis']:
            status = analysis['range_analysis']['status']
        
        # Determinar tendencia
        trend = 'unknown'
        if 'trend_analysis' in analysis and 'trend' in analysis['trend_analysis']:
            trend = analysis['trend_analysis']['trend']
        
        # Obtener valor medio
        mean_value = 0
        if 'statistics' in analysis and 'mean' in analysis['statistics']:
            mean_value = analysis['statistics']['mean']
        
        # Obtener porcentaje en rango óptimo
        pct_in_range = 0
        if 'range_analysis' in analysis and 'pct_in_range' in analysis['range_analysis']:
            pct_in_range = analysis['range_analysis']['pct_in_range']
        
        html.append("      <div class='col-md-3 mb-4'>")
        html.append("        <div class='dashboard-card parameter-card'>")
        html.append(f"          <h4>{param.capitalize()}</h4>")
        html.append(f"          <div class='parameter-value {status}'>{mean_value:.2f}</div>")
        
        # Estado
        if 'range_analysis' in analysis and 'status' in analysis['range_analysis']:
            status_map = {
                'optimal': 'ÓPTIMO',
                'acceptable': 'ACEPTABLE',
                'suboptimal': 'SUBÓPTIMO'
            }
            status_text = status_map.get(status, status.upper())
            html.append(f"          <p><strong>Estado:</strong> <span class='{status}'>{status_text}</span></p>")
            html.append(f"          <p><strong>En rango:</strong> {pct_in_range:.1f}%</p>")
        
        # Tendencia
        if 'trend_analysis' in analysis and 'message' in analysis['trend_analysis']:
            html.append(f"          <p><strong>Tendencia:</strong> {analysis['trend_analysis']['message']}</p>")
        
        # Gráfico de línea para este parámetro
        html.append(f"          <canvas id='chart_{param}'></canvas>")
        html.append("        </div>")
        html.append("      </div>")
    
    html.append("    </div>")
    
    # Recomendaciones
    recommendations = overall_analysis.get('recommendations', [])
    if recommendations:
        html.append("    <div class='row mt-4'>")
        html.append("      <div class='col-12'>")
        html.append("        <div class='dashboard-card'>")
        html.append("          <h2>Recomendaciones</h2>")
        html.append("          <div class='row'>")
        
        for i, rec in enumerate(recommendations):
            html.append("            <div class='col-md-6'>")
            html.append(f"              <div class='recommendation-item'>{i+1}. {rec}</div>")
            html.append("            </div>")
        
        html.append("          </div>")
        html.append("        </div>")
        html.append("      </div>")
        html.append("    </div>")
    
    # Scripts para gráficos
    html.append("    <script>")
    
    # Datos para gráfico de radar
    html.append("      // Gráfico de radar para parámetros")
    html.append("      const radarCtx = document.getElementById('radarChart').getContext('2d');")
    html.append("      const radarData = {")
    html.append("        labels: [")
    
    # Etiquetas de parámetros
    param_labels = []
    for param in param_analysis.keys():
        param_labels.append(f"'{param.capitalize()}'")
    html.append("          " + ", ".join(param_labels))
    
    html.append("        ],")
    html.append("        datasets: [{")
    html.append("          label: 'Porcentaje en Rango Óptimo',")
    html.append("          data: [")
    
    # Valores de parámetros
    param_values = []
    for param, analysis in param_analysis.items():
        if 'range_analysis' in analysis and 'pct_in_range' in analysis['range_analysis']:
            param_values.append(str(analysis['range_analysis']['pct_in_range']))
        else:
            param_values.append("0")
    html.append("            " + ", ".join(param_values))
    
    html.append("          ],")
    html.append("          backgroundColor: 'rgba(54, 162, 235, 0.2)',")
    html.append("          borderColor: 'rgb(54, 162, 235)',")
    html.append("          pointBackgroundColor: 'rgb(54, 162, 235)',")
    html.append("          pointBorderColor: '#fff',")
    html.append("          pointHoverBackgroundColor: '#fff',")
    html.append("          pointHoverBorderColor: 'rgb(54, 162, 235)'")
    html.append("        }]")
    html.append("      };")
    html.append("      const radarConfig = {")
    html.append("        type: 'radar',")
    html.append("        data: radarData,")
    html.append("        options: {")
    html.append("          scales: {")
    html.append("            r: {")
    html.append("              beginAtZero: true,")
    html.append("              max: 100,")
    html.append("              ticks: {")
    html.append("                stepSize: 20")
    html.append("              }")
    html.append("            }")
    html.append("          }")
    html.append("        }")
    html.append("      };")
    html.append("      new Chart(radarCtx, radarConfig);")
    
    # Gráficos de línea para cada parámetro
    for param, df in sensor_data.items():
        if df.empty:
            continue
            
        # Preparar datos para el gráfico
        dates = []
        values = []
        
        # Remuestrear a datos diarios para simplificar
        if 'timestamp' in df.columns:
            df['date'] = df['timestamp'].dt.date
            daily_avg = df.groupby('date')['value'].mean().reset_index()
            
            for _, row in daily_avg.iterrows():
                dates.append(row['date'].strftime('%d/%m'))
                values.append(str(row['value']))
        
        # Crear gráfico de línea
        html.append(f"      // Gráfico de línea para {param}")
        html.append(f"      const {param}Ctx = document.getElementById('chart_{param}').getContext('2d');")
        html.append(f"      const {param}Data = {{")
        html.append("        labels: [")
        html.append("          " + ", ".join([f"'{d}'" for d in dates]))
        html.append("        ],")
        html.append("        datasets: [{")
        html.append(f"          label: '{param.capitalize()}',")
        html.append("          data: [")
        html.append("            " + ", ".join(values))
        html.append("          ],")
        html.append("          borderColor: 'rgb(75, 192, 192)',")
        html.append("          tension: 0.1")
        html.append("        }]")
        html.append("      };")
        html.append(f"      const {param}Config = {{")
        html.append("        type: 'line',")
        html.append(f"        data: {param}Data,")
        html.append("        options: {")
        html.append("          responsive: true,")
        html.append("          plugins: {")
        html.append("            legend: {")
        html.append("              display: false")
        html.append("            }")
        html.append("          },")
        html.append("          scales: {")
        html.append("            y: {")
        html.append("              beginAtZero: false")
        html.append("            }")
        html.append("          }")
        html.append("        }")
        html.append("      };")
        html.append(f"      new Chart({param}Ctx, {param}Config);")
    
    html.append("    </script>")
    
    # Pie de página
    html.append("    <footer class='pt-3 mt-4 text-muted border-top'>")
    html.append("      <p class='text-center'>Generado por Mycodo Plant Analyzer</p>")
    html.append("    </footer>")
    
    html.append("  </div>")
    html.append("</body>")
    html.append("</html>")
    
    # Guardar archivo HTML
    with open(output_file, 'w') as f:
        f.write("\n".join(html))
    
    return output_file

def create_comparison_chart(profiles, analysis_results, output_file):
    """
    Crea un gráfico comparativo entre diferentes perfiles de plantas.
    
    Args:
        profiles: Lista de perfiles de plantas
        analysis_results: Diccionario con resultados de análisis por perfil
        output_file: Ruta al archivo de imagen de salida
        
    Returns:
        Ruta al archivo de imagen generado
    """
    # Verificar datos
    if not profiles or not analysis_results:
        print("No hay datos suficientes para crear gráfico comparativo")
        return None
    
    # Preparar datos para el gráfico
    scores = []
    categories = []
    
    for profile in profiles:
        if profile in analysis_results:
            result = analysis_results[profile]
            overall = result.get('overall_analysis', {})
            scores.append(overall.get('overall_score', 0))
            categories.append(overall.get('category', 'unknown'))
        else:
            scores.append(0)
            categories.append('unknown')
    
    # Crear figura
    plt.figure(figsize=(12, 6))
    
    # Colores según categoría
    colors = []
    for category in categories:
        if category == 'excellent':
            colors.append('#28a745')  # Verde
        elif category == 'good':
            colors.append('#5cb85c')  # Verde claro
        elif category == 'fair':
            colors.append('#f0ad4e')  # Naranja
        elif category == 'poor':
            colors.append('#d9534f')  # Rojo
        else:
            colors.append('#6c757d')  # Gris
    
    # Crear gráfico de barras
    bars = plt.bar(profiles, scores, color=colors)
    
    # Añadir etiquetas de valor
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}', ha='center', va='bottom')
    
    # Configurar etiquetas y título
    plt.xlabel('Perfiles de Plantas')
    plt.ylabel('Puntuación de Crecimiento')
    plt.title('Comparación de Perfiles de Plantas')
    
    # Añadir líneas de referencia
    plt.axhline(y=80, color='#28a745', linestyle='--', alpha=0.5, label='Excelente')
    plt.axhline(y=60, color='#5cb85c', linestyle='--', alpha=0.5, label='Bueno')
    plt.axhline(y=40, color='#f0ad4e', linestyle='--', alpha=0.5, label='Aceptable')
    
    # Añadir leyenda
    plt.legend()
    
    # Guardar imagen
    plt.tight_layout()
    plt.savefig(output_file, dpi=100)
    plt.close()
    
    return output_file

def main():
    """Función principal para demostrar visualizaciones avanzadas."""
    parser = argparse.ArgumentParser(description='Visualizaciones avanzadas para Mycodo Plant Analyzer')
    parser.add_argument('--config', type=str, default='config/config.json',
                        help='Ruta al archivo de configuración')
    parser.add_argument('--profile', type=str, required=True,
                        help='Perfil de planta a utilizar')
    parser.add_argument('--days', type=int, default=30,
                        help='Número de días de datos históricos')
    parser.add_argument('--output', type=str, default=None,
                        help='Directorio de salida para visualizaciones')
    
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
        output_dir = args.output
    else:
        output_dir = os.path.join(os.getcwd(), 'visualizations')
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Verificar si el perfil existe
    if args.profile not in config.get('plant_profiles', {}):
        print(f"Error: Perfil de planta '{args.profile}' no encontrado en la configuración")
        sys.exit(1)
    
    print(f"Generando visualizaciones avanzadas para perfil: {args.profile}")
    
    try:
        # Inicializar componentes
        connector = MycodoConnector(config=config)
        preprocessor = DataPreprocessor(config=config)
        analyzer = GrowthAnalyzer(config=config)
        
        # Obtener datos de sensores
        print("Obteniendo datos de sensores de Mycodo...")
        # Nota: En este ejemplo, generamos datos simulados en lugar de conectar con Mycodo
        sensor_data = generate_sample_data(args.profile, args.days)
        
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
        
        # Generar dashboard personalizado
        print("Generando dashboard visual personalizado...")
        dashboard_file = os.path.join(output_dir, f"visual_dashboard_{args.profile}.html")
        dashboard_path = create_custom_dashboard(sensor_data, analysis_results, dashboard_file)
        
        print(f"Dashboard visual generado: {dashboard_path}")
        print(f"Abra este archivo en su navegador para ver las visualizaciones avanzadas.")
        
        # Generar comparación si hay múltiples perfiles
        profiles = list(config.get('plant_profiles', {}).keys())
        if len(profiles) > 1:
            print("\nGenerando comparación entre perfiles...")
            
            # Simular análisis para otros perfiles
            all_results = {args.profile: analysis_results}
            for profile in profiles:
                if profile != args.profile:
                    # Generar datos simulados y análisis para comparación
                    print(f"Analizando perfil adicional: {profile}")
                    profile_data = generate_sample_data(profile, args.days)
                    for param, df in profile_data.items():
                        profile_data[param] = preprocessor.clean_data(df)
                    
                    profile_results = analyzer.analyze_growth_conditions(profile_data, profile)
                    if profile_results['status'] == 'success':
                        all_results[profile] = profile_results
            
            # Crear gráfico comparativo
            comparison_file = os.path.join(output_dir, "profile_comparison.png")
            comparison_path = create_comparison_chart(profiles, all_results, comparison_file)
            
            if comparison_path:
                print(f"Gráfico comparativo generado: {comparison_path}")
        
    except Exception as e:
        print(f"Error durante la generación de visualizaciones: {str(e)}")
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
    
    # Configuración según perfil
    if plant_profile == 'tomate':
        base_temp = 22
        temp_trend = 0.001
        base_humidity = 70
        humidity_trend = -0.0005
        base_light = 20000
        base_moisture = 70
    elif plant_profile == 'lechuga':
        base_temp = 18
        temp_trend = 0.0005
        base_humidity = 80
        humidity_trend = 0.0002
        base_light = 15000
        base_moisture = 75
    elif plant_profile == 'pimiento':
        base_temp = 24
        temp_trend = 0.002
        base_humidity = 60
        humidity_trend = -0.001
        base_light = 25000
        base_moisture = 65
    else:
        base_temp = 20
        temp_trend = 0.0008
        base_humidity = 65
        humidity_trend = -0.0003
        base_light = 18000
        base_moisture = 60
    
    # Temperatura (patrón diario con tendencia)
    temp_values = []
    for i, ts in enumerate(timestamps):
        # Patrón diario (más caliente durante el día, más frío durante la noche)
        hour = ts.hour
        daily_pattern = 3 * np.sin(hour * np.pi / 12)
        
        # Tendencia
        trend = i * temp_trend
        
        # Valor base + patrón + tendencia + ruido
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
        
        # Tendencia
        trend = i * humidity_trend
        
        # Valor base + patrón + tendencia + ruido
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
        base_level = base_moisture - 30  # Nivel base
        watering_boost = 30  # Incremento al regar
        moisture = base_level + watering_boost * drying_factor
        
        # Añadir ruido
        moisture += np.random.normal(0, 1)
        
        # Regar cuando la humedad baja de cierto umbral
        if moisture < base_moisture - 15:
            last_watering = ts
            moisture = base_level + watering_boost
        
        soil_values.append(max(0, min(100, moisture)))  # Limitar entre 0-100%
    
    sensor_data['soil_moisture'] = pd.DataFrame({
        'timestamp': timestamps,
        'value': soil_values
    })
    
    return sensor_data

if __name__ == "__main__":
    main()
