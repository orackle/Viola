import sqlite3
import pandas as pd
import folium

conn = sqlite3.connect('./a4-sampled.db')
c = conn.cursor()

m = folium.Map(location=[53.5444,-113.323], zoom_start=11)
strt_year = int(input("Enter start year (YYYY):"))
end_year = int(input("Enter end_year (YYYY):"))
number_nbhd = int(input("Enter number of neighbourhoods:"))

start_statement = '''select neighbourhood_name, (canadian_citizen+ non_canadian_citizen+ no_response) as population_count 
from population 
where population_count!=0
group by neighbourhood_name;'''
population = pd.read_sql_query(start_statement,conn)

sql_statement = '''SELECT neighbourhood_name, sum(incidents_count) as total_incidents  
from crime_incidents
where year between %d and %d
group by neighbourhood_name
order by total_incidents''' % (strt_year, end_year)

crimes = pd.read_sql_query(sql_statement, conn)

crimes = pd.merge(crimes, population, on = 'Neighbourhood_Name')
crimes['ratio'] = crimes['total_incidents']/crimes['population_count']
crimes = crimes.sort_values(['ratio'], ascending=[False])
# print(crimes.to_string(index = False))

listone = ['Neighbourhood_Name', 'ratio']
result= crimes[[col for col in listone if col in crimes.columns]]
result = result.iloc[:number_nbhd, :]


parent = '''SELECT neighbourhood_name,crime_type, sum(incidents_count) as total_incidents  from crime_incidents
where year between %d and %d
group by neighbourhood_name, crime_type
order by neighbourhood_name asc, total_incidents desc''' % (strt_year, end_year)

dummy = pd.read_sql_query(parent, conn)
dummy = dummy.groupby("Neighbourhood_Name").head(1)
list = ['Neighbourhood_Name', 'Crime_Type', 'ratio']
dummy = pd.merge(result, dummy, on="Neighbourhood_Name")
semi_final=dummy[[col for col in list if col in dummy.columns]]

coordinate_query = '''select * from coordinates'''
coord = pd.read_sql_query(coordinate_query, conn)
coord = pd.merge(semi_final, coord, on='Neighbourhood_Name')
list = ['Neighbourhood_Name', 'Crime_Type', 'ratio', 'Latitude', 'Longitude']
final=coord[[col for col in list if col in coord.columns]]
print(final)
for row in final.head().itertuples():
    folium.Circle(
        location = [row.Latitude, row.Longitude],
        popup = "{} <br> {} <br> {}".format(row.Neighbourhood_Name, row.Crime_Type, row.ratio),
        radius = (1500*(row.ratio)),
        color = 'crimson',
        fill = True,
        fill_color = 'crimson'
    ).add_to(m)
m.save('q4.html')
conn.close()