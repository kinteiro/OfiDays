import pandas as pd
from datetime import datetime, timedelta
import os

DIAS_SEMANA = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']

def obtener_lunes_de_semana(fecha=None):
    """Obtiene el lunes de la semana actual o de una fecha específica"""
    if fecha is None:
        fecha = datetime.now()
    dias_desde_lunes = fecha.weekday()
    lunes = fecha - timedelta(days=dias_desde_lunes)
    return lunes.replace(hour=0, minute=0, second=0, microsecond=0)

def obtener_fecha_semana(lunes, dia_nombre):
    """Obtiene la fecha específica de un día de la semana"""
    indice = DIAS_SEMANA.index(dia_nombre)
    return lunes + timedelta(days=indice)

def formatear_semana(lunes):
    """Formatea la semana para mostrar (ej: '10/02/2026 - 14/02/2026')"""
    viernes = lunes + timedelta(days=4)
    return f"{lunes.strftime('%d/%m/%Y')} - {viernes.strftime('%d/%m/%Y')}"

def cargar_votos():
    """Carga los votos desde el CSV"""
    try:
        if os.path.exists('votos.csv'):
            df = pd.read_csv('votos.csv')
            if df.empty:
                return pd.DataFrame(columns=['semana_inicio', 'usuario', 'dia', 'tipo_semana'])
            return df
        else:
            return pd.DataFrame(columns=['semana_inicio', 'usuario', 'dia', 'tipo_semana'])
    except Exception as e:
        print(f"Error al cargar votos: {e}")
        return pd.DataFrame(columns=['semana_inicio', 'usuario', 'dia', 'tipo_semana'])

def guardar_votos(df_votos):
    """Guarda los votos en el CSV"""
    try:
        df_votos.to_csv('votos.csv', index=False)
        return True
    except Exception as e:
        print(f"Error al guardar votos: {e}")
        return False

def obtener_votos_semana(lunes, tipo_semana='current'):
    """Obtiene los votos de una semana específica"""
    df_votos = cargar_votos()
    fecha_str = lunes.strftime('%Y-%m-%d')

    votos_semana = df_votos[
        (df_votos['semana_inicio'] == fecha_str) &
        (df_votos['tipo_semana'] == tipo_semana)
    ]

    resultado = {dia: [] for dia in DIAS_SEMANA}

    for _, row in votos_semana.iterrows():
        if row['dia'] in resultado:
            resultado[row['dia']].append(row['usuario'])

    return resultado

def agregar_voto(lunes, usuario, dia, tipo_semana='current'):
    """Agrega un voto para un usuario en un día específico"""
    df_votos = cargar_votos()
    fecha_str = lunes.strftime('%Y-%m-%d')

    nuevo_voto = pd.DataFrame([{
        'semana_inicio': fecha_str,
        'usuario': usuario,
        'dia': dia,
        'tipo_semana': tipo_semana
    }])

    df_votos = pd.concat([df_votos, nuevo_voto], ignore_index=True)
    return guardar_votos(df_votos)

def eliminar_voto(lunes, usuario, dia, tipo_semana='current'):
    """Elimina un voto de un usuario en un día específico"""
    df_votos = cargar_votos()
    fecha_str = lunes.strftime('%Y-%m-%d')

    df_votos = df_votos[~(
        (df_votos['semana_inicio'] == fecha_str) &
        (df_votos['usuario'] == usuario) &
        (df_votos['dia'] == dia) &
        (df_votos['tipo_semana'] == tipo_semana)
    )]

    return guardar_votos(df_votos)

def reiniciar_semana():
    """
    Reinicia la semana:
    - La semana 'next' pasa a ser 'current'
    - Se elimina la antigua 'current'
    """
    df_votos = cargar_votos()

    lunes_actual = obtener_lunes_de_semana()
    lunes_siguiente = lunes_actual + timedelta(days=7)

    fecha_actual_str = lunes_actual.strftime('%Y-%m-%d')
    fecha_siguiente_str = lunes_siguiente.strftime('%Y-%m-%d')

    # Eliminar la semana current antigua (la semana pasada)
    lunes_pasado = lunes_actual - timedelta(days=7)
    fecha_pasado_str = lunes_pasado.strftime('%Y-%m-%d')

    df_votos = df_votos[~(
        (df_votos['semana_inicio'] == fecha_pasado_str) &
        (df_votos['tipo_semana'] == 'current')
    )]

    # La semana 'next' de la semana actual pasa a ser 'current' de esta semana
    df_votos.loc[
        (df_votos['semana_inicio'] == fecha_actual_str) &
        (df_votos['tipo_semana'] == 'next'),
        'tipo_semana'
    ] = 'current'

    return guardar_votos(df_votos)

def verificar_y_reiniciar_si_necesario():
    """Verifica si es lunes y reinicia la semana si es necesario"""
    # Marcar en un archivo temporal si ya se reinició esta semana
    lunes_actual = obtener_lunes_de_semana()
    archivo_marca = '.ultimo_reinicio'

    if os.path.exists(archivo_marca):
        with open(archivo_marca, 'r') as f:
            ultima_fecha = f.read().strip()
            if ultima_fecha == lunes_actual.strftime('%Y-%m-%d'):
                return False  # Ya se reinició esta semana

    # Reiniciar y guardar la marca
    reiniciar_semana()

    with open(archivo_marca, 'w') as f:
        f.write(lunes_actual.strftime('%Y-%m-%d'))

    return True
