import sqlite3
import pandas as pd
import folium

conn = sqlite3.connect('./a4-sampled.db')
c = conn.cursor()

strt_year = int(input("Enter start year (YYYY):"))
end_year = int(input("Enter end_year (YYYY):"))
crime_type = str(input("Enter crime type:"))
number_nbhd = int(input("Enter number of neighbourhoods:"))

sql_statement = '''SELECT neighbourhood_name, sum(incidents_count) as total_incidents  
from crime_incidents
where crime_type = '%s'
and year between %d and %d
group by neighbourhood_name
order by total_incidents desc''' % (crime_type, strt_year, end_year)


test1 = pd.read_sql_query(sql_statement, conn)
rows = test1.nlargest(number_nbhd,'total_incidents',keep='all')
new = rows.iloc[:, 0]

universe = pd.read_sql_query('''Select * from coordinates''', conn)
result = pd.merge(rows, universe, on = 'Neighbourhood_Name')
print(result)
map =folium.Map(location=[result['Latitude'].mean(),result['Longitude'].mean()], zoom_start=14)


for row in result.head().itertuples():
    folium.Circle(
        location = [row.Latitude, row.Longitude],
        popup = "{} <br> {} ".format(row.Neighbourhood_Name, row.total_incidents),
        radius = (45*(row.total_incidents//50)),
        color = 'crimson',
        fill = True,
        fill_color = 'crimson'
    ).add_to(map)
map.save(outfile='q3.html')
conn.close()