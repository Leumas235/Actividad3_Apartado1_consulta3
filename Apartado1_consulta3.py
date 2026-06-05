# Configuración inicial necesaria
import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

# Se guardan los valores del código del municipio y la fecha a utilizar
id_municipio = "2724"
precio_dia = "12-02-2026"

# Se definen funciones para hacer las llamadas a las peticiones API con una URL pasada por parámetro. En resumen las funciones hacen:
# - Llama a una API mediante una URL pasada por parámetro
# - Realiza un timeout de 10'' por si la llamada tarda demasiado
# - Devuelve los datos en formato JSON
# - Devuelve un error controlado

# Datos para realizar la llamada a la API de obtener precio por día y municipio. Devuelve una lista diccionario con todos los datos.
def obtener_precio_dia_municipio(id_municipio, precio_dia):
    url = f"https://energia.serviciosmin.gob.es/ServiciosRestCarburantes/PreciosCarburantes/EstacionesTerrestresHist/FiltroMunicipio/{precio_dia}/{id_municipio}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        datos = response.json()

        # Guardar JSON para depuración
        # with open("datos_consulta_streamlit.json", "w", encoding="utf-8") as archivo:
        #     json.dump(datos, archivo, indent=4, ensure_ascii=False)

        return {
            "Fecha": datos.get("Fecha", precio_dia),
            "Estaciones": datos.get("ListaEESSPrecio", [])
        }

    except Exception as e:
        st.error(f"Error al conectar con la API: {e}")
        return {"Fecha": precio_dia, "Estaciones": []}


# Datos para realizar la llamada a la API de consulta de Municipios. Devuelve el nombre dela municipio del código introducido por parámetro.
def obtener_municipio(id_muni):
    url = "https://energia.serviciosmin.gob.es/ServiciosRestCarburantes/PreciosCarburantes/Listados/Municipios/"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        datos = response.json()

        for i in datos:
            if i.get("IDMunicipio") == id_muni:
                return i.get("Municipio", "Municipio no disponible")

        return "ID Municipio no encontrado"

    except Exception as e:
        st.error(f"Error al obtener municipios: {e}")
        return "Error"


# Se configura la pagina web completa con el nombre de la pestaña y la funcionalidad del menú About
st.set_page_config(
    layout="wide", 
    page_title="Precio por día y municipio",
    menu_items={
        "About": "Aplicación para consultar los productos de estaciones de Cúllar del día 12/02/2026. Actividad 3, apartado 1, consulta 3 de Tecnologías Emergentes"
    }
)

# Título página web
st.title("Precios de estaciones de servicio por Municipio y Día")

# Obtener nombre del municipio
municipio = obtener_municipio(id_municipio)

# Pintar texto y valor
st.subheader(f"Municipio: {municipio} — Fecha: {precio_dia}")

# Obtener datos de las estaciones por municipio y día
datos = obtener_precio_dia_municipio(id_municipio, precio_dia)
estaciones = datos["Estaciones"]

# Si no se encuentran valores para ese municipio y día
if not estaciones:
    st.warning("No hay datos disponibles para la fecha y municipio seleccionados.")
    st.stop()

# Identificar productos disponibles para pintar sólo productos disponibles y que sea más visible
productos = set()
for est in estaciones:
    for i, valor in est.items():
        if i.startswith("Precio ") and valor.strip() != "":
            productos.add(i)

# Ordenar los productos disponibles
productos = sorted(list(productos))

# Construir DataFrame
filas = []
for est in estaciones:
    fila = {
        "Rótulo": est.get("Rótulo", "").strip(),
        "Dirección": est.get("Dirección", "").strip(),
    }

    for comb in productos:
        # Formato europeo, substituir punto por coma decimal
        precio = est.get(comb, "").replace(",", ".")
        fila[comb.replace("Precio ", "")] = float(precio) if precio.replace(".", "").isdigit() else None

    filas.append(fila)

df = pd.DataFrame(filas)

# Mostrar tabla
st.dataframe(df, use_container_width=True)
