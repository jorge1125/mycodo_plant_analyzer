#!/usr/bin/env python3
"""
Módulo de inicialización para el paquete mycodo_plant_analyzer.
"""
from mycodo_plant_analyzer.data_connector import MycodoConnector
from mycodo_plant_analyzer.data_analyzer import (
    DataPreprocessor, 
    GrowthAnalyzer, 
    VisualizationGenerator
)
from mycodo_plant_analyzer.run_analyzer import main as run_analyzer

__version__ = '0.1.0'
__author__ = 'Jorge'
__email__ = 'jorge1125@example.com'
