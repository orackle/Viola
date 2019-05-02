import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import folium
def q2():
    conn = sqlite3.connect("tiebreaking.db")
    c = conn.cursor()
    n_value = int(input("Enter number of locations:"))
    m = folium.Map(location=[53.5444,-113.323], zoom_start=11)
    sql_n_locations = '''
        SELECT p.Neighbourhood_Name, c.Latitude, c.Longitude, (CANADIAN_CITIZEN+NON_CANADIAN_CITIZEN+NO_RESPONSE) as Total
        FROM population p, coordinates c
        WHERE p.Neighbourhood_name = c.Neighbourhood_name and total > 0 and c.Latitude != 0 and c.Longitude != 0
        ORDER BY Total
    '''
    unfiltered_data = pd.read_sql_query(sql_n_locations,conn)
    top_n = unfiltered_data.nlargest(n_value,'Total',keep='all')
    bot_n = unfiltered_data.nsmallest(n_value,'Total',keep='all')
    print(top_n)
    print(bot_n)
    for i in range(n_value):
        folium.Circle(
            location=[bot_n.iloc[i]['Latitude'], bot_n.iloc[i]['Longitude']],
            popup=bot_n.iloc[i]['Neighbourhood_Name'] + '\n' + str(bot_n.iloc[i]['Total']),
            radius = int(bot_n.iloc[i]['Total']) * 1.1,
            color = 'green',
            fill = True,
            fill_color='blue',
        ).add_to(m)
    for i in range(n_value):
        folium.Circle(
            location=[top_n.iloc[i]['Latitude'], top_n.iloc[i]['Longitude']],
            popup=top_n.iloc[i]['Neighbourhood_Name'] + '\n' + str(top_n.iloc[i]['Total']),
            radius = int(top_n.iloc[i]['Total']) * 0.1,
            color = 'crimson',
            fill = True,
            fill_color='red',
        ).add_to(m)
    m.save('q2.html')
    

    conn.close()
q2()