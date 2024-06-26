# -*- coding: utf-8 -*-
"""Avance1.ipynb

**Cargamos los datasets**

 Cargamos información relevante de estos archivos, como los datos de resultados de carreras con los tiempos de vuelta y las posiciones de clasificación para obtener una visión más completa del desempeño de cada piloto en cada carrera.
"""

import pandas as pd

#Registra los tiempos de vuelta de cada piloto en cada carrera.
tiempos = pd.read_csv('lap_times.csv')
#Ofrece los tiempos de clasificación de cada piloto en cada carrera
clasificacion = pd.read_csv('qualifying.csv')
#Parrilla de salida y posición final de cada piloto en cada carrera (también incluye el estado de cada carrera)
resultados = pd.read_csv('results.csv')
#informacion de los pilotos
pilotos = pd.read_csv('drivers.csv')
#informacion de las carreras
races = pd.read_csv('races.csv')

"""**Union de los datasets**

Selecionaremos solo algunas columnas relevantes del dataframe races y obtendremos solo aquellos circuitos de 1982 en adelante porque anteriormente los circuitos eran drsticamente diferentes.
"""

races = races[["raceId", "year", "round", "circuitId"]].copy()
races = races[races["year"] >= 1982]

races.head()

"""Ahora seleccionamos las entidades del marco de datos original: raceId, driverId, constructorId, grid (posición inicial), positionOrder (posición final)"""

resultados = resultados[['raceId', 'driverId', 'constructorId', 'grid', 'positionOrder']].copy()
resultados.head()

"""Ahora vamos a fusionar los datos de las carreras

Nos aseguramos que no hayan duplicados en las carreras
"""

duplicates = races.duplicated()
num_duplicates = duplicates.sum()
print(f"Number of duplicate rows: {num_duplicates}")

df = pd.merge(races, resultados, on='raceId')
df.head()

"""Ahora unimos la clasificacion de las carreras"""

clasificacion.head()
df = pd.merge(df, clasificacion, on=['raceId', 'driverId','constructorId'])
df.head()

"""Seguidamente vamos a unir los tiempos"""

#eliminamos la position del dataframe
df = df.drop("position",axis = 1)
df = pd.merge(df, tiempos, on=['raceId', 'driverId'])
df.head()

"""Finalmente vamos a unir la informacion de los pilotos"""

#eliminams la columna number del dataframe
df = df.drop("number",axis = 1)
df_final = pd.merge(df, pilotos, on=['driverId'])
df_final.head()

"""Vamos a ver valores nulos en el dataframe en porcentajes"""

df_final.isna().sum()*100/len(df_final['grid'])

"""Observamos datos nulos en las columnas q1, q2 y q3 pero son un numero muy bajo en relacion al total por lo que eliminaremos estas filas."""

df_final = df_final.dropna()
df_final.isna().sum()*100/len(df_final['grid'])

"""Observamos que se han eliminado los valores nulos

Ahora describamos nuestro dataset
"""

df_final.describe().T

"""Como nuestro objetivo es poder predeir las 3 primeras posiciones de la carrera, vamos a crear una variable logica que nos indique si el piloto quedo en el top tres"""

df_final['Top3'] = df_final['positionOrder'].le(3).astype(int)
df_final.head()

"""Vamos a agregar el número de paradas en boxes para ayudar a nuestro analisis exploratorio"""

pit_stops = pd.read_csv('pit_stops.csv')
pit_stops.head()

pit_stops_final = pit_stops[["raceId","driverId","stop"]]
pit_stops_final = pit_stops_final.groupby(['raceId', 'driverId'])['stop'].sum().reset_index()
pit_stops_final.rename(columns={'stop': 'stop_boxes'}, inplace=True)
pit_stops_final.head()

"""Ahora vamos a unir las veces que paro el piloto con el dataset completo"""

df_final = pd.merge(df_final, pit_stops_final, on=['driverId','raceId'])
df_final.head()

"""Grafiquemos el numero de paradas que realizan los pilotos que han quedado en los 3 primeros puestos"""

import matplotlib.pyplot as plt
#filtramos el dataset solo para los pilotos que han quedado en el top 3

data_fil = df_final[df_final["Top3"]==1]

plt.figure(figsize=(12, 6))
plt.hist(data_fil["stop_boxes"], color='skyblue')

plt.title('Numero de paradas de los pilotos que han quedado en Top 3')
plt.xlabel('Paradas')
plt.ylabel('Frequency')
plt.show()

"""Grafiquemos ahora los tiempos de vueltas para los pilotos que han quedado en Top 3

Para esto vamos a cnvertir los tiempos a segundos
"""

import numpy as np
def tiempo_a_segundos(tiempo):
  if len(tiempo.split(':')) == 2:
    minutos, segundos = tiempo.split(':')
    segundos_totales = int(minutos) * 60 + float(segundos)
    return segundos_totales
  else:
    return np.nan
