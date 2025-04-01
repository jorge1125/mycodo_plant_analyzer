#!/usr/bin/env python3
"""
Ejemplo de análisis automatizado con programación.

Este script muestra cómo configurar análisis automáticos periódicos
y enviar notificaciones por correo electrónico con los resultados.
"""
import os
import sys
import json
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
import schedule
import time

# Añadir el directorio actual al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mycodo_plant_analyzer.data_connector import MycodoConnector
from mycodo_plant_analyzer.data_analyzer import DataPreprocessor, GrowthAnalyzer, VisualizationGenerator

# Configuración de correo electrónico
EMAIL_CONFIG = {
    'enabled': False,  # Cambiar a True para habilitar notificaciones por correo
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'username': 'su_correo@gmail.com',
    'password': 'su_contraseña',
    'from_email': 'su_correo@gmail.com',
    'to_email': 'destinatario@example.com'
}

def run_analysis(config_file, plant_profile, days=30, output_dir=None):
    """
    Ejecuta un análisis completo para un perfil de planta.
    
    Args:
        config_file: Ruta al archivo de configuración
        plant_profile: Nombre del perfil de planta
        days: Número de días de datos históricos
        output_dir: Directorio de salida (opcional)
        
    Returns:
        Diccionario con resultados del análisis y ruta al dashboard
    """
    # Verificar si existe el archivo de configuración
    if not os.path.exists(config_file):
        print(f"Error: Archivo de configuración '{config_file}' no encontrado")
        return None
    
    # Cargar configuración
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Establecer directorio de salida
    if output_dir:
        config['output_dir'] = output_dir
    elif 'output_dir' not in config:
        config['output_dir'] = os.path.join(os.getcwd(), 'output')
    
    os.makedirs(config['output_dir'], exist_ok=True)
    
    # Verificar si el perfil existe
    if plant_profile not in config.get('plant_profiles', {}):
        print(f"Error: Perfil de planta '{plant_profile}' no encontrado en la configuración")
        return None
    
    print(f"[{datetime.now()}] Iniciando análisis para perfil de planta: {plant_profile}")
    
    try:
        # Inicializar componentes
        connector = MycodoConnector(config=config)
        preprocessor = DataPreprocessor(config=config)
        analyzer = GrowthAnalyzer(config=config)
        visualizer = VisualizationGenerator(output_dir=config['output_dir'])
        
        # Obtener datos de sensores
        print("Obteniendo datos de sensores de Mycodo...")
        sensor_data = connector.get_sensor_data_for_profile(plant_profile, days=days)
        
        if not sensor_data:
            print("Error: No se pudieron obtener datos de sensores")
            return None
        
        # Preprocesar datos
        print("Preprocesando datos...")
        for param, df in sensor_data.items():
            sensor_data[param] = preprocessor.clean_data(df)
        
        # Realizar análisis
        print("Analizando condiciones de crecimiento...")
        analysis_results = analyzer.analyze_growth_conditions(sensor_data, plant_profile)
        
        if analysis_results['status'] != 'success':
            print(f"Error en el análisis: {analysis_results.get('message', 'Error desconocido')}")
            return None
        
        # Generar dashboard
        print("Generando dashboard...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dashboard_file = visualizer.generate_dashboard(
            analysis_results,
            output_file=os.path.join(config['output_dir'], f"dashboard_{plant_profile}_{timestamp}.html")
        )
        
        # Mostrar resultados
        overall_analysis = analysis_results.get('overall_analysis', {})
        print(f"Análisis completado con éxito!")
        print(f"Puntuación general: {overall_analysis.get('overall_score', 0):.1f}/100 ({overall_analysis.get('category', 'desconocido').upper()})")
        
        return {
            'results': analysis_results,
            'dashboard_file': dashboard_file,
            'timestamp': timestamp
        }
        
    except Exception as e:
        print(f"Error durante el análisis: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def send_email_notification(analysis_result, plant_profile):
    """
    Envía una notificación por correo electrónico con los resultados del análisis.
    
    Args:
        analysis_result: Resultados del análisis
        plant_profile: Nombre del perfil de planta
    """
    if not EMAIL_CONFIG['enabled']:
        print("Notificaciones por correo electrónico deshabilitadas")
        return
    
    if not analysis_result:
        print("No hay resultados para enviar por correo")
        return
    
    try:
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['from_email']
        msg['To'] = EMAIL_CONFIG['to_email']
        msg['Subject'] = f"Análisis de Planta: {plant_profile} - {analysis_result['timestamp']}"
        
        # Obtener datos del análisis
        results = analysis_result['results']
        overall = results.get('overall_analysis', {})
        score = overall.get('overall_score', 0)
        category = overall.get('category', 'desconocido').upper()
        message = overall.get('message', 'No disponible')
        
        # Crear cuerpo del mensaje
        body = f"""
        <html>
        <body>
            <h2>Resultados del Análisis de Planta: {plant_profile}</h2>
            <p><strong>Fecha:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <p><strong>Puntuación:</strong> {score:.1f}/100 ({category})</p>
            <p><strong>Evaluación:</strong> {message}</p>
            
            <h3>Recomendaciones:</h3>
            <ul>
        """
        
        # Añadir recomendaciones
        recommendations = overall.get('recommendations', [])
        if recommendations:
            for rec in recommendations:
                body += f"<li>{rec}</li>"
        else:
            body += "<li>No hay recomendaciones disponibles</li>"
        
        body += """
            </ul>
            <p>Se adjunta el dashboard completo para más detalles.</p>
        </body>
        </html>
        """
        
        # Adjuntar cuerpo HTML
        msg.attach(MIMEText(body, 'html'))
        
        # Adjuntar dashboard
        if os.path.exists(analysis_result['dashboard_file']):
            with open(analysis_result['dashboard_file'], 'rb') as f:
                attachment = MIMEApplication(f.read(), _subtype='html')
                attachment.add_header('Content-Disposition', 'attachment', 
                                     filename=os.path.basename(analysis_result['dashboard_file']))
                msg.attach(attachment)
        
        # Enviar correo
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
            server.send_message(msg)
        
        print(f"Notificación enviada a {EMAIL_CONFIG['to_email']}")
        
    except Exception as e:
        print(f"Error al enviar correo: {str(e)}")

def scheduled_job(config_file, plant_profile, days=30, output_dir=None):
    """Trabajo programado para ejecutar análisis y enviar notificaciones."""
    print(f"\n[{datetime.now()}] Ejecutando análisis programado para {plant_profile}")
    result = run_analysis(config_file, plant_profile, days, output_dir)
    if result:
        send_email_notification(result, plant_profile)

def main():
    """Función principal para configurar análisis programados."""
    parser = argparse.ArgumentParser(description='Análisis automatizado de plantas con Mycodo')
    parser.add_argument('--config', type=str, default='config/config.json',
                        help='Ruta al archivo de configuración')
    parser.add_argument('--profile', type=str, required=True,
                        help='Perfil de planta a utilizar')
    parser.add_argument('--days', type=int, default=30,
                        help='Número de días de datos históricos')
    parser.add_argument('--output', type=str, default=None,
                        help='Directorio de salida para informes')
    parser.add_argument('--interval', type=int, default=24,
                        help='Intervalo de análisis en horas (por defecto: 24)')
    parser.add_argument('--run-now', action='store_true',
                        help='Ejecutar análisis inmediatamente')
    
    args = parser.parse_args()
    
    # Configurar trabajo programado
    interval_hours = max(1, args.interval)  # Mínimo 1 hora
    print(f"Configurando análisis automático cada {interval_hours} horas para {args.profile}")
    
    # Programar trabajo
    schedule.every(interval_hours).hours.do(
        scheduled_job, args.config, args.profile, args.days, args.output
    )
    
    # Ejecutar inmediatamente si se solicita
    if args.run_now:
        print("Ejecutando análisis inicial...")
        scheduled_job(args.config, args.profile, args.days, args.output)
    
    # Bucle principal
    print(f"Servicio de análisis iniciado. Presione Ctrl+C para detener.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar cada minuto
    except KeyboardInterrupt:
        print("Servicio de análisis detenido.")

if __name__ == "__main__":
    main()
