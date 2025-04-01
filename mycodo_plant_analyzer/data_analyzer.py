"""
Módulo para el preprocesamiento y análisis de datos de sensores.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats, signal
from datetime import datetime, timedelta
import os
import json

class DataPreprocessor:
    """
    Clase para limpiar y preprocesar datos de sensores.
    """
    
    def __init__(self, config=None):
        """
        Inicializa el preprocesador con configuración opcional.
        
        Args:
            config: Diccionario de configuración (opcional)
        """
        self.config = config or {}
    
    def clean_data(self, df):
        """
        Limpia y preprocesa un DataFrame de datos de sensores.
        
        Args:
            df: DataFrame con datos de sensores
            
        Returns:
            DataFrame limpio y preprocesado
        """
        if df.empty:
            return df
        
        # Hacer una copia para evitar modificar el original
        df_clean = df.copy()
        
        # Asegurar que la columna timestamp sea datetime
        if 'timestamp' in df_clean.columns:
            df_clean['timestamp'] = pd.to_datetime(df_clean['timestamp'])
        
        # Ordenar por timestamp
        if 'timestamp' in df_clean.columns:
            df_clean = df_clean.sort_values('timestamp')
        
        # Eliminar duplicados
        df_clean = df_clean.drop_duplicates()
        
        # Manejar valores faltantes
        if 'value' in df_clean.columns:
            # Interpolar valores faltantes si no son demasiados
            missing_pct = df_clean['value'].isna().mean() * 100
            if missing_pct < 20:  # Si menos del 20% son valores faltantes
                df_clean['value'] = df_clean['value'].interpolate(method='linear')
            
            # Eliminar filas restantes con valores faltantes
            df_clean = df_clean.dropna(subset=['value'])
        
        # Detectar y eliminar valores atípicos extremos
        if 'value' in df_clean.columns and len(df_clean) > 10:
            # Calcular límites usando IQR
            Q1 = df_clean['value'].quantile(0.25)
            Q3 = df_clean['value'].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 3 * IQR  # Más permisivo que el estándar 1.5*IQR
            upper_bound = Q3 + 3 * IQR
            
            # Filtrar valores extremos
            df_clean = df_clean[(df_clean['value'] >= lower_bound) & 
                               (df_clean['value'] <= upper_bound)]
        
        return df_clean
    
    def resample_data(self, df, freq='1H'):
        """
        Remuestrea datos a una frecuencia específica.
        
        Args:
            df: DataFrame con datos de sensores
            freq: Frecuencia de remuestreo (por defecto: 1 hora)
            
        Returns:
            DataFrame remuestreado
        """
        if df.empty or 'timestamp' not in df.columns or 'value' not in df.columns:
            return df
        
        # Establecer timestamp como índice
        df_resampled = df.copy()
        df_resampled = df_resampled.set_index('timestamp')
        
        # Remuestrear datos
        resampled = df_resampled['value'].resample(freq).mean()
        
        # Convertir de nuevo a DataFrame
        result = pd.DataFrame({'timestamp': resampled.index, 'value': resampled.values})
        
        # Restaurar otras columnas si existen
        for col in df.columns:
            if col not in ['timestamp', 'value']:
                # Para columnas categóricas, usar el valor más frecuente
                if df[col].dtype == 'object':
                    mode_values = df_resampled[col].resample(freq).apply(
                        lambda x: x.mode()[0] if not x.empty and len(x.mode()) > 0 else None
                    )
                    result[col] = [mode_values.loc[t] for t in resampled.index]
                else:
                    # Para columnas numéricas, usar la media
                    mean_values = df_resampled[col].resample(freq).mean()
                    result[col] = [mean_values.loc[t] for t in resampled.index]
        
        return result
    
    def normalize_data(self, df, method='minmax'):
        """
        Normaliza los valores en un DataFrame.
        
        Args:
            df: DataFrame con datos de sensores
            method: Método de normalización ('minmax' o 'zscore')
            
        Returns:
            DataFrame con valores normalizados
        """
        if df.empty or 'value' not in df.columns:
            return df
        
        df_norm = df.copy()
        
        if method == 'minmax':
            # Normalización Min-Max (escala a rango 0-1)
            min_val = df_norm['value'].min()
            max_val = df_norm['value'].max()
            
            if max_val > min_val:
                df_norm['value_normalized'] = (df_norm['value'] - min_val) / (max_val - min_val)
            else:
                df_norm['value_normalized'] = 0.5  # Valor constante
        
        elif method == 'zscore':
            # Normalización Z-score (media 0, desviación estándar 1)
            mean = df_norm['value'].mean()
            std = df_norm['value'].std()
            
            if std > 0:
                df_norm['value_normalized'] = (df_norm['value'] - mean) / std
            else:
                df_norm['value_normalized'] = 0  # Valor constante
        
        return df_norm


class GrowthAnalyzer:
    """
    Clase para analizar el crecimiento de plantas basado en datos de sensores.
    """
    
    def __init__(self, config=None, config_file=None):
        """
        Inicializa el analizador con configuración.
        
        Args:
            config: Diccionario de configuración (opcional)
            config_file: Ruta al archivo de configuración JSON (opcional)
        """
        # Cargar configuración
        self.config = config or {}
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.config.update(json.load(f))
        
        # Cargar perfiles de plantas
        self.plant_profiles = self.config.get('plant_profiles', {})
        
        # Directorio para visualizaciones
        self.output_dir = self.config.get('output_dir', '/tmp')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def analyze_growth_conditions(self, sensor_data, plant_profile):
        """
        Analiza las condiciones de crecimiento basado en datos de sensores.
        
        Args:
            sensor_data: Diccionario con DataFrames de diferentes sensores
            plant_profile: Nombre del perfil de planta a utilizar
            
        Returns:
            Diccionario con resultados de análisis
        """
        if plant_profile not in self.plant_profiles:
            return {
                'status': 'error',
                'message': f"Perfil de planta '{plant_profile}' no encontrado"
            }
        
        # Verificar si tenemos datos suficientes
        if not sensor_data:
            return {
                'status': 'error',
                'message': 'No se pudieron obtener datos de sensores'
            }
        
        # Obtener perfil de planta
        profile = self.plant_profiles[plant_profile]
        
        # Resultados de análisis
        analysis = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'plant_profile': plant_profile,
            'parameter_analysis': {},
            'overall_analysis': {},
            'visualizations': {}
        }
        
        # Analizar cada parámetro
        for param, df in sensor_data.items():
            if df.empty:
                continue
                
            # Análisis de parámetros
            param_analysis = self._analyze_parameter(df, param, profile)
            analysis['parameter_analysis'][param] = param_analysis
            
            # Visualización de parámetros
            viz_path = self._visualize_parameter(df, param, param_analysis, profile)
            if viz_path:
                analysis['visualizations'][f"{param}_analysis"] = viz_path
        
        # Análisis general
        analysis['overall_analysis'] = self._generate_overall_analysis(analysis['parameter_analysis'])
        
        # Visualización general
        viz_path = self._visualize_overall_analysis(analysis)
        if viz_path:
            analysis['visualizations']['overall_analysis'] = viz_path
        
        return analysis
    
    def _analyze_parameter(self, df, param, profile):
        """
        Analiza un parámetro específico.
        
        Args:
            df: DataFrame con datos del sensor
            param: Nombre del parámetro
            profile: Perfil de planta
            
        Returns:
            Diccionario con análisis del parámetro
        """
        # Obtener rango óptimo si está disponible
        optimal_range = None
        if 'optimal_ranges' in profile and param in profile['optimal_ranges']:
            optimal_range = (
                profile['optimal_ranges'][param].get('min'),
                profile['optimal_ranges'][param].get('max')
            )
        
        # Estadísticas básicas
        stats_analysis = {
            'mean': df['value'].mean(),
            'median': df['value'].median(),
            'min': df['value'].min(),
            'max': df['value'].max(),
            'std': df['value'].std(),
            'variance': df['value'].var()
        }
        
        # Análisis de rango óptimo
        range_analysis = {}
        if optimal_range:
            min_val, max_val = optimal_range
            in_range = df[(df['value'] >= min_val) & (df['value'] <= max_val)]
            pct_in_range = len(in_range) / len(df) * 100 if len(df) > 0 else 0
            
            below_range = df[df['value'] < min_val]
            above_range = df[df['value'] > max_val]
            
            pct_below = len(below_range) / len(df) * 100 if len(df) > 0 else 0
            pct_above = len(above_range) / len(df) * 100 if len(df) > 0 else 0
            
            range_analysis = {
                'optimal_min': min_val,
                'optimal_max': max_val,
                'pct_in_range': pct_in_range,
                'pct_below_range': pct_below,
                'pct_above_range': pct_above
            }
            
            # Determinar estado
            if pct_in_range >= 80:
                range_analysis['status'] = 'optimal'
            elif pct_in_range >= 60:
                range_analysis['status'] = 'acceptable'
            else:
                range_analysis['status'] = 'suboptimal'
        
        # Análisis de tendencia
        trend_analysis = self._analyze_trend(df)
        
        # Compilar resultados
        return {
            'statistics': stats_analysis,
            'range_analysis': range_analysis,
            'trend_analysis': trend_analysis
        }
    
    def _analyze_trend(self, df):
        """
        Analiza la tendencia de un parámetro.
        
        Args:
            df: DataFrame con datos del sensor
            
        Returns:
            Diccionario con análisis de tendencia
        """
        if df.empty or len(df) < 5:
            return {'trend': 'unknown', 'message': 'Datos insuficientes para análisis de tendencia'}
        
        # Asegurar que los datos están ordenados
        df = df.sort_values('timestamp')
        
        # Calcular medias diarias
        if 'timestamp' in df.columns:
            df['date'] = df['timestamp'].dt.date
            daily_avg = df.groupby('date')['value'].mean().reset_index()
        else:
            return {'trend': 'unknown', 'message': 'Formato de datos incorrecto para análisis de tendencia'}
        
        # Si tenemos suficientes días, calcular tendencia
        if len(daily_avg) >= 3:
            # Calcular pendiente de la línea de tendencia
            x = np.arange(len(daily_avg))
            y = daily_avg['value'].values
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            # Determinar tendencia
            if abs(slope) < 0.01:  # Umbral para considerar estable
                trend = 'stable'
                message = 'Se mantiene estable en el tiempo'
            elif slope > 0:
                trend = 'increasing'
                message = f'Muestra tendencia creciente ({slope:.3f} por día)'
            else:
                trend = 'decreasing'
                message = f'Muestra tendencia decreciente ({slope:.3f} por día)'
            
            # Calcular velocidad de cambio
            if len(daily_avg) > 1:
                first_value = daily_avg['value'].iloc[0]
                last_value = daily_avg['value'].iloc[-1]
                days_diff = (daily_avg['date'].iloc[-1] - daily_avg['date'].iloc[0]).days
                
                if days_diff > 0:
                    change_rate = (last_value - first_value) / days_diff
                else:
                    change_rate = 0
            else:
                change_rate = 0
            
            return {
                'trend': trend,
                'message': message,
                'slope': slope,
                'r_value': r_value,
                'p_value': p_value,
                'change_rate': change_rate
            }
        else:
            return {
                'trend': 'unknown',
                'message': 'Datos insuficientes para análisis de tendencia (se necesitan al menos 3 días)'
            }
    
    def _generate_overall_analysis(self, parameter_analysis):
        """
        Genera un análisis general basado en los análisis de parámetros individuales.
        
        Args:
            parameter_analysis: Diccionario con análisis de parámetros
            
        Returns:
            Diccionario con análisis general
        """
        # Calcular puntuación general
        scores = []
        
        # Puntuación de parámetros
        param_scores = []
        for param, analysis in parameter_analysis.items():
            if 'range_analysis' in analysis and 'status' in analysis['range_analysis']:
                status = analysis['range_analysis']['status']
                if status == 'optimal':
                    param_scores.append(1.0)
                elif status == 'acceptable':
                    param_scores.append(0.7)
                elif status == 'suboptimal':
                    param_scores.append(0.3)
                else:
                    param_scores.append(0.0)
        
        if param_scores:
            avg_param_score = sum(param_scores) / len(param_scores)
            scores.append(avg_param_score)
        
        # Calcular puntuación general
        if scores:
            overall_score = sum(scores) / len(scores) * 100
        else:
            overall_score = 0
        
        # Determinar categoría
        if overall_score >= 80:
            category = 'excellent'
            message = 'Condiciones excelentes para el crecimiento'
        elif overall_score >= 60:
            category = 'good'
            message = 'Buenas condiciones para el crecimiento'
        elif overall_score >= 40:
            category = 'fair'
            message = 'Condiciones aceptables, algunas mejoras recomendadas'
        else:
            category = 'poor'
            message = 'Condiciones deficientes, se requieren mejoras significativas'
        
        # Generar recomendaciones
        recommendations = self._generate_recommendations(parameter_analysis)
        
        return {
            'overall_score': overall_score,
            'category': category,
            'message': message,
            'recommendations': recommendations
        }
    
    def _generate_recommendations(self, parameter_analysis):
        """
        Genera recomendaciones basadas en el análisis de parámetros.
        
        Args:
            parameter_analysis: Diccionario con análisis de parámetros
            
        Returns:
            Lista de recomendaciones
        """
        recommendations = []
        
        for param, analysis in parameter_analysis.items():
            if 'range_analysis' in analysis and 'status' in analysis['range_analysis']:
                status = analysis['range_analysis']['status']
                
                if status != 'optimal':
                    range_data = analysis['range_analysis']
                    
                    if 'pct_below_range' in range_data and range_data['pct_below_range'] > 20:
                        if param == 'temperature':
                            recommendations.append(f"Aumentar la temperatura. Actualmente está por debajo del rango óptimo ({range_data['optimal_min']}°C) durante un {range_data['pct_below_range']:.1f}% del tiempo.")
                        elif param == 'humidity':
                            recommendations.append(f"Aumentar la humedad. Actualmente está por debajo del rango óptimo ({range_data['optimal_min']}%) durante un {range_data['pct_below_range']:.1f}% del tiempo.")
                        elif param == 'light':
                            recommendations.append(f"Aumentar la exposición a la luz. Actualmente está por debajo del rango óptimo ({range_data['optimal_min']} lux) durante un {range_data['pct_below_range']:.1f}% del tiempo.")
                        elif param == 'soil_moisture':
                            recommendations.append(f"Aumentar el riego. La humedad del suelo está por debajo del rango óptimo ({range_data['optimal_min']}%) durante un {range_data['pct_below_range']:.1f}% del tiempo.")
                        else:
                            recommendations.append(f"Aumentar {param}. Actualmente está por debajo del rango óptimo ({range_data['optimal_min']}) durante un {range_data['pct_below_range']:.1f}% del tiempo.")
                    
                    if 'pct_above_range' in range_data and range_data['pct_above_range'] > 20:
                        if param == 'temperature':
                            recommendations.append(f"Reducir la temperatura. Actualmente está por encima del rango óptimo ({range_data['optimal_max']}°C) durante un {range_data['pct_above_range']:.1f}% del tiempo.")
                        elif param == 'humidity':
                            recommendations.append(f"Reducir la humedad. Actualmente está por encima del rango óptimo ({range_data['optimal_max']}%) durante un {range_data['pct_above_range']:.1f}% del tiempo.")
                        elif param == 'light':
                            recommendations.append(f"Reducir la exposición a la luz. Actualmente está por encima del rango óptimo ({range_data['optimal_max']} lux) durante un {range_data['pct_above_range']:.1f}% del tiempo.")
                        elif param == 'soil_moisture':
                            recommendations.append(f"Reducir el riego. La humedad del suelo está por encima del rango óptimo ({range_data['optimal_max']}%) durante un {range_data['pct_above_range']:.1f}% del tiempo.")
                        else:
                            recommendations.append(f"Reducir {param}. Actualmente está por encima del rango óptimo ({range_data['optimal_max']}) durante un {range_data['pct_above_range']:.1f}% del tiempo.")
        
        return recommendations
    
    def _visualize_parameter(self, df, param, param_analysis, profile):
        """
        Genera visualización para un parámetro.
        
        Args:
            df: DataFrame con datos del sensor
            param: Nombre del parámetro
            param_analysis: Análisis del parámetro
            profile: Perfil de planta
            
        Returns:
            Ruta al archivo de imagen guardado
        """
        if df.empty:
            return None
            
        # Crear figura
        plt.figure(figsize=(12, 6))
        
        # Gráfico principal de datos
        plt.plot(df['timestamp'], df['value'], 'b-', linewidth=1.5)
        
        # Añadir rango óptimo si está disponible
        if 'range_analysis' in param_analysis and 'optimal_min' in param_analysis['range_analysis']:
            min_val = param_analysis['range_analysis']['optimal_min']
            max_val = param_analysis['range_analysis']['optimal_max']
            
            plt.axhspan(min_val, max_val, alpha=0.2, color='green', label='Rango óptimo')
            plt.axhline(y=min_val, color='g', linestyle='--', alpha=0.7)
            plt.axhline(y=max_val, color='g', linestyle='--', alpha=0.7)
        
        # Añadir tendencia si está disponible
        if 'trend_analysis' in param_analysis and 'slope' in param_analysis['trend_analysis']:
            # Calcular línea de tendencia
            x = np.arange(len(df))
            slope = param_analysis['trend_analysis']['slope']
            intercept = df['value'].iloc[0]
            trend_line = intercept + slope * x
            
            # Convertir índices a timestamps para graficar
            trend_timestamps = df['timestamp'].iloc[0] + pd.to_timedelta(x * np.mean(np.diff(df.index)), unit='s')
            
            plt.plot(trend_timestamps, trend_line, 'r--', linewidth=1.5, label='Tendencia')
        
        # Configurar etiquetas y título
        unit = ''
        if 'optimal_ranges' in profile and param in profile['optimal_ranges']:
            unit = profile['optimal_ranges'][param].get('unit', '')
        
        plt.xlabel('Fecha/Hora')
        plt.ylabel(f'{param.capitalize()} ({unit})' if unit else param.capitalize())
        
        # Determinar título basado en estado
        title = f'Análisis de {param.capitalize()}'
        if 'range_analysis' in param_analysis and 'status' in param_analysis['range_analysis']:
            status = param_analysis['range_analysis']['status']
            if status == 'optimal':
                title += ' - ÓPTIMO'
            elif status == 'acceptable':
                title += ' - ACEPTABLE'
            elif status == 'suboptimal':
                title += ' - SUBÓPTIMO'
        
        plt.title(title)
        
        # Añadir leyenda
        plt.legend()
        
        # Añadir cuadrícula
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Formatear eje x para mejor visualización de fechas
        plt.gcf().autofmt_xdate()
        
        # Añadir estadísticas como texto
        if 'statistics' in param_analysis:
            stats = param_analysis['statistics']
            stats_text = f"Media: {stats['mean']:.2f} {unit}\n"
            stats_text += f"Mín: {stats['min']:.2f} {unit}\n"
            stats_text += f"Máx: {stats['max']:.2f} {unit}"
            
            plt.figtext(0.02, 0.02, stats_text, fontsize=9,
                      bbox=dict(facecolor='white', alpha=0.8))
        
        # Añadir información de rango óptimo
        if 'range_analysis' in param_analysis and 'pct_in_range' in param_analysis['range_analysis']:
            range_data = param_analysis['range_analysis']
            range_text = f"Tiempo en rango óptimo: {range_data['pct_in_range']:.1f}%\n"
            range_text += f"Por debajo: {range_data['pct_below_range']:.1f}%\n"
            range_text += f"Por encima: {range_data['pct_above_range']:.1f}%"
            
            plt.figtext(0.98, 0.02, range_text, fontsize=9,
                      bbox=dict(facecolor='white', alpha=0.8),
                      horizontalalignment='right')
        
        # Guardar imagen
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{param.lower().replace(' ', '_')}_analysis_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=100)
        plt.close()
        
        return filepath
    
    def _visualize_overall_analysis(self, analysis):
        """
        Genera visualización para el análisis general.
        
        Args:
            analysis: Diccionario con resultados de análisis
            
        Returns:
            Ruta al archivo de imagen guardado
        """
        # Crear figura con 2x2 subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Gráfico de puntuación general (gauge)
        overall_analysis = analysis.get('overall_analysis', {})
        overall_score = overall_analysis.get('overall_score', 0)
        category = overall_analysis.get('category', 'unknown')
        
        gauge_colors = {
            'poor': 'red',
            'fair': 'orange',
            'good': 'lightgreen',
            'excellent': 'green',
            'unknown': 'gray'
        }
        
        gauge_color = gauge_colors.get(category, 'gray')
        ax1.pie([overall_score, 100-overall_score], colors=[gauge_color, 'lightgray'], 
               startangle=90, counterclock=False,
               wedgeprops={'width': 0.3, 'edgecolor': 'w'})
        
        ax1.text(0, 0, f"{overall_score:.1f}", ha='center', va='center', fontsize=36)
        ax1.text(0, -0.2, f"{category.upper()}", ha='center', va='center', fontsize=14)
        
        # Añadir título
        ax1.set_title('Puntuación de Crecimiento')
        ax1.axis('equal')
        
        # 2. Gráfico de parámetros
        param_analysis = analysis.get('parameter_analysis', {})
        params = []
        values = []
        colors = []
        
        for param, param_data in param_analysis.items():
            if 'range_analysis' in param_data and 'pct_in_range' in param_data['range_analysis']:
                params.append(param.capitalize())
                
                # Calcular porcentaje en rango óptimo
                pct = param_data['range_analysis']['pct_in_range']
                values.append(pct)
                
                # Determinar color basado en estado
                status = param_data['range_analysis'].get('status', 'unknown')
                if status == 'optimal':
                    colors.append('green')
                elif status == 'acceptable':
                    colors.append('lightgreen')
                elif status == 'suboptimal':
                    colors.append('red')
                else:
                    colors.append('gray')
        
        # Crear gráfico de barras horizontales
        if params:
            bars = ax2.barh(params, values, color=colors)
            
            # Añadir etiquetas de porcentaje
            for bar in bars:
                width = bar.get_width()
                ax2.text(width + 1, bar.get_y() + bar.get_height()/2, 
                        f'{width:.1f}%', ha='left', va='center')
            
            # Configurar etiquetas y título
            ax2.set_xlabel('% en Rango Óptimo')
            ax2.set_title('Parámetros de Crecimiento')
            
            # Establecer límites del eje x
            ax2.set_xlim(0, 105)
        else:
            ax2.text(0.5, 0.5, 'No hay datos de parámetros disponibles', 
                    ha='center', va='center', fontsize=12)
            ax2.axis('off')
        
        # 3. Gráfico de tendencias
        trends = {'increasing': [], 'decreasing': [], 'stable': [], 'unknown': []}
        
        for param, param_data in param_analysis.items():
            if 'trend_analysis' in param_data and 'trend' in param_data['trend_analysis']:
                trend = param_data['trend_analysis']['trend']
                trends[trend].append(param.capitalize())
        
        # Preparar datos para gráfico
        trend_labels = []
        trend_counts = []
        trend_colors = []
        
        for trend, params in trends.items():
            if params:  # Solo incluir tendencias con parámetros
                if trend == 'increasing':
                    label = 'Creciente'
                    color = 'green'
                elif trend == 'decreasing':
                    label = 'Decreciente'
                    color = 'red'
                elif trend == 'stable':
                    label = 'Estable'
                    color = 'blue'
                else:
                    label = 'Desconocida'
                    color = 'gray'
                
                trend_labels.append(label)
                trend_counts.append(len(params))
                trend_colors.append(color)
        
        # Crear gráfico de pastel
        if trend_counts:
            ax3.pie(trend_counts, labels=trend_labels, colors=trend_colors, 
                   autopct='%1.1f%%', startangle=90)
            ax3.axis('equal')
            ax3.set_title('Tendencias de Parámetros')
        else:
            ax3.text(0.5, 0.5, 'No hay datos de tendencias disponibles', 
                    ha='center', va='center', fontsize=12)
            ax3.axis('off')
        
        # 4. Gráfico de recomendaciones
        recommendations = overall_analysis.get('recommendations', [])
        
        if recommendations:
            # Limitar a 5 recomendaciones para el gráfico
            if len(recommendations) > 5:
                display_recommendations = recommendations[:4] + ['Otras recomendaciones...']
            else:
                display_recommendations = recommendations
            
            # Crear texto para mostrar
            rec_text = '\n\n'.join([f"{i+1}. {rec}" for i, rec in enumerate(display_recommendations)])
            
            ax4.text(0.5, 0.5, rec_text, 
                    ha='center', va='center', fontsize=11,
                    bbox=dict(facecolor='white', alpha=0.8),
                    wrap=True)
            ax4.axis('off')
            ax4.set_title('Recomendaciones')
        else:
            ax4.text(0.5, 0.5, 'No hay recomendaciones disponibles', 
                    ha='center', va='center', fontsize=12)
            ax4.axis('off')
            ax4.set_title('Recomendaciones')
        
        # Añadir título general
        plt.suptitle('Análisis General de Crecimiento', fontsize=16)
        
        # Guardar imagen
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"overall_analysis_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        plt.tight_layout(rect=[0, 0, 1, 0.97])  # Ajustar para título general
        plt.savefig(filepath, dpi=100)
        plt.close()
        
        return filepath


class VisualizationGenerator:
    """
    Clase para generar visualizaciones avanzadas de datos de plantas.
    """
    
    def __init__(self, output_dir=None):
        """
        Inicializa el generador de visualizaciones.
        
        Args:
            output_dir: Directorio para guardar visualizaciones
        """
        self.output_dir = output_dir or '/tmp'
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_dashboard(self, analysis_results, output_file=None):
        """
        Genera un dashboard HTML interactivo con los resultados del análisis.
        
        Args:
            analysis_results: Resultados del análisis
            output_file: Ruta al archivo de salida (opcional)
            
        Returns:
            Ruta al archivo HTML generado
        """
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(
                self.output_dir,
                f"dashboard_{timestamp}.html"
            )
        
        # Crear HTML básico
        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html lang='es'>")
        html.append("<head>")
        html.append("  <meta charset='UTF-8'>")
        html.append("  <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
        html.append(f"  <title>Dashboard de Análisis - {analysis_results.get('plant_profile', 'Desconocido')}</title>")
        html.append("  <style>")
        html.append("    body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }")
        html.append("    h1, h2, h3 { color: #2c3e50; }")
        html.append("    .container { max-width: 1200px; margin: 0 auto; }")
        html.append("    .header { background-color: #3498db; color: white; padding: 20px; border-radius: 5px; }")
        html.append("    .section { margin: 20px 0; padding: 15px; background-color: #f9f9f9; border-radius: 5px; }")
        html.append("    .score { font-size: 48px; font-weight: bold; text-align: center; }")
        html.append("    .excellent { color: #27ae60; }")
        html.append("    .good { color: #2ecc71; }")
        html.append("    .fair { color: #f39c12; }")
        html.append("    .poor { color: #e74c3c; }")
        html.append("    .chart { max-width: 100%; height: auto; display: block; margin: 20px auto; }")
        html.append("    .parameter-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }")
        html.append("    .parameter-card { background-color: #fff; border-radius: 5px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }")
        html.append("    .parameter-value { font-size: 24px; font-weight: bold; margin: 10px 0; }")
        html.append("    .optimal { color: #27ae60; }")
        html.append("    .acceptable { color: #2ecc71; }")
        html.append("    .suboptimal { color: #e74c3c; }")
        html.append("    .trend-up { color: #27ae60; }")
        html.append("    .trend-down { color: #e74c3c; }")
        html.append("    .trend-stable { color: #3498db; }")
        html.append("    .recommendations { background-color: #fff; border-radius: 5px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }")
        html.append("    .recommendations ul { padding-left: 20px; }")
        html.append("    .recommendations li { margin-bottom: 10px; }")
        html.append("  </style>")
        html.append("</head>")
        html.append("<body>")
        html.append("  <div class='container'>")
        
        # Encabezado
        html.append("    <div class='header'>")
        html.append(f"      <h1>Dashboard de Análisis: {analysis_results.get('plant_profile', 'Desconocido')}</h1>")
        html.append(f"      <p>Fecha: {datetime.fromisoformat(analysis_results.get('timestamp', datetime.now().isoformat())).strftime('%d/%m/%Y %H:%M')}</p>")
        html.append("    </div>")
        
        # Evaluación general
        overall_analysis = analysis_results.get('overall_analysis', {})
        overall_score = overall_analysis.get('overall_score', 0)
        category = overall_analysis.get('category', 'fair')
        
        html.append("    <div class='section'>")
        html.append("      <h2>Evaluación General</h2>")
        html.append(f"      <div class='score {category}'>{overall_score:.1f}</div>")
        html.append(f"      <p style='text-align: center;'><strong>Categoría:</strong> {category.upper()}</p>")
        html.append(f"      <p style='text-align: center;'>{overall_analysis.get('message', '')}</p>")
        
        # Incluir imagen de análisis general si está disponible
        if 'visualizations' in analysis_results and 'overall_analysis' in analysis_results['visualizations']:
            viz_path = analysis_results['visualizations']['overall_analysis']
            html.append(f"      <img src='{os.path.basename(viz_path)}' alt='Análisis general' class='chart'>")
        
        html.append("    </div>")
        
        # Parámetros
        html.append("    <div class='section'>")
        html.append("      <h2>Análisis de Parámetros</h2>")
        html.append("      <div class='parameter-grid'>")
        
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
            
            # Determinar clase CSS para tendencia
            trend_class = ''
            if trend == 'increasing':
                trend_class = 'trend-up'
            elif trend == 'decreasing':
                trend_class = 'trend-down'
            elif trend == 'stable':
                trend_class = 'trend-stable'
            
            # Obtener valor medio
            mean_value = 0
            if 'statistics' in analysis and 'mean' in analysis['statistics']:
                mean_value = analysis['statistics']['mean']
            
            html.append(f"        <div class='parameter-card'>")
            html.append(f"          <h3>{param.capitalize()}</h3>")
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
                
                if 'pct_in_range' in analysis['range_analysis']:
                    html.append(f"          <p><strong>Tiempo en rango óptimo:</strong> {analysis['range_analysis']['pct_in_range']:.1f}%</p>")
            
            # Tendencia
            if 'trend_analysis' in analysis and 'message' in analysis['trend_analysis']:
                html.append(f"          <p><strong>Tendencia:</strong> <span class='{trend_class}'>{analysis['trend_analysis']['message']}</span></p>")
            
            # Enlace a gráfico detallado
            if 'visualizations' in analysis_results and f"{param}_analysis" in analysis_results['visualizations']:
                viz_path = analysis_results['visualizations'][f"{param}_analysis"]
                html.append(f"          <p><a href='{os.path.basename(viz_path)}' target='_blank'>Ver análisis detallado</a></p>")
            
            html.append("        </div>")
        
        html.append("      </div>")
        html.append("    </div>")
        
        # Recomendaciones
        recommendations = overall_analysis.get('recommendations', [])
        if recommendations:
            html.append("    <div class='section'>")
            html.append("      <h2>Recomendaciones</h2>")
            html.append("      <div class='recommendations'>")
            html.append("        <ul>")
            
            for rec in recommendations:
                html.append(f"          <li>{rec}</li>")
            
            html.append("        </ul>")
            html.append("      </div>")
            html.append("    </div>")
        
        # Pie de página
        html.append("    <div style='text-align: center; margin-top: 30px; color: #7f8c8d;'>")
        html.append("      <p>Generado por Mycodo Plant Analyzer</p>")
        html.append("    </div>")
        
        html.append("  </div>")
        html.append("</body>")
        html.append("</html>")
        
        # Guardar archivo HTML
        with open(output_file, 'w') as f:
            f.write("\n".join(html))
        
        # Copiar imágenes al mismo directorio
        visualizations = analysis_results.get('visualizations', {})
        for viz_path in visualizations.values():
            if viz_path and os.path.exists(viz_path):
                dest_path = os.path.join(os.path.dirname(output_file), os.path.basename(viz_path))
                if viz_path != dest_path:
                    import shutil
                    shutil.copy(viz_path, dest_path)
        
        return output_file