data_fil['q1'] = data_fil['q1'].apply(tiempo_a_segundos)
data_fil['q2'] = data_fil['q2'].apply(tiempo_a_segundos)
data_fil['q3'] = data_fil['q3'].apply(tiempo_a_segundos)

plt.figure(figsize=(12, 6))
plt.plot(data_fil["q1"], color='skyblue')

plt.title('primera parte de la sesión de clasificación Q1')
plt.ylabel('Q1')
plt.show()

plt.figure(figsize=(12, 6))
plt.plot(data_fil["q2"], color='skyblue')

plt.title('primera parte de la sesión de clasificación Q2')
plt.ylabel('Q2')
plt.show()

plt.figure(figsize=(12, 6))
plt.plot(data_fil["q3"], color='skyblue')

plt.title('primera parte de la sesión de clasificación Q3')
plt.ylabel('Q3')
plt.show()

"""Ahora miremos la matriz de correlacion de las variables"""

df_final.corr()
import seaborn as sns
plt.figure(figsize=(10,7))
sns.heatmap(df_final.corr(), annot=True, mask = False, annot_kws={"size": 7})
plt.show()

"""Observemos nuestra variable de Top 3 con las mejores correlaciones"""

df_final.corr()['Top3'].sort_values(ascending=False)

"""Vamos convertir los tiempos en el dataframe a segundos"""

df_final['q1'] = df_final['q1'].apply(tiempo_a_segundos)
df_final['q2'] = df_final['q2'].apply(tiempo_a_segundos)
df_final['q3'] = df_final['q3'].apply(tiempo_a_segundos)

"""Observemos nuevamente los valores nulos"""

df_final.isna().sum()*100/len(df_final['grid'])

"""Los tiempos tienen valores nulos nque podrian afectar mucho los datos, en el caso de q1 se pueden eliminar pero para q2 podriamos usar el promediode tiempo y para la variable q3 esta variable se eliminara porque casi el 50 % de los datos son nulos"""

#ponemos el promedio de q2 en los nulos
df_final["q2"] = df_final["q2"].fillna(df_final["q2"].mean())

#ahora eliminamos la columna q3
df_final = df_final.drop("q3",axis=1)

"""Contamos nuevamente los nan"""

df_final.isna().sum()*100/len(df_final['grid'])

"""Solo quedan los de la variable q2 asi que eliminaremos esas filas por ser tan insignificativo el numero de valores"""

df_final = df_final.dropna()
df_final.isna().sum()*100/len(df_final['grid'])

"""Como observamos el dataframe queda limpio nuevamente, ahora vamos a mostrar nuevamente las correlaciones"""

df_final.corr()
import seaborn as sns
plt.figure(figsize=(10,7))
sns.heatmap(df_final.corr(), annot=True, mask = False, annot_kws={"size": 7})
plt.show()

"""Vamos a observar solo la de las variables Top 3"""

df_final.corr()['Top3'].sort_values(ascending=False)

"""Observamos que estas variables agregadas no correlacionan positivamente con el top 3.

Vamos a calcular el número total de carreras y los 3 primeros resultados de cada piloto en cada año
"""

conductor = df_final.groupby(['year', 'driverId']).agg(
    Total_Races=('raceId', 'nunique'),
    Top_3_Finishes=('Top3', 'sum')
).reset_index()

conductor

"""Ahora calculamos el porcentaje de los 3 primeros puestos de cada piloto en cada año"""

conductor['Top3FinishPercentage'] = (conductor['Top_3_Finishes'] / conductor['Total_Races']) * 100

conductor

"""Vamos a agregar estas dos nuevas variables al set de datos para mirar la correlacion que aportan"""

df_final = pd.merge(df_final, conductor, on=['driverId','year'])

df_final.head()

"""Calculemos la correlacion nuevamente del top3"""

#eliminamos la variable top 3 finish por redundancia
df_final = df_final.drop('Top_3_Finishes', axis = 1)
df_final.corr()['Top3'].sort_values(ascending=False)

"""Observamos que el total de vueltas por carrera y el porcentaje de finalizacion del top 3 ayudan a la variable de prediccion. Miremoslo graficamente"""

plt.figure(figsize=(12, 6))
plt.hist(df_final["Top3FinishPercentage"], color='skyblue')

plt.title('Distribucion de Porcentaje de terminar entre los 3 primeros')
plt.ylabel('Frecuencia')
plt.xlabel('Porcentaje')
plt.show()

plt.figure(figsize=(12, 6))
plt.hist(df_final["Total_Races"], color='skyblue')

plt.title('Distribucion del numero de vueltas por año')
plt.ylabel('Frecuencia')
plt.xlabel('Porcentaje')
plt.show()

#from imblearn.over_sampling import RandomOverSampler
#oversampling = RandomOverSampler(random_state=42)
#data_X = df_final.drop('top3', axis=1)
#data_y = df_final['top3']

#X_resampled, y_resampled = oversampling.fit_resample(data_X, data_y)

#resampled_data = pd.DataFrame(X_resampled, columns=data_X.columns)
#resampled_data['top3'] = y_resampled
