# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 12:59:06 2024

@author: alexr
"""
import streamlit as st 
import pandas as pd
from datetime import datetime

def calcular_promedio_tbill(ruta_csv, fecha_inicio, fecha_fin):
    """
    Calcula el promedio de la tasa del Treasury Bill desde un archivo CSV para un rango de fechas.

    :param ruta_csv: Ruta al archivo CSV con los datos. Debe tener columnas "Fecha" y "Tasa".
    :param fecha_inicio: Fecha inicial en formato 'YYYY-MM-DD'.
    :param fecha_fin: Fecha final en formato 'YYYY-MM-DD'.
    :return: Promedio de la tasa dentro del rango de fechas especificado o un mensaje de error.
    """
    try:
        # Leer el archivo CSV
        datos = pd.read_csv(ruta_csv)
        
        # Asegurarse de que la columna Fecha sea de tipo datetime
        datos['Date'] = pd.to_datetime(datos['Date'])
        
        # Convertir las fechas de entrada a objetos datetime
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
        
        # Filtrar los datos para el rango de fechas
        datos_filtrados = datos[(datos['Date'] >= fecha_inicio) & (datos['Date'] <= fecha_fin)]
        
        # Calcular el promedio de la columna "Tasa"
        promedio = datos_filtrados['Price'].mean()
        
        return promedio
    
    except Exception as e:
        return f"Error al procesar el archivo: {e}"

ruta_csv ="C:\ProyectoSeminario\datos.csv"
fecha_inicio = "2010-04-01"
fecha_fin = "2024-12-04"
promedio = calcular_promedio_tbill(ruta_csv, fecha_inicio, fecha_fin)

if isinstance(promedio, str):
    print(promedio)  # Mensaje de error o de falta de datos
else:
    print(f"El promedio del Treasury Bill desde {fecha_inicio} hasta {fecha_fin} es: {promedio:.2f}%")

st.write("Hello, *World!* :sunglasses:")