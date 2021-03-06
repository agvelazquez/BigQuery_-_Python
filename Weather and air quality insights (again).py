import numpy  as np 
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
import os

from google.cloud import bigquery
from bq_helper    import BigQueryHelper

bq_assist = BigQueryHelper(active_project = 'bigquery-public-data', dataset_name = 'epa_historical_air_quality')
bq_assist.list_tables()

bq_assist.head('temperature_daily_summary')

query = """ SELECT EXTRACT (YEAR FROM date_local)  AS Year,
                   AVG ((arithmetic_mean - 32.0)/ 1.80)  AS avg_temp_celcius
            FROM  `bigquery-public-data.epa_historical_air_quality.temperature_daily_summary` 
            GROUP BY  Year
            Order BY  Year
"""
avg_temp = bq_assist.query_to_pandas_safe(query, max_gb_scanned = 10)

query = """ SELECT EXTRACT (YEAR FROM date_local)  AS Year,
                   AVG (arithmetic_mean) AS avg_co
            FROM  `bigquery-public-data.epa_historical_air_quality.co_daily_summary` 
            GROUP BY  Year
            Order BY  Year
"""
avg_co = bq_assist.query_to_pandas_safe(query, max_gb_scanned = 10)

concat = pd.concat([avg_temp, avg_co.avg_co], axis = 1)

fig, ax = plt.subplots(figsize=(16,5)) 

color = 'tab:blue'
ax.bar(concat.Year, concat.avg_temp_celcius, color = color)
ax.set_xticks(concat.Year)
ax.set_ylabel('T °C', color = color )
ax.tick_params(axis = 'y', labelcolor = color)

ax2 = ax.twinx()

color = 'tab:red'
ax2.plot(concat.Year, concat.avg_co, color = 'red')
ax2.set_ylabel('Avg CO', color = color)
ax2.tick_params(axis = 'y', labelcolor = color)

ax.set_title ('Temperature and Air CO')

plt.show()

# Level of pollutants (AIQ) along the years
pollutant = ["co", 'o3', 'so2', 'no2','pm25_frm' ]

query_pol = """ SELECT EXTRACT (YEAR FROM date_local) AS Year, 
            AVG(aqi) AS AQI_pollutant
            FROM `bigquery-public-data.epa_historical_air_quality.pollutant_daily_summary` 
            GROUP BY Year
            ORDER BY Year
"""
df = None
for element in pollutant:
    query = query_pol.replace('pollutant', element)
    temp = bq_assist.query_to_pandas_safe(query, max_gb_scanned = 10).set_index('Year')
    df = pd.concat([df, temp], axis = 1, join = 'outer')

#bq_assist.query_to_pandas_safe(query, max_gb_scanned = 10)

green = {'gl' : [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50, 50,50,50,50,50,50,50,50,50,50,50]}
green = pd.DataFrame(data=green)
green


color = 'tab:red'

df = df.reset_index()

fig, ax = plt.subplots(figsize=(16,5))
so2 = ax.plot(df.Year,df.AQI_so2, color = color, label = 'SO2')
co =  ax.plot(df.Year, df.AQI_co, color = color, label = 'co')
o3 =  ax.plot(df.Year, df.AQI_o3, color = color, label = 'o3')
no2 = ax.plot(df.Year, df.AQI_no2, color = color, label = 'no2')
pm25 =ax.plot(df.Year, df.AQI_pm25_frm, color = color, label = 'pm25')
lm =  ax.plot(df.Year, green.gl, color = 'tab:green', label = 'Safe Limit', marker ='.')

ax.legend()
ax.set_title('AQI Pollutants')
ax.set_ylabel('AQI level')
ax.set_xlabel('Years')

plt.show()


avg = df.drop(columns = ['Year']).mean(axis = 1, skipna = True)
avg = avg.astype(int)
avg_df = pd.concat([df.Year, avg], axis = 1)
avg_df = avg_df.rename(columns = {0 : 'AQI_avg'})
avg_df


fig, ax = plt.subplots(figsize=(16,5))
ax.plot(avg_df.Year, avg_df.AQI_avg, color = 'tab:red', label = 'Average AQI')
ax.plot(avg_df.Year, green.gl, color = 'tab:green', label = 'Safe limit', marker = '.')
ax.legend()
ax.set_xlabel('Year')
ax.set_xticks(avg_df.Year)
ax.set_ylabel('AQI')

ax.set_title('Average AQI and safe level')

plt.show()
